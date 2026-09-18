from apis_core.generic.forms import GenericModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Row, Column

from crispy_forms.layout import Column, Row, Layout


class DimensionsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        dimensions = {
            "dimensions_length",
            "dimensions_breadth",
            "dimensions_height",
        }

        layout = []
        dimensions_added = False

        for name in self.fields:
            if name in dimensions:
                if not dimensions_added:
                    layout.append(
                        Row(
                            Column("dimensions_length"),
                            Column("dimensions_breadth"),
                            Column("dimensions_height"),
                        )
                    )
                    dimensions_added = True
                continue

            layout.append(name)

        self.helper.layout = Layout(*layout)


class InscriptionForm(DimensionsMixin, GenericModelForm):

    field_order = [
        "material",
        "technique",
        "dimensions_length",
        "dimensions_breadth",
        "dimensions_height",
        "remarks_on_material_and_technique",
        "preservation_state",
        "remarks_on_preservation",
        "writing_field",
        "distribution",
        "style",
        "diacritics",
        "ornaments",
        "remarks_on_style_and_ornaments",
        "text_classification",
        "language",
        "text_original",
        "text_transliteration",
        "text_translation",
        "reading_author",
        "remarks",
        "date",
        "remarks_on_date",
        "comparisons",
        "reference_tei",
    ]


class PersonForm(GenericModelForm):
    field_order = [
        "preferred_name",
        "person_role",
        "active_years_start",
        "active_years_end",
        "dynasty",
        "gender",
        "person_title",
        "honorifics",
        "kunya",
        "ism",
        "nasab",
        "nisba",
        "relation to caliph",
    ]


class ObjectForm(DimensionsMixin, GenericModelForm):
    field_order = [
        "object_type",
        "original_position",
        "find_spot",
        "current_position",
        "material",
        "dimensions_length",
        "dimensions_breadth",
        "dimensions_height",
        "perservation_state",
        "remarks_on_preservation",
    ]
