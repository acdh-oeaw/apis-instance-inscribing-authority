from apis_acdhch_default_settings.settings import *

ROOT_URLCONF = "apis_ontology.urls"
ADDITIONAL_APPS = [
    "django_interval",
    "apis_core.documentation",
]
for app in ADDITIONAL_APPS:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)
