from apis_core.apis_entities.abc import SimpleLabelModel
from apis_core.generic.abc import GenericModel


class Country(GenericModel, SimpleLabelModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = "country"
        verbose_name_plural = "countries"

    pass


class MonumentType(GenericModel, SimpleLabelModel):
    pass


class Material(GenericModel, SimpleLabelModel):
    pass


class Technique(GenericModel, SimpleLabelModel):
    pass


class Diacritics(GenericModel, SimpleLabelModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = "diacritics"
        verbose_name_plural = "diacritics"

    pass


class Ornaments(GenericModel, SimpleLabelModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = "ornaments"
        verbose_name_plural = "ornaments"

    pass


class TextClassification(GenericModel, SimpleLabelModel):
    """Example:Benedictory text, Commemorative text, Construction text"""

    pass


class Language(GenericModel, SimpleLabelModel):
    pass


class Dynasty(GenericModel, SimpleLabelModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = "dynasty"
        verbose_name_plural = "dynasties"

    pass


class PersonRole(GenericModel, SimpleLabelModel):
    pass
