import django_tables2 as tables
from apis_core.generic.tables import GenericTable
from apis_core.relations.tables import RelationsListTable


class IABaseModelTable(GenericTable):
    class Meta(GenericTable.Meta):
        attrs = {
            "td": {"dir": "auto"},
        }
        exclude = ("id",)
        sequence = ("...", "actions")


class IABaseModelRelationsTable(RelationsListTable):
    class Meta(RelationsListTable.Meta):
        attrs = {
            "td": {"dir": "auto"},
        }
        exclude = ("id",)
        sequence = ("...", "actions")
        orderable = False


class InscriptionPersonRelationsTable(IABaseModelRelationsTable):
    class Meta(IABaseModelRelationsTable.Meta):
        sequence = ("...", "introduction", "full_name", "benediction", "actions")

    person_role = tables.Column(accessor="person_role")
    full_name = tables.Column(accessor="ism", verbose_name="Full Name")
    introduction = tables.Column(accessor="introduction", verbose_name="Introduction")
    benediction = tables.Column(accessor="benediction", verbose_name="Benediction")

    def render_person_role(self, record):
        roles = record.person_role.all()
        return ", ".join([str(role) for role in roles]) if roles else "-"

    def render_full_name(self, record):
        parts = [
            getattr(record, "person_title", None),
            getattr(record, "ism", None),
            getattr(record, "kunya", None),
            getattr(record, "nasab", None),
            getattr(record, "nisba", None),
            getattr(record, "relation_to_caliph", None),
        ]
        return " ".join([part for part in parts if part])


class PersonInscriptionRelationsTable(InscriptionPersonRelationsTable):
    class Meta(InscriptionPersonRelationsTable.Meta):
        pass


class PersonTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "dynasty")


class MonumentTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "monument_type")


class ObjectTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "object_type")
