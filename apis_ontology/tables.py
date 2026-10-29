import django_tables2 as tables
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import mark_safe

from apis_core.generic.tables import GenericTable
from apis_core.relations.tables import RelationsListTable


class IABaseModelTable(GenericTable):
    pk = tables.Column(accessor="pk", verbose_name="ID", orderable=True)

    class Meta(GenericTable.Meta):
        attrs = {
            "td": {"dir": "auto"},
        }
        sequence = ("pk", "...", "actions")


class VocabularyBaseModelTable(GenericTable):
    def render_label(self, record):
        return mark_safe(record.label) if record.label else "-"


class IABaseModelRelationsTable(RelationsListTable):
    class Meta(RelationsListTable.Meta):
        attrs = {
            "td": {"dir": "auto"},
        }
        exclude = ("id",)
        sequence = ("...", "actions")
        orderable = False


class FoundInRelationsTable(IABaseModelRelationsTable):
    class Meta(IABaseModelRelationsTable.Meta):
        sequence = ("...", "position", "actions")

    position = tables.Column(accessor="position")


class ReferenceRelationsTable(IABaseModelRelationsTable):
    class Meta(IABaseModelRelationsTable.Meta):
        sequence = ("...", "reference", "actions")

    reference = tables.Column(accessor="reference")

    def render_reference(self, value, record):
        return mark_safe(linebreaksbr(record.reference)) if record.reference else "-"


class PersonRelationsTable(
    ReferenceRelationsTable,
    IABaseModelRelationsTable,
):
    class Meta(IABaseModelRelationsTable.Meta):
        sequence = (
            "...",
            "person_role",
            "introduction",
            "full_name",
            "benediction",
            "reference",
            "actions",
        )

    person_role = tables.Column(accessor="person_role")
    full_name = tables.Column(verbose_name="Full Name", empty_values=())
    introduction = tables.Column(accessor="introduction", verbose_name="Introduction")
    benediction = tables.Column(accessor="benediction", verbose_name="Benediction")

    def render_person_role(self, record):
        roles = record.person_role.all()
        return ", ".join([str(role) for role in roles]) if roles else "-"

    def render_full_name(self, record):
        parts = [
            getattr(record, "person_title", None),
            getattr(record, "honorifics", None),
            getattr(record, "kunya", None),
            getattr(record, "ism", None),
            getattr(record, "nasab", None),
            getattr(record, "nisba", None),
            getattr(record, "relation_to_caliph", None),
        ]
        return " ".join([part for part in parts if part])


class InscriptionPersonRelationsTable(PersonRelationsTable):
    class Meta(PersonRelationsTable.Meta):
        pass


class PersonInscriptionRelationsTable(PersonRelationsTable):
    class Meta(PersonRelationsTable.Meta):
        pass


class PersonObjectRelationsTable(PersonRelationsTable):
    class Meta(PersonRelationsTable.Meta):
        sequence = ("...", "person_role", "reference", "actions")
        exclude = ("introduction", "full_name", "benediction")


class ObjectPersonRelationsTable(PersonRelationsTable):
    class Meta(PersonRelationsTable.Meta):
        sequence = ("...", "person_role", "reference", "actions")
        exclude = ("introduction", "full_name", "benediction")


class MonumentPersonRelationsTable(PersonRelationsTable):
    class Meta(PersonRelationsTable.Meta):
        pass


class PersonMonumentRelationsTable(PersonRelationsTable):
    class Meta(PersonRelationsTable.Meta):
        pass


class InscriptionMonumentRelationsTable(FoundInRelationsTable):
    class Meta(FoundInRelationsTable.Meta):
        pass


class MonumentInscriptionRelationsTable(FoundInRelationsTable):
    class Meta(FoundInRelationsTable.Meta):
        pass


class InscriptionObjectRelationsTable(FoundInRelationsTable):
    class Meta(FoundInRelationsTable.Meta):
        pass

    text_classification = tables.Column(
        accessor="text_classification", verbose_name="Text Classification"
    )


class ObjectInscriptionRelationsTable(FoundInRelationsTable):
    class Meta(FoundInRelationsTable.Meta):
        pass

    text_classification = tables.Column(
        accessor="text_classification", verbose_name="Text Classification"
    )


class ObjectMonumentRelationsTable(FoundInRelationsTable):
    class Meta(FoundInRelationsTable.Meta):
        pass


class MonumentObjectRelationsTable(FoundInRelationsTable):
    class Meta(FoundInRelationsTable.Meta):
        pass


class InscriptionWorkRelationsTable(ReferenceRelationsTable):
    class Meta(ReferenceRelationsTable.Meta):
        pass


class WorkInscriptionRelationsTable(ReferenceRelationsTable):
    class Meta(ReferenceRelationsTable.Meta):
        pass


class PersonTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "dynasty", "person_role")


class InscriptionTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "text_classification")


class MonumentTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "monument_type")


class ObjectTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "object_type")
