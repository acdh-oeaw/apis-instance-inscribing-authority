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
        data = json.loads(ref.bibtex)
        author = data["author"][0]
        year = data["issued"]["date-parts"][0][0]
        title = data["title"]
        formatted_refs.append(
            f"{author['family']}, {author['given']} ({year}). {title}"
        )

    return formatted_refs


# ref['author'][0]['family']}, {ref['author'][0]['given']} ({ref['issued']['date-parts'][0][0]}).
