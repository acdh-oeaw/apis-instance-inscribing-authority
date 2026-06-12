import logging
import math
from django.core.cache import cache
from django.db import models
from apis_core.apis_entities.abc import (
    E21_Person,
    E53_Place,
    SimpleLabelModel,
)
from apis_core.apis_entities.models import AbstractEntity
from apis_core.collections.models import SkosCollectionContentObject
from apis_core.generic.abc import GenericModel
from apis_core.history.models import VersionMixin
from apis_core.relations.models import Relation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_interval.fields import FuzzyDateParserField

from .date_utils import nomansland_dateparser
from auditlog.registry import auditlog
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class IADateMixin(models.Model):
    class Meta:
        abstract = True

    start = FuzzyDateParserField(parser=nomansland_dateparser, null=True, blank=True)
    end = FuzzyDateParserField(parser=nomansland_dateparser, null=True, blank=True)


class VocabularyBaseModel(GenericModel, SimpleLabelModel):
    class Meta(GenericModel.Meta, SimpleLabelModel.Meta):
        abstract = True


class IABaseModel(VersionMixin, AbstractEntity):
    class Meta(VersionMixin.Meta, AbstractEntity.Meta):
        abstract = True


class Dynasty(VocabularyBaseModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = "dynasty"
        verbose_name_plural = "dynasties"


class PersonRole(VocabularyBaseModel):
    pass


class PersonMixin(models.Model):
    class Meta:
        abstract = True

    # can account for the origin [of the Person himself or his ancestors] or the profession;
    # attribute of relation Person/Place or Person/Monument//Object//Inscription
    person_title = models.TextField(
        blank=True, null=True, help_text="one title per line"
    )
    kunya = models.CharField(
        max_length=255, blank=True, null=True, help_text="Teknonym"
    )
    ism = models.CharField(max_length=255, blank=True, null=True, help_text="Forename")
    nasab = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Patronymic, can be several, eg. name of father, grandfather, etc.",
    )
    nisba = models.CharField(max_length=255, blank=True, null=True, help_text="Epithet")
    relation_to_caliph = models.CharField(max_length=255, blank=True, null=True)
    dynasty = models.ManyToManyField(Dynasty, blank=True)
    person_role = models.ManyToManyField(PersonRole, blank=True)


class MonumentType(VocabularyBaseModel):
    pass


class Material(VocabularyBaseModel):
    # Imported from Getty Thesaurus:
    # https://www.getty.edu/vow/AATFullDisplay?find=Alabaster&logic=AND&note=&english=N&prev_page=1&subjectid=300011101
    pass


class ObjectType(VocabularyBaseModel):
    # Imported from Getty Thesaurus:
    # https://www.getty.edu/vow/AATFullDisplay?find=Alabaster&logic=AND&note=&english=N&prev_page=1&subjectid=300011101
    pass


class Style(VocabularyBaseModel):
    pass


class Ornaments(VocabularyBaseModel):
    class Meta(VocabularyBaseModel.Meta):
        verbose_name = "ornament"
        verbose_name_plural = "ornaments"


class Technique(VocabularyBaseModel):
    pass


class Diacritics(VocabularyBaseModel):
    class Meta(VocabularyBaseModel.Meta):
        verbose_name = "diacritics"
        verbose_name_plural = "diacritics"


class TextClassification(VocabularyBaseModel):
    """Example:Benedictory text, Commemorative text, Construction text"""

    pass


class Language(VocabularyBaseModel):
    pass


class PreservationStateMixin(models.Model):
    class Meta:
        abstract = True

    # must be one of multiple states
    PRESERVATION_STATE_CHOICES = [
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Medium", "Medium"),
        ("Fragmentary", "Fragmentary"),
        ("Poor", "Poor"),
        ("Restored", "Restored"),
        ("Not extant", "Not extant"),
    ]
    preservation_state = models.CharField(
        max_length=20, choices=PRESERVATION_STATE_CHOICES, blank=True, null=True
    )
    remarks_on_preservation = models.TextField(blank=True, null=True)


class Monument(IABaseModel, PreservationStateMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    monument_type = models.ManyToManyField(MonumentType, blank=True)
    alternative_names = models.TextField(blank=True, null=True)

    @cached_property
    def location(self):
        return Place.objects.filter(
            pk__in=MonumentLocatedInPlace.objects.filter(
                subj_object_id=self.pk
            ).values_list("obj_object_id", flat=True)
        )

    def __str__(self):
        try:
            return f"{self.name} ({self.location.first()})"
        except Exception as e:
            logger.warning(f"Error in Monument __str__: {e}")

        return self.name


class Object(IABaseModel, PreservationStateMixin):
    object_type = models.ForeignKey(
        ObjectType, on_delete=models.SET_NULL, blank=True, null=True
    )
    find_spot = models.TextField(blank=True, null=True)
    current_position = models.TextField(blank=True, null=True)
    material = models.ManyToManyField(Material, blank=True)
    dimensions_length = models.CharField(
        max_length=255, blank=True, null=True, help_text="in cm"
    )
    dimensions_breadth = models.CharField(
        max_length=255, blank=True, null=True, help_text="in cm"
    )
    dimensions_height = models.CharField(
        max_length=255, blank=True, null=True, help_text="in cm"
    )

    @cached_property
    def monument(self):
        return Monument.objects.filter(
            pk__in=ObjectPartOfMonument.objects.filter(
                subj_object_id=self.pk
            ).values_list("obj_object_id", flat=True)
        )

    def __str__(self):
        prefix = f"{self.object_type} | " if self.object_type else ""
        if self.monument.exists():
            return f"{prefix}{self.monument.first()}".strip()
        return f"{prefix}{super().__str__()}"


class Inscription(IABaseModel, PreservationStateMixin):
    writing_field = models.TextField(blank=True, null=True)
    reference_tei = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Thesaurus d'Epigraphie Islamique ID",
    )
    distribution = models.TextField(blank=True, null=True)
    material = models.ManyToManyField(Material, blank=True)
    technique = models.ManyToManyField(Technique, blank=True)
    dimensions_length = models.CharField(
        max_length=255, blank=True, null=True, help_text="in cm"
    )
    dimensions_breadth = models.CharField(
        max_length=255, blank=True, null=True, help_text="in cm"
    )
    dimensions_height = models.CharField(
        max_length=255, blank=True, null=True, help_text="in cm"
    )
    remarks_on_material_and_technique = models.TextField(blank=True, null=True)
    style = models.ManyToManyField(Style, blank=True)
    diacritics = models.ManyToManyField(Diacritics, blank=True)
    ornaments = models.TextField(blank=True, null=True)
    remarks_on_style_and_ornaments = models.TextField(blank=True, null=True)
    text_classification = models.ManyToManyField(TextClassification, blank=True)
    language = models.ManyToManyField(Language, blank=True)
    text_original = models.TextField(blank=True, null=True)
    text_transliteration = models.TextField(blank=True, null=True)
    text_translation = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True, verbose_name="remarks on text")
    date = FuzzyDateParserField(parser=nomansland_dateparser, null=True, blank=True)
    remarks_on_date = models.TextField(blank=True, null=True)
    comparisons = models.TextField(blank=True, null=True)

    @cached_property
    def object(self):
        return Object.objects.filter(
            pk__in=InscriptionFoundInObject.objects.filter(
                subj_object_id=self.pk
            ).values_list("obj_object_id", flat=True)
        )

    def __str__(self):
        if self.object.exists():
            return f"{self.object.first()}"
        return super().__str__()


class Place(E53_Place, IABaseModel):
    alternative_names = models.TextField(blank=True, null=True)


class Illustration(IABaseModel):
    remarks = models.TextField(blank=True, null=True)

    @cached_property
    def inscription(self):
        return Inscription.objects.filter(
            pk__in=InscriptionRepresentedAsIllustration.objects.filter(
                obj_object_id=self.pk
            ).values_list("subj_object_id", flat=True)
        )

    @cached_property
    def monument(self):
        return Monument.objects.filter(
            pk__in=MonumentRepresentedAsIllustration.objects.filter(
                obj_object_id=self.pk
            ).values_list("subj_object_id", flat=True)
        )

    def __str__(self) -> str:
        if self.inscription.exists():
            return f"{self.inscription.first()}"
        if self.monument.exists():
            return f"{self.monument.first()}"

        return super().__str__()


class Person(E21_Person, PersonMixin, IABaseModel):
    GENDERS = [
        ("unknown", "unknown"),
        ("male", "Male"),
        ("female", "Female"),
    ]
    preferred_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="If not provided, the name will be generated from the name parts.",
    )
    active_years_start = FuzzyDateParserField(
        parser=nomansland_dateparser, null=True, blank=True
    )
    date_of_birth = None
    active_years_end = FuzzyDateParserField(
        parser=nomansland_dateparser, null=True, blank=True
    )
    date_of_death = None
    forename = None
    surname = None
    gender = models.CharField(max_length=7, choices=GENDERS)

    def __str__(self):
        if self.preferred_name:
            return self.preferred_name
        parts = [self.person_title, self.kunya, self.ism, self.nasab, self.nisba]
        return " ".join([part for part in parts if part])

    class Meta(E21_Person.Meta, IABaseModel.Meta):
        verbose_name = "person"
        verbose_name_plural = "persons"
        ordering = [
            "nisba",
        ]


class Work(IABaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class IARelationMixin(Relation, models.Model):
    class Meta:
        abstract = True

    remarks = models.TextField(blank=True, null=True)


class PlaceLocatedInPlace(IARelationMixin):
    subj_model = Place
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "place located in"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains"


class InscriptionQuotesAsSourceWork(IARelationMixin):
    subj_model = Inscription
    obj_model = Work
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "quotes"

    @classmethod
    def reverse_name(cls) -> str:
        return "is quoted in"


class MonumentLocatedInPlace(IARelationMixin):
    subj_model = Monument
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "monument located in"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains"


class ObjectPartOfMonument(IARelationMixin):
    subj_model = Object
    obj_model = Monument
    position = models.CharField(max_length=255, blank=True, null=True)
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "object part of monument"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains"


class MonumentRepresentedAsIllustration(IARelationMixin):
    subj_model = Monument
    obj_model = Illustration

    @classmethod
    def name(cls) -> str:
        return "monument represented as"

    @classmethod
    def reverse_name(cls) -> str:
        return "representation of"


class InscriptionFoundInMonument(IARelationMixin):
    subj_model = Inscription
    obj_model = Monument
    position = models.CharField(max_length=255, blank=True, null=True)
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "found in monument"

    @classmethod
    def reverse_name(cls) -> str:
        return "monument contains inscription"


class InscriptionFoundInObject(IARelationMixin):
    subj_model = Inscription
    obj_model = Object
    position = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "found in object"

    @classmethod
    def reverse_name(cls) -> str:
        return "object contains"


class PersonMentionedInInscription(PersonMixin, IARelationMixin):
    subj_model = Person
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)
    benediction = models.CharField(max_length=255, blank=True, null=True)
    introduction = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "person mentioned in"

    @classmethod
    def reverse_name(cls) -> str:
        return "mentions"


class MonumentMentionedInInscription(IARelationMixin):
    subj_model = Monument
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "monument mentioned in"

    @classmethod
    def reverse_name(cls) -> str:
        return "mentions"


class ObjectMentionedInInscription(IARelationMixin):
    subj_model = Object
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "object mentioned in"

    @classmethod
    def reverse_name(cls) -> str:
        return "mentions"


class PersonRelatedToInscription(PersonMixin, IARelationMixin):
    subj_model = Person
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "person related to"

    @classmethod
    def reverse_name(cls) -> str:
        return "is related to"


class MonumentRelatedToInscription(IARelationMixin):
    subj_model = Monument
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "monument related to"

    @classmethod
    def reverse_name(cls) -> str:
        return "is related to"


class ObjectRelatedToInscription(IARelationMixin):
    subj_model = Object
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "object related to"

    @classmethod
    def reverse_name(cls) -> str:
        return "is related to"


class ObjectRepresentedAsIllustration(IARelationMixin):
    subj_model = Object
    obj_model = Illustration

    @classmethod
    def name(cls) -> str:
        return "object represented as"

    @classmethod
    def reverse_name(cls) -> str:
        return "representation of"


class ObjectFoundInplace(IARelationMixin):
    subj_model = Object
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "object found in"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains object"


class InscriptionRepresentedAsIllustration(IARelationMixin):
    subj_model = Inscription
    obj_model = Illustration

    @classmethod
    def name(cls) -> str:
        return "inscription represented as"

    @classmethod
    def reverse_name(cls) -> str:
        return "representation of"


class PersonParentOfPerson(IARelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "parent of"

    @classmethod
    def reverse_name(cls) -> str:
        return "child of"


class PersonSiblingOfPerson(IARelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "sibling of"

    @classmethod
    def reverse_name(cls) -> str:
        return "sibling of"


class PersonHusbandOfPerson(IARelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "husband of"

    @classmethod
    def reverse_name(cls) -> str:
        return "wife of"


class PersonGrandparentOfPerson(IARelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "grandparent of"

    @classmethod
    def reverse_name(cls) -> str:
        return "grandchild of"


class PersonSubordinateOfPerson(IARelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "subordinate of"

    @classmethod
    def reverse_name(cls) -> str:
        return "master of"


class PersonIdenticalToPerson(IARelationMixin):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "identical to"

    @classmethod
    def reverse_name(cls) -> str:
        return "identical to"


class PersonRelatedToObject(PersonMixin, IARelationMixin):
    subj_model = Person
    obj_model = Object

    @classmethod
    def name(cls) -> str:
        return "person related to object"

    @classmethod
    def reverse_name(cls) -> str:
        return "object related to person"


class PersonRelatedToMonument(PersonMixin, IARelationMixin):
    subj_model = Person
    obj_model = Monument

    @classmethod
    def name(cls) -> str:
        return "person related to monument"

    @classmethod
    def reverse_name(cls) -> str:
        return "monument related to person"


class PersonMakerOfInscription(PersonMixin, IARelationMixin):
    subj_model = Person
    obj_model = Inscription

    @classmethod
    def name(cls) -> str:
        return "person maker of inscription"

    @classmethod
    def reverse_name(cls) -> str:
        return "inscription made by person"


class PersonMakerOfMonument(PersonMixin, IARelationMixin):
    subj_model = Person
    obj_model = Monument

    @classmethod
    def name(cls) -> str:
        return "person maker of monument"

    @classmethod
    def reverse_name(cls) -> str:
        return "monument made by person"


class PersonMakerOfObject(PersonMixin, IARelationMixin):
    subj_model = Person
    obj_model = Object

    @classmethod
    def name(cls) -> str:
        return "person maker of object"

    @classmethod
    def reverse_name(cls) -> str:
        return "object made by person"


class ObjectConnectedToObject(IARelationMixin):
    subj_model = Object
    obj_model = Object

    @classmethod
    def name(cls) -> str:
        return "object connected to"

    @classmethod
    def reverse_name(cls) -> str:
        return "object connected to"


class MonumentConnectedToMonument(IARelationMixin):
    subj_model = Monument
    obj_model = Monument

    @classmethod
    def name(cls) -> str:
        return "monument connected to"

    @classmethod
    def reverse_name(cls) -> str:
        return "monument connected to"


class GraphSearchSnapshot(models.Model):
    DEFAULT_KEY = "global"
    CACHE_KEY = "graph_nodes_links_snapshot_v2"

    key = models.CharField(max_length=64, unique=True, default=DEFAULT_KEY)
    nodes = models.JSONField(default=list, blank=True)
    links = models.JSONField(default=list, blank=True)
    node_count = models.PositiveIntegerField(default=0, editable=False)
    link_count = models.PositiveIntegerField(default=0, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("graph search snapshot")
        verbose_name_plural = _("Graph search snapshots")

    def __str__(self):
        return f"{self.key} ({self.node_count} nodes / {self.link_count} links)"

    @staticmethod
    def _assign_node_sizes(nodes, links, max_size=6, base_size=4, scale=10):
        degree = {}

        for link in links:
            source = link.get("source")
            target = link.get("target")
            if source:
                degree[source] = degree.get(source, 0) + 1
            if target:
                degree[target] = degree.get(target, 0) + 1

        for node in nodes:
            d = degree.get(node["id"], 0)
            size = base_size + max_size * (math.atan(d / scale) / (math.pi / 2))
            node["size"] = round(size, 2)

        return nodes

    @classmethod
    def build_payload(cls):
        nodes = []

        def iter_iabase_models(base_model):
            for model in base_model.__subclasses__():
                if not model._meta.abstract:
                    yield model
                yield from iter_iabase_models(model)

        def get_relation_labels(relation):
            if hasattr(relation, "name") and callable(relation.name):
                label = relation.name()
            else:
                label = relation.__class__.__name__

            if hasattr(relation, "reverse_name") and callable(relation.reverse_name):
                reverse_label = relation.reverse_name()
            else:
                reverse_label = f"{label} [REVERSE]"

            return label, reverse_label

        def get_collections_by_object_id(model, object_ids):
            if not object_ids:
                return {}

            content_type = ContentType.objects.get_for_model(model)
            collection_map = {}
            collection_links = (
                SkosCollectionContentObject.objects.filter(
                    content_type=content_type,
                    object_id__in=object_ids,
                )
                .select_related("collection")
                .iterator(chunk_size=5000)
            )
            for link in collection_links:
                collection_map.setdefault(link.object_id, []).append(
                    {
                        "id": link.collection_id,
                        "label": str(link.collection),
                    }
                )
            return collection_map

        def add_nodes(qs, group, collection_map):
            for obj in qs:
                node = {"id": obj.id, "label": str(obj), "group": group}
                collections = collection_map.get(obj.id, [])
                if collections:
                    node["collection_ids"] = [collection["id"] for collection in collections]
                    node["collections"] = collections
                nodes.append(node)

        seen_models = set()
        for model in iter_iabase_models(IABaseModel):
            if model in seen_models:
                continue
            seen_models.add(model)
            queryset = model.objects.only("id")
            object_ids = list(queryset.values_list("id", flat=True))
            collection_map = get_collections_by_object_id(model, object_ids)
            add_nodes(queryset, model._meta.model_name, collection_map)

        node_ids = {n["id"] for n in nodes}
        links = []
        relations = (
            Relation.objects.select_subclasses()
            .exclude(subj_object_id__isnull=True, obj_object_id__isnull=True)
            .filter(subj_object_id__in=node_ids, obj_object_id__in=node_ids)
            .iterator(chunk_size=5000)
        )
        for relation in relations:
            label, reverse_label = get_relation_labels(relation)
            links.append(
                {
                    "source": relation.subj_object_id,
                    "target": relation.obj_object_id,
                    "label": label,
                    "reverse_label": reverse_label,
                    "group": f"{label}|{reverse_label}",
                }
            )

        nodes = cls._assign_node_sizes(nodes, links)
        return nodes, links

    @classmethod
    def rebuild(cls):
        nodes, links = cls.build_payload()
        snapshot, _ = cls.objects.update_or_create(
            key=cls.DEFAULT_KEY,
            defaults={
                "nodes": nodes,
                "links": links,
                "node_count": len(nodes),
                "link_count": len(links),
            },
        )
        cache.delete(cls.CACHE_KEY)
        return snapshot


auditlog.register(MonumentType)
auditlog.register(Material)
auditlog.register(ObjectType)
auditlog.register(Style)
auditlog.register(Technique)
auditlog.register(Diacritics)
auditlog.register(TextClassification)
auditlog.register(Language)
auditlog.register(Ornaments)
auditlog.register(Dynasty)
auditlog.register(PersonRole)
auditlog.register(Monument)
auditlog.register(Object)
auditlog.register(Inscription)
auditlog.register(Place)
auditlog.register(Illustration)
auditlog.register(Person)
auditlog.register(Work)
auditlog.register(PlaceLocatedInPlace)
auditlog.register(InscriptionQuotesAsSourceWork)
auditlog.register(MonumentLocatedInPlace)
auditlog.register(ObjectPartOfMonument)
auditlog.register(MonumentRepresentedAsIllustration)
auditlog.register(InscriptionFoundInMonument)
auditlog.register(InscriptionFoundInObject)
auditlog.register(PersonMentionedInInscription)
auditlog.register(MonumentMentionedInInscription)
auditlog.register(ObjectMentionedInInscription)
auditlog.register(PersonRelatedToInscription)
auditlog.register(MonumentRelatedToInscription)
auditlog.register(ObjectRelatedToInscription)
auditlog.register(ObjectRepresentedAsIllustration)
auditlog.register(ObjectFoundInplace)
auditlog.register(InscriptionRepresentedAsIllustration)
