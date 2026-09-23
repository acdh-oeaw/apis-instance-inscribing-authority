# templatetags/custom_filters.py
import re
from html.parser import HTMLParser

from django import template
from django.template.defaultfilters import urlize
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apis_core.apis_entities.models import RootObject

register = template.Library()
ID_PATTERN = re.compile(r"\bID:\s*(\d+)\b")


class URLizingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.in_tag = False

    def handle_starttag(self, tag, attrs):
        self.result.append(self.get_starttag_text())
        self.in_tag = True

    def handle_endtag(self, tag):
        self.result.append(f"</{tag}>")
        self.in_tag = False

    def handle_data(self, data):
        if not self.in_tag:
            # Urlize only the data (text content)
            self.result.append(urlize(data))
        else:
            self.result.append(data)


@register.filter
def urlize_newtab(value):
    if not value:
        return value
    parser = URLizingParser()
    parser.feed(str(value))
    result = "".join(parser.result)
    result = result.replace("<a ", '<a target="_blank" rel="noopener noreferrer" ')
    return mark_safe(result)


@register.filter
def link_ids(value):
    if not value:
        return value

    def replace(match):
        id_ = match.group(1)
        entity = RootObject.objects_inheritance.get_subclass(pk=id_)
        url = entity.get_absolute_url() if entity else "#"
        return format_html(
            '<a href="{}">{}</a>',
            url,
            match.group(0),
        )

    return mark_safe(ID_PATTERN.sub(replace, str(value)))
