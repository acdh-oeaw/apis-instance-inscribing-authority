from django.urls import include, path

from apis_acdhch_default_settings.urls import urlpatterns

from apis_ontology.views import GraphView

urlpatterns += [    path(
        "graph/",
        GraphView.as_view(),
        name="graph_view",
    ),
]
urlpatterns += [
    path("highlighter/", include("apis_highlighter.urls", namespace="highlighter")),
]

urlpatterns += [path("", include("django_interval.urls"))]
urlpatterns += (
    path("apis_bibsonomy/", include("apis_bibsonomy.urls", namespace="bibsonomy")),
)
urlpatterns += (path("datamodel/", include("apis_datamodel.urls")),)
