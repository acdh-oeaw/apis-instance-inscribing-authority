from django.urls import include, path

from apis_acdhch_default_settings.urls import urlpatterns

urlpatterns += [path("", include("django_interval.urls"))]
