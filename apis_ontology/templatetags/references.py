
import logging
from django import template
from apis_bibsonomy.models import Reference
import json

register = template.Library()


@register.filter
def get_references(content_type, object_id):
    refs_qs = Reference.objects.filter(content_type=content_type, object_id=object_id)
    formatted_refs = []

    for ref in refs_qs:
        # Assuming ref.bibtex is stored as JSON string
        try:
            data = json.loads(ref.bibtex)
            parts = []
            author = data.get("author", [{}])
            if author and isinstance(author, list) and author[0]:
                a = author[0]
                name = []
                if 'family' in a:
                    name.append(a['family'])
                if 'given' in a:
                    name.append(a['given'])
                if name:
                    parts.append(", ".join(name))
            year = None
            issued = data.get("issued", {})
            if isinstance(issued, dict):
                date_parts = issued.get("date-parts", [])
                if date_parts and isinstance(date_parts, list) and date_parts[0]:
                    year = date_parts[0][0] if len(date_parts[0]) > 0 else None
            if year:
                parts.append(f"({year})")
            title = data.get("title")
            if title:
                parts.append(title)
            if parts:
                formatted_refs.append(". ".join(parts))
            else:
                logging.warning(f"Could not construct custom reference for Reference id={ref.id}, using default string.")
                formatted_refs.append(str(ref))
        except (json.JSONDecodeError, IndexError, AttributeError, TypeError) as e:
            logging.warning(f"Error parsing Reference id={ref.id}: {e}. Using default string representation.")
            formatted_refs.append(str(ref))

    return formatted_refs
