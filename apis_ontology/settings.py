from apis_acdhch_default_settings.settings import *

DEBUG = True

ROOT_URLCONF = "apis_ontology.urls"
ADDITIONAL_APPS = [
    "django_interval",
    "apis_core.documentation",
    "apis_bibsonomy",
]
for app in ADDITIONAL_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)


APIS_BIBSONOMY = [
    {
        "type": "zotero",
        "url": "https://api.zotero.org",
        "user": os.environ.get("APIS_BIBSONOMY_USER"),
        "API key": os.environ.get("APIS_BIBSONOMY_PASSWORD"),
        "group": "6307386",
    }
]
