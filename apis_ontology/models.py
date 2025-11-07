from apis_core.apis_entities.abc import (
    E21_Person,
    E53_Place,
    SimpleLabelModel,
)
from apis_core.relations.models import Relation
from apis_core.apis_entities.models import AbstractEntity
from apis_core.generic.abc import GenericModel
from apis_core.history.models import VersionMixin
from django.db import models
from django_interval.fields import FuzzyDateParserField
from .date_utils import nomansland_dateparser


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


class RelationBaseModel(Relation):
    class Meta(Relation.Meta):
        abstract = True


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


class Technique(VocabularyBaseModel):
    pass


class Diacritics(VocabularyBaseModel):
    class Meta(VocabularyBaseModel.Meta):
        verbose_name = "diacritics"
        verbose_name_plural = "diacritics"

    pass


class Ornaments(VocabularyBaseModel):
    class Meta(VocabularyBaseModel.Meta):
        verbose_name = "ornaments"
        verbose_name_plural = "ornaments"

    pass


class TextClassification(VocabularyBaseModel):
    """Example:Benedictory text, Commemorative text, Construction text"""

    pass


class Language(VocabularyBaseModel):
    pass


class Dynasty(VocabularyBaseModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = "dynasty"
        verbose_name_plural = "dynasties"

    pass


class PersonRole(VocabularyBaseModel):
    pass


class PreservationState(VocabularyBaseModel):
    pass


class Monument(IABaseModel):

    pass


class Object(IABaseModel):

    pass


class Inscription(IABaseModel):

    pass


class Place(E53_Place, IABaseModel):
    pass


class Illustration(IABaseModel):
    pass


class Person(E21_Person, IABaseModel):
    GENDERS = [
        ("unknown", "unknown"),
        ("male", "Male"),
        ("female", "Female"),
    ]

    person_title = models.TextField(blank=True, null=True)
    kunya = models.CharField(max_length=255, blank=True, null=True)
    ism = models.CharField(max_length=255, blank=True, null=True)
    nasab = models.CharField(max_length=255, blank=True, null=True)
    nisba = models.CharField(max_length=255, blank=True, null=True)
    relation_to_caliph = models.CharField(max_length=255, blank=True, null=True)
    preferred_name = models.CharField(max_length=255, blank=True, null=True)
    active_years_start = FuzzyDateParserField(
        parser=nomansland_dateparser, null=True, blank=True
    )
    active_years_end = FuzzyDateParserField(
        parser=nomansland_dateparser, null=True, blank=True
    )
    dynasty = models.ManyToManyField(Dynasty, blank=True, null=True)
    person_role = models.ManyToManyField(PersonRole, blank=True)
    forename = None
    surname = None
    gender = models.CharField(max_length=7, choices=GENDERS)

    def __str__(self):
        parts = [self.person_title, self.ism, self.kunya, self.nasab, self.nisba]
        return " ".join([part for part in parts if part])

    pass

    class Meta(E21_Person.Meta, IABaseModel.Meta):
        verbose_name = "person"
        verbose_name_plural = "persons"
        ordering = [
            "nisba",
        ]


class Work(IABaseModel):
    name = models.CharField(max_length=255)
    pass
