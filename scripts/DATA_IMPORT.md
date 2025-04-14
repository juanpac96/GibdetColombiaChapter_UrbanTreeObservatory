# Urban Tree Observatory Data Import Analysis

## Taxonomy Data Issues

### Missing Fields in CSV vs. Django Model

The taxonomy_details.csv has unexpected fields that need to be addressed:

| CSV Field | Issue | Action Required | Status |
|-----------|-------|-----------------|--------|
| **gbif_id** | Points to a resource on gbif.org (e.g., gbif.org/species/2977854) or contains "No identificado" | **ACTION:** Add a URL field to the Species model or store only the numeric ID and build the URL in a property method | **Done**  |
| **lifeForm** | New field not in current model | **ACTION:** Explore this data in the exploration script. Don't update models yet | **In Progress** |
| **establishmentMeans** | New field not in current model | **ACTION:** Explore this data in the exploration script. Don't update models yet | **In Progress** |
| **iucn_category** | Similar to existing field | **ACTION:** Map to existing field `iucn_status` (IUCNStatus enum) | **In Progress** |

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

UPDATED: The gbif_id field has been added to the Species model. The property method for generating the GBIF URL is also implemented. We will need to extract the numeric ID from the gbif_id field in the CSV and store it in the model.

Patterns for gbif_id: gbif.org/species/10503673 -- 10503673 is the ID we need to store.

#### GBIF ID Analysis

The following records do not follow the pattern and ought to be handled during the import process:

| GBIF ID Value    | Number of Occurrences |
|------------------|-----------------------|
| No identificado  | 99                    |
| 26758            | 1                     |
| 5235             | 1                     |
| 7914             | 1                     |

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

#### Record Code Patterns

| Value | Occurrences | Notes |
|-------|------------:|-------|
| 100285 - F3 | 1 | Common pattern with space-hyphen-space |
| 10028_F1 | 1 | Common pattern with underscore |
| 67689 - F3 | 2 | Only non-unique value in dataset |
| 1000_F1 | 1 | 4-digit code with underscore |

### Place ID Mapping

- Use "place_id" to find the related place in the place CSV.

### Latitude/Longitude Mapping

- Convert latitude/longitude fields to a Point object (epsg_id is "4326" in all instances, which matches our default system).

### Foreign Keys

- place_id maps to the unnamed first column in place CSV (index in original pandas dataframe).
  - We could use the site field for extra validation in the import script when mapping since it contains the site name (duplicated from the place CSV).

## Measurement Data Issues

### Field Names

Our model's TextChoices need to map to field names in the CSV:

- "total_height" → MeasuredAttribute.TOTAL_HEIGHT
- "crown_diameter" → Consider changing our model's "canopy_diameter" to "crown_diameter" (DONE)
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
- Phytosanitary status: "Sano" (Healthy), "Enfermo" (Sick), "Muerto" (Dead), "Critico" (Critical) - add "Critical" as a choice (DONE)
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

- Add gbif_id field to Species model. (DONE)
- Add "Critical" value to PhytosanitaryStatus. (DONE)
- Move common_name from BiodiversityRecord to Species model (common_name is specific to species). (DONE)

NOTE. These changes still require creating migrations and updating the database.

## Mapping Strategy for Spansih Terms and Import Strategy for Units

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

## Matching Logic

### File: measurements.csv

#### Field: record_code

10001_F1 MATCHES biodiversity_record code_record = 10001_F1
20272_F2 MATCHES biodiversity_record code_record = 20272_F2
67689 - F3  MATCHES biodiversity_record code_record = 67689 - F3

### File: observations_details.csv

#### Field: record_code in observations_details.csv

27543_10001 MATCHES biodiversity_record code_record = 10001_F1
34888_20272 MATCHES biodiversity_record code_record = 20272_F2
97133_67689 MATCHES biodiversity_record code_record = 67689 - F3

### File: biodiversity_records.csv

#### Field: code_record in biodiversity_records.csv

Examples:

10001_F1
33915_F2
67689 - F3

#### Field: place_id

place_id MATCHES first (unnamed) column in place.csv

## Import Run Notes

The fallback logic we implemented is causing issues.

  When processing measurements and observations, we look for matching biodiversity records using the record codes from the CSV files. However, our current matching logic isn't working correctly for many records, resulting in the fallback being used excessively.

  Here's the current fallback logic in our code:

  1. For measurements.csv:
    - We try to match record_code (like "10001_F1") directly with a biodiversity record's code_record
    - If no match is found, we try normalizing both codes (removing spaces/dashes) and compare again
    - If still no match, we use BiodiversityRecord.objects.first() as a fallback (using the first record found)
  2. For observations_details.csv:
    - We try to match using first or second part of record_code (like "27543_10001") with biodiversity record codes
    - If no match is found, we try the full code
    - If still no match, we use BiodiversityRecord.objects.first() as a fallback

  The problem is that our numeric part matching logic isn't working correctly. For example, with observation code "100489_33867", we're not correctly matching it to the corresponding biodiversity record.

  The fallback to the first biodiversity record is problematic because:

  1. It creates incorrect relationships (all unmatched records link to the same biodiversity record)
  2. It doesn't capture the true error (that we couldn't find a match)
  3. It might create duplicated or meaningless measurements/observations

  We should improve this by:

  1. Better understanding the pattern between observation codes and biodiversity codes
  2. Potentially making the fallback optional or disabled by default
  3. Providing more detailed logs about why matching failed
  4. Creating a more comprehensive mapping between record codes

  This high number of fallbacks suggests our record matching logic needs to be revisited to better handle the specific patterns in your data files.
  