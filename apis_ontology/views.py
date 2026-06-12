from django_cosmograph.views import CosmographView
from .models import GraphSearchSnapshot
from django.core.cache import cache
import json
import math
import logging
from django_cosmograph.utils import assign_node_sizes

logger = logging.getLogger(__name__)

class GraphView(CosmographView):
    # TODO: How do I restrict the view based on user permissions

    def _get_selected_collection_ids(self):
        values = []
        for value in self.request.GET.getlist("collection"):
            if not value:
                continue
            values.extend(part.strip() for part in value.split(","))

        selected_ids = set()
        for value in values:
            if value.isdigit():
                selected_ids.add(int(value))
        return selected_ids

    def _apply_collection_filter(self, nodes, links):
        selected_collection_ids = self._get_selected_collection_ids()
        if not selected_collection_ids:
            return nodes, links

        filtered_nodes = [
            node
            for node in nodes
            if selected_collection_ids.intersection(node.get("collection_ids", []))
        ]
        filtered_node_ids = {node.get("id") for node in filtered_nodes}

        filtered_links = [
            link
            for link in links
            if link.get("source") in filtered_node_ids
            and link.get("target") in filtered_node_ids
        ]

        return filtered_nodes, filtered_links

    def _collection_choices(self, nodes):
        choices = {}
        for node in nodes:
            for collection in node.get("collections", []):
                collection_id = collection.get("id")
                if collection_id is None:
                    continue
                choices[collection_id] = collection.get("label", str(collection_id))

        return [
            {"id": collection_id, "label": label}
            for collection_id, label in sorted(
                choices.items(), key=lambda item: item[1].lower()
            )
        ]

    def _serialize_nodes_for_cosmograph(self, nodes):
        serialized_nodes = []
        for node in nodes:
            clean_node = dict(node)
            clean_node.pop("collection_ids", None)
            clean_node.pop("collections", None)
            serialized_nodes.append(clean_node)
        return serialized_nodes

    def _get_snapshot_nodes_links(self):
        cache_key = GraphSearchSnapshot.CACHE_KEY
        cached_data = cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        snapshot = GraphSearchSnapshot.objects.filter(
            key=GraphSearchSnapshot.DEFAULT_KEY
        ).first()
        if snapshot is None:
            logger.debug("Graph snapshot missing - rebuilding from source models")
            snapshot = GraphSearchSnapshot.rebuild()

        nodes = snapshot.nodes
        links = snapshot.links
        cache.set(cache_key, json.dumps((nodes, links)), 86400)
        return nodes, links

    def _show_unconnected_nodes(self):
        value = self.request.GET.get("show_unconnected", "1").strip().lower()
        return value not in {"0", "false", "no", "off"}

    def _apply_unconnected_visibility(self, nodes, links):
        if not links or self._show_unconnected_nodes():
            return nodes, links

        linked_node_ids = {
            endpoint
            for link in links
            for endpoint in (link.get("source"), link.get("target"))
            if endpoint is not None
        }
        return [node for node in nodes if node.get("id") in linked_node_ids], links

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        snapshot_nodes, _ = self._get_snapshot_nodes_links()
        context["graph_query"] = self.request.GET.get("q", "").strip()
        context["graph_show_unconnected"] = self._show_unconnected_nodes()
        context["graph_collection_choices"] = self._collection_choices(snapshot_nodes)
        context["graph_selected_collection_ids"] = self._get_selected_collection_ids()
        return context

    def get_params(self, *args, **kwargs):
        params = super().get_params(*args, **kwargs)
        params["renderLinks"] = getattr(self, "_graph_has_links", True)
        return params

    def _filter_nodes_links(self, nodes, links):
        query = self.request.GET.get("q", "").strip().lower()
        if not query:
            return nodes, links

        def matches_query(value):
            if isinstance(value, dict):
                return any(matches_query(v) for v in value.values())
            if isinstance(value, (list, tuple, set)):
                return any(matches_query(v) for v in value)
            return query in str(value).lower()

        matching_nodes = [
            node
            for node in nodes
            if matches_query(node)
        ]

        matching_node_ids = {node.get("id") for node in matching_nodes}

        matching_links = [link for link in links if matches_query(link)]

        links_of_matching_nodes = [
            link
            for link in links
            if link.get("source") in matching_node_ids
            or link.get("target") in matching_node_ids
        ]

        if not matching_node_ids and not matching_links:
            return [], []

        # Include all links that match directly and all links connected to matching nodes.
        filtered_links = []
        seen_links = set()
        for link in matching_links + links_of_matching_nodes:
            key = json.dumps(link, sort_keys=True, default=str)
            if key in seen_links:
                continue
            seen_links.add(key)
            filtered_links.append(link)

        visible_node_ids = set()
        for link in filtered_links:
            visible_node_ids.add(link.get("source"))
            visible_node_ids.add(link.get("target"))

        # Keep all matched nodes, even if they have no incident links.
        filtered_nodes = list(matching_nodes)
        for node in nodes:
            if node.get("id") in visible_node_ids and node not in filtered_nodes:
                filtered_nodes.append(node)

        return filtered_nodes, filtered_links

    def get_nodes_links(self):
        nodes, links = self._get_snapshot_nodes_links()
        logger.debug(f"Generated graph with {len(nodes)} nodes and {len(links)} links")

        nodes, links = self._apply_collection_filter(nodes, links)
        nodes, links = self._filter_nodes_links(nodes, links)
        nodes = self._serialize_nodes_for_cosmograph(nodes)
        logger.debug(
            f"After filtering, graph has {len(nodes)} nodes and {len(links or [])} links"
        )
        
        nodes, links = self._apply_unconnected_visibility(nodes, links)
        self._graph_has_links = bool(links)
        if not links and nodes:
            node_id = nodes[0]["id"]
            links = [
                {
                    "source": node_id,
                    "target": node_id,
                    "label": "",
                    "reverse_label": "",
                    "group": "__collection_placeholder__",
                }
            ]
        return nodes, links
