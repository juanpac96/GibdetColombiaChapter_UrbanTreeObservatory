"""
Mapping utilities for converting between Spanish and English values in the database.
"""

from apps.taxonomy.models import Species
from apps.reports.models import Measurement, Observation

# Taxonomy mappings
ORIGIN_MAPPINGS = {
    "Exótica": Species.Origin.EXOTIC,
    "Exotica": Species.Origin.EXOTIC,
    "Nativa": Species.Origin.NATIVE,
    # Add more mappings as needed
}

IUCN_STATUS_MAPPINGS = {
    "Datos insuficientes": Species.IUCNStatus.DATA_DEFICIENT,
    "Preocupación menor": Species.IUCNStatus.LEAST_CONCERN,
    "Preocupacion menor": Species.IUCNStatus.LEAST_CONCERN,
    "Casi amenazada": Species.IUCNStatus.NEAR_THREATENED,
    "Vulnerable": Species.IUCNStatus.VULNERABLE,
    "En peligro": Species.IUCNStatus.ENDANGERED,
    "En peligro crítico": Species.IUCNStatus.CRITICALLY_ENDANGERED,
    "En peligro critico": Species.IUCNStatus.CRITICALLY_ENDANGERED,
    "Extinta en estado silvestre": Species.IUCNStatus.EXTINCT_IN_WILD,
    "Extinta": Species.IUCNStatus.EXTINCT,
    "No evaluado": Species.IUCNStatus.NOT_EVALUATED,
    "No evaluada": Species.IUCNStatus.NOT_EVALUATED,
    # Add more mappings as needed
}

LIFEFORM_MAPPINGS = {
    "Árbol": Species.LifeForm.TREE,
    "Arbol": Species.LifeForm.TREE,
    "Palmera": Species.LifeForm.PALM_TREE,
    "Arbusto": Species.LifeForm.SHRUB,
    "Otro": Species.LifeForm.OTHER,
    "Otra": Species.LifeForm.OTHER,
    # Add more mappings as needed
}

# Measurement mappings
MEASURED_ATTRIBUTE_MAPPINGS = {
    "Altura de fuste": Measurement.MeasuredAttribute.TRUNK_HEIGHT,
    "Altura total": Measurement.MeasuredAttribute.TOTAL_HEIGHT,
    "Diámetro de copa": Measurement.MeasuredAttribute.CROWN_DIAMETER,
    "Diametro de copa": Measurement.MeasuredAttribute.CROWN_DIAMETER,
    "DAP": Measurement.MeasuredAttribute.DIAMETER_BH,
    "Volumen": Measurement.MeasuredAttribute.VOLUME,
    "Densidad de madera": Measurement.MeasuredAttribute.WOOD_DENSITY,
    "Otro": Measurement.MeasuredAttribute.OTHER,
    "No reportado": Measurement.MeasuredAttribute.NOT_REPORTED,
    "No reportada": Measurement.MeasuredAttribute.NOT_REPORTED,
    # Add more mappings as needed
}

MEASUREMENT_UNIT_MAPPINGS = {
    "m": Measurement.MeasurementUnit.METERS,
    "metros": Measurement.MeasurementUnit.METERS,
    "m3": Measurement.MeasurementUnit.CUBIC_METERS,
    "metros cúbicos": Measurement.MeasurementUnit.CUBIC_METERS,
    "metros cubicos": Measurement.MeasurementUnit.CUBIC_METERS,
    "cm": Measurement.MeasurementUnit.CENTIMETERS,
    "centímetros": Measurement.MeasurementUnit.CENTIMETERS,
    "centimetros": Measurement.MeasurementUnit.CENTIMETERS,
    "mm": Measurement.MeasurementUnit.MILLIMETERS,
    "milímetros": Measurement.MeasurementUnit.MILLIMETERS,
    "milimetros": Measurement.MeasurementUnit.MILLIMETERS,
    "g/cm3": Measurement.MeasurementUnit.GRAMS_PER_CUBIC_CM,
    "gramos por centímetro cúbico": Measurement.MeasurementUnit.GRAMS_PER_CUBIC_CM,
    "gramos por centimetro cubico": Measurement.MeasurementUnit.GRAMS_PER_CUBIC_CM,
    "Otro": Measurement.MeasurementUnit.OTHER,
    "Otra": Measurement.MeasurementUnit.OTHER,
    "No reportado": Measurement.MeasurementUnit.NOT_REPORTED,
    "No reportada": Measurement.MeasurementUnit.NOT_REPORTED,
    # Add more mappings as needed
}

MEASUREMENT_METHOD_MAPPINGS = {
    "Estimación óptica": Measurement.MeasurementMethod.OPTICAL_ESTIMATION,
    "Estimacion optica": Measurement.MeasurementMethod.OPTICAL_ESTIMATION,
    "Cinta diamétrica": Measurement.MeasurementMethod.DIAMETER_TAPE,
    "Cinta diametrica": Measurement.MeasurementMethod.DIAMETER_TAPE,
    "Ecuación de volumen": Measurement.MeasurementMethod.VOLUME_EQUATION,
    "Ecuacion de volumen": Measurement.MeasurementMethod.VOLUME_EQUATION,
    "Base de datos de densidad de madera": Measurement.MeasurementMethod.WOOD_DENSITY_DB,
    "Otro": Measurement.MeasurementMethod.OTHER,
    "Otra": Measurement.MeasurementMethod.OTHER,
    "No reportado": Measurement.MeasurementMethod.NOT_REPORTED,
    "No reportada": Measurement.MeasurementMethod.NOT_REPORTED,
    # Add more mappings as needed
}

# Observation mappings
REPRODUCTIVE_CONDITION_MAPPINGS = {
    "Floración": Observation.ReproductiveCondition.FLOWERING,
    "Floracion": Observation.ReproductiveCondition.FLOWERING,
    "Fructificación": Observation.ReproductiveCondition.FRUITING,
    "Fructificacion": Observation.ReproductiveCondition.FRUITING,
    "Estéril": Observation.ReproductiveCondition.STERILE,
    "Esteril": Observation.ReproductiveCondition.STERILE,
    "No reportado": Observation.ReproductiveCondition.NOT_REPORTED,
    "No reportada": Observation.ReproductiveCondition.NOT_REPORTED,
    # Add more mappings as needed
}

PHYTOSANITARY_STATUS_MAPPINGS = {
    "Sano": Observation.PhytosanitaryStatus.HEALTHY,
    "Enfermo": Observation.PhytosanitaryStatus.SICK,
    "Muerto": Observation.PhytosanitaryStatus.DEAD,
    "No reportado": Observation.PhytosanitaryStatus.NOT_REPORTED,
    "No reportada": Observation.PhytosanitaryStatus.NOT_REPORTED,
    # Add more mappings as needed
}

PHYSICAL_CONDITION_MAPPINGS = {
    "Bueno": Observation.PhysicalCondition.GOOD,
    "Buena": Observation.PhysicalCondition.GOOD,
    "Regular": Observation.PhysicalCondition.FAIR,
    "Malo": Observation.PhysicalCondition.POOR,
    "Mala": Observation.PhysicalCondition.POOR,
    "No reportado": Observation.PhysicalCondition.NOT_REPORTED,
    "No reportada": Observation.PhysicalCondition.NOT_REPORTED,
    # Add more mappings as needed
}

FOLIAGE_DENSITY_MAPPINGS = {
    "Denso": Observation.FoliageDensity.DENSE,
    "Densa": Observation.FoliageDensity.DENSE,
    "Medio": Observation.FoliageDensity.MEDIUM,
    "Media": Observation.FoliageDensity.MEDIUM,
    "Escaso": Observation.FoliageDensity.SPARSE,
    "Escasa": Observation.FoliageDensity.SPARSE,
    "No reportado": Observation.FoliageDensity.NOT_REPORTED,
    "No reportada": Observation.FoliageDensity.NOT_REPORTED,
    # Add more mappings as needed
}

AESTHETIC_VALUE_MAPPINGS = {
    "Esencial": Observation.AestheticValue.ESSENTIAL,
    "Emblemático": Observation.AestheticValue.EMBLEMATIC,
    "Emblematico": Observation.AestheticValue.EMBLEMATIC,
    "Deseable": Observation.AestheticValue.DESIRABLE,
    "Indiferente": Observation.AestheticValue.INDIFFERENT,
    "Inaceptable": Observation.AestheticValue.UNACCEPTABLE,
    "No reportado": Observation.AestheticValue.NOT_REPORTED,
    "No reportada": Observation.AestheticValue.NOT_REPORTED,
    # Add more mappings as needed
}

GROWTH_PHASE_MAPPINGS = {
    "F1": Observation.GrowthPhase.F1,
    "F2": Observation.GrowthPhase.F2,
    "F3": Observation.GrowthPhase.F3,
    "No reportado": Observation.GrowthPhase.NOT_REPORTED,
    "No reportada": Observation.GrowthPhase.NOT_REPORTED,
    # Add more mappings as needed
}


def get_mapped_value(value, mapping_dict, default=None):
    """
    Get the mapped value from a dictionary, case-insensitive.
    If not found, return the default value.

    Args:
        value: The value to map
        mapping_dict: Dictionary with mappings
        default: Default value to return if mapping not found

    Returns:
        The mapped value or default
    """
    if value is None:
        return default

    # Try direct lookup
    if value in mapping_dict:
        return mapping_dict[value]

    # Try case-insensitive lookup
    value_lower = value.lower()
    for k, v in mapping_dict.items():
        if k.lower() == value_lower:
            return v

    return default
