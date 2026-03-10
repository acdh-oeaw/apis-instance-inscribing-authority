from django.db import models
import django_filters
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from apis_core.relations.filtersets import RelationFilterSet


class IContainsFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
        }


class IABaseModelFilterSet(IContainsFilterSet):
    pass


class VocabularyBaseModelFilterSet(IContainsFilterSet):
    pass


class IARelationMixinFilterSet(RelationFilterSet):
    class Meta(RelationFilterSet.Meta):
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            },
        }
