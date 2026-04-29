# templatetags/custom_filters.py
from django import template
from django.template.defaultfilters import urlize
from django.utils.safestring import mark_safe
from html.parser import HTMLParser

register = template.Library()

class URLizingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.in_tag = False

    def handle_starttag(self, tag, attrs):
        self.result.append(self.get_starttag_text())
        self.in_tag = True

    def handle_endtag(self, tag):
        self.result.append(f'</{tag}>')
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
    result = ''.join(parser.result)
    # Now modify links to open in new tab
    result = result.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ')
    return mark_safe(result)