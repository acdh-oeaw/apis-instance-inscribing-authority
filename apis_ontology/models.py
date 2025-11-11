from apis_core.apis_entities.abc import (
    E21_Person,
    E53_Place,
    SimpleLabelModel,
)
from apis_core.apis_entities.models import AbstractEntity
from apis_core.generic.abc import GenericModel
from apis_core.history.models import VersionMixin
from apis_core.relations.models import Relation
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
    alternative_names = models.TextField(blank=True, null=True)
    is_extant = models.BooleanField(default=True)  # type: ignore
    remarks_on_preservation = models.TextField(blank=True, null=True)


class Object(IABaseModel):
    object_type = models.CharField(max_length=255, blank=True, null=True)
    find_spot = models.TextField(blank=True, null=True)
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
    is_extant = models.BooleanField(default=True)  # type: ignore
    remarks_on_preservation = models.TextField(blank=True, null=True)


class Inscription(IABaseModel):
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
    is_extant = models.BooleanField(default=True)  # type: ignore
    style = models.ManyToManyField(Style, blank=True)
    diacritics = models.ManyToManyField(Diacritics, blank=True)
    ornaments = models.TextField(blank=True, null=True)
    remarks_on_style_and_ornaments = models.TextField(blank=True, null=True)
    text_classification = models.ManyToManyField(TextClassification, blank=True)
    language = models.ManyToManyField(Language, blank=True)
    text_original = models.TextField(blank=True, null=True)
    text_transliteration = models.TextField(blank=True, null=True)
    text_translation = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    date = FuzzyDateParserField(parser=nomansland_dateparser, null=True, blank=True)
    remarks_on_date = models.TextField(blank=True, null=True)
    comparisons = models.TextField(blank=True, null=True)


class Place(E53_Place, IABaseModel):
    alternative_names = models.TextField(blank=True, null=True)


class Illustration(IABaseModel):
    remarks = models.TextField(blank=True, null=True)


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


class PlaceLocatedInPlace(Relation):
    subj_model = Place
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "located in"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains"


class InscriptionQuotesAsSourceWork(Relation):
    subj_model = Inscription
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "quotes as source"

    @classmethod
    def reverse_name(cls) -> str:
        return "is quoted as source in"


class MonumentLocatedInPlace(Relation):
    subj_model = Monument
    obj_model = Place

    @classmethod
    def name(cls) -> str:
        return "located in"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains"


class ObjectPartOfMonument(Relation):
    subj_model = Object
    obj_model = Monument
    position = models.CharField(max_length=255, blank=True, null=True)
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "part of"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains part"


class MonumentRepresentedAsIllustration(Relation):
    subj_model = Monument
    obj_model = Illustration

    @classmethod
    def name(cls) -> str:
        return "represented as"

    @classmethod
    def reverse_name(cls) -> str:
        return "representation of"


class InscriptionFoundInMonument(Relation):
    subj_model = Inscription
    obj_model = Monument
    position = models.CharField(max_length=255, blank=True, null=True)
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "found in"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains inscription"


class InscriptionFoundInObject(Relation):
    subj_model = Inscription
    obj_model = Object
    position = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "found in"

    @classmethod
    def reverse_name(cls) -> str:
        return "contains inscription"


class PersonMentionedInInscription(Relation):
    subj_model = Person
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "mentioned in"

    @classmethod
    def reverse_name(cls) -> str:
        return "mentions"


class MonumentMentionedInInscription(Relation):
    subj_model = Monument
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "mentioned in"

    @classmethod
    def reverse_name(cls) -> str:
        return "mentions"


class ObjectMentionedInInscription(Relation):
    subj_model = Object
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "mentioned in"

    @classmethod
    def reverse_name(cls) -> str:
        return "mentions"


class PersonRelatedToInscription(Relation):
    subj_model = Person
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "related to"

    @classmethod
    def reverse_name(cls) -> str:
        return "is related to"


class MonumentRelatedToInscription(Relation):
    subj_model = Monument
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "related to"

    @classmethod
    def reverse_name(cls) -> str:
        return "is related to"


class ObjectRelatedToInscription(Relation):
    subj_model = Object
    obj_model = Inscription
    reference = models.TextField(blank=True, null=True)

    @classmethod
    def name(cls) -> str:
        return "related to"

    @classmethod
    def reverse_name(cls) -> str:
        return "is related to"
