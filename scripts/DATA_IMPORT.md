# Urban Tree Observatory Data Import Analysis

## Taxonomy Data Issues

### Missing Fields in CSV vs. Django Model

The taxonomy_details.csv has unexpected fields that need to be addressed:

| CSV Field | Issue | Action Required |
|-----------|-------|----------------|
| **gbif_id** | Points to a resource on gbif.org (e.g., gbif.org/species/2977854) or contains "No identificado" | **ACTION:** Add a URL field to the Species model or store only the numeric ID and build the URL in a property method |
| **lifeForm** | New field not in current model | **ACTION:** Explore this data in the exploration script. Don't update models yet |
| **establishmentMeans** | New field not in current model | **ACTION:** Explore this data in the exploration script. Don't update models yet |
| **iucn_category** | Similar to existing field | **ACTION:** Map to existing field `iucn_status` (IUCNStatus enum) |

#### Proposed Model Changes

```python
# Species model update
class Species(models.Model):
    # Add new field for GBIF ID
    gbif_id = models.CharField(max_length=20, blank=True, null=True, 
                              help_text="GBIF species identifier")
    
    # Alternatively, add a property method:
    @property
    def gbif_url(self):
        if self.gbif_id and self.gbif_id != "No identificado":
            return f"https://gbif.org/species/{self.gbif_id}"
        return None
```

### Species Information

Naming inconsistencies:

- "specie" in CSV vs. "name" in our model
  - CSV's "specie" field contains the genus. For our database, we need to extract just the species name for the "name" field.
- "accept_scientific_name" (CSV) vs. "accepted_scientific_name" (our model)

### Empty Values

- iucn_category in taxonomy CSV contains the full name in Spanish plus English initials, while iucn_status in observations_details contains only the initials.

## Biodiversity Records Issues

### Field Mapping

- code_record in CSV vs. uuid in our model:
  - Example in biodiversity: "99899 -- F3"
  - In measurements: called "record_code" with same pattern
  - In observations: called "record_code" with pattern "646_99899" (first part is autoincrement, second part is unique identifier)

- Use "place_id" to find the related place in the place CSV.
- Convert latitude/longitude fields to a Point object (epsg_id appears to be "4326").

### Foreign Keys

- place_id maps to the unnamed first column in place (index in original pandas dataframe).
  - Could use the site field for extra validation when mapping.

## Measurement Data Issues

### Field Names

Our model's TextChoices need to map to field names in the CSV:

- "total_height" → MeasuredAttribute.TOTAL_HEIGHT
- "crown_diameter" → Consider changing our model's "canopy_diameter" to "crown_diameter"
- "diameter_bh_cm" → MeasuredAttribute.DIAMETER_BH
- "volume_m3" → MeasuredAttribute.VOLUME
- "density_g_cm3" → MeasuredAttribute.WOOD_DENSITY

### Measurement Methods

Spanish terms need mapping:

- "Estimación optica" → "Optical estimation"
- "Ecuación de volumen" → "Volume equation"
- "Cinta diametrica" → "Diameter tape"
- "Wood Density Database" (already in English)

## Observations Data Issues

### Spanish Values for TextChoices

Need to map:

- Reproductive conditions: Mostly "No reportado" (Not reported)
- Phytosanitary status: "Sano" (Healthy), "Enfermo" (Sick), "Muerto" (Dead), "Critico" (Critical) - add "Critical" as a choice
- Physical condition: "Bueno" (Good), "Regular" (Fair), "Malo" (Poor)
- Foliage density: "Denso" (Dense), "Medio" (Medium), "Ralo" (Sparse)
- Aesthetic value: "Deseable" (Desirable), "Indiferente" (Indifferent), etc.
- Growth phase: F1, F2, F3 (match our model)
- Origin: "Exotica" (Exotic), "Nativa" (Native)
- IUCN status: LC, NE, NT, VU, EN, CR, EW (standard codes)
- Growth habit: "Arbol" (Tree), "Arbusto" (Shrub), "Palma" (Palm tree)

## Place Data Issues

- Over 500 different locations with special characters - keep as is.
- Sites include specific streets and neighborhoods within Ibagué - keep as is.

## Model Updates Needed

- Add gbif_id field to Species model.
- Add "Critical" value to PhytosanitaryStatus.
- No need to add "Sparse" to FoliageDensity (already exists).
- Move common_name from BiodiversityRecord to Species model (common_name is specific to species).

## Mapping Strategy

- Expand mappings for Spanish terms to English choices.
- Infer measurement units from field names:
  - volume_m3 → cubic meters
  - diameter_bh_cm → centimeters
  - density_g_cm3 → g/cm3
  - trunk_height, total height, crown_diameter → meters

## Import Order

1. Taxonomy data
2. Place data
3. Biodiversity records
4. Measurements and observations

The data structure is more complex than anticipated, with different naming conventions than our current models. We need to update our mappings and possibly models to accommodate these differences.
