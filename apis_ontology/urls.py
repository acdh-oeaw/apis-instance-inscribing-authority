from django.urls import include, path

from apis_acdhch_default_settings.urls import urlpatterns

urlpatterns += [path("", include("django_interval.urls"))]
urlpatterns += (
    path("apis_bibsonomy/", include("apis_bibsonomy.urls", namespace="bibsonomy")),
)
