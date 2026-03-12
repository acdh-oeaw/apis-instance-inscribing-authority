import django_tables2 as tables
from apis_core.generic.tables import GenericTable


class IABaseModelTable(GenericTable):
    class Meta(GenericTable.Meta):
        attrs = {
            "td": {"dir": "auto"},
        }
        exclude = (
            "id",
            "noduplicate",
        )
        sequence = ("...", "view", "edit", "delete")


class PersonTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "dynasty")


class MonumentTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "monument_type")


class ObjectTable(IABaseModelTable):
    class Meta(IABaseModelTable.Meta):
        fields = ("desc", "object_type")
