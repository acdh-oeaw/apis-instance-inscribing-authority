from apis_core.generic.forms import GenericModelForm


class InscriptionForm(GenericModelForm):

    field_order = [
        "material",
        "technique",
        "dimensions_length",
        "dimensions_breadth",
        "dimensions_height",
        "remarks_on_material_and_technique",
        "preservation_state",
        "remarks_on_preservation",
        "distribution",
        "style",
        "diacritics",
        "ornaments",
        "remarks_on_style_and_ornaments",
        "text_classification",
        "language",
        "writing_field",
        "text_original",
        "text_transliteration",
        "text_translation",
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
        "kunya",
        "ism",
        "nasab",
        "nisba",
        "relation to caliph",
    ]
