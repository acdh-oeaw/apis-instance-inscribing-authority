import django_tables2 as tables
from apis_core.generic.tables import GenericTable


class IABaseModelTable(GenericTable):
    class Meta(GenericTable.Meta):
        attrs = {
            "td": {"dir": "auto"},
        }
