# Core App

This Django app contains common functionality used across the Urban Tree Observatory project.

## Management Commands

### `import_data`

This command imports data from CSV files into the database. It handles importing taxonomy, places, biodiversity records, measurements, and observations.

#### Usage

```bash
# Using default URLs
python manage.py import_data

# Using custom URLs
python manage.py import_data \
  --taxonomy-url=https://example.com/taxonomy_details.csv \
  --place-url=https://example.com/place.csv \
  --biodiversity-url=https://example.com/biodiversity_records.csv \
  --measurements-url=https://example.com/measurements.csv \
  --observations-url=https://example.com/observations_details.csv

# Using local files in a directory
python manage.py import_data --local-dir=/path/to/csv/files
```

#### Data Flow

The import process follows this order:

1. Taxonomy data (creates Family, Genus, and Species records)
2. Place data (creates Place records)
3. Biodiversity records (creates BiodiversityRecord records)
4. Measurements (creates Measurement records linked to biodiversity records)
5. Observations (creates Observation records linked to biodiversity records and updates Species with additional details)

#### Required CSV Files

The command expects the following CSV files:

1. **taxonomy_details.csv** - Contains data about species taxonomy:
   - family: Plant family name
   - genus: Plant genus name
   - specie: Species name (without genus)
   - accept_scientific_name: Accepted scientific name
   - identified_by: Who identified the species
   - date_of_identification: Date when identification was made

2. **place.csv** - Contains data about places:
   - country: Country name
   - department: Department/state/province
   - municipality: City/town/municipality
   - populated_center: Populated center/neighborhood
   - site: Specific site name
   - zone: Zone number
   - subzone: Subzone number

3. **biodiversity_records.csv** - Contains data about biodiversity records:
   - code_record: Unique record identifier
   - common_name: Common name(s) of the species
   - latitude: Latitude coordinate
   - longitude: Longitude coordinate
   - elevation_m: Elevation in meters
   - registered_by: Name of the person who recorded the data
   - date_event: Date when the data was recorded
   - taxonomy_id: Reference to taxonomy_details
   - place_id: Reference to place
   - epsg_id: Coordinate reference system code

4. **measurements.csv** - Contains data about measurements:
   - measurement_name: Name of the measurement (e.g., "Altura total")
   - measurement_value: Numeric value of the measurement
   - measurement_method: Method used to take the measurement
   - measurement_date_event: Date when the measurement was taken
   - record_code: Reference to the biodiversity record

5. **observations_details.csv** - Contains data about observations:
   - record_code: Reference to the biodiversity record
   - biological_record_comments: General comments
   - reproductive_condition: Reproductive state (e.g., "Floración", "Fructificación")
   - observations: Additional observations
   - phytosanitary_status: Health status (e.g., "Sano", "Enfermo")
   - accompanying_collectors: People who helped with the collection
   - use: Reference URL for use
   - physical_condition: Physical state (e.g., "Bueno", "Regular")
   - foliage_density: Foliage density (e.g., "Denso", "Medio")
   - aesthetic_value: Aesthetic value (e.g., "Esencial", "Emblemático")
   - growth_phase: Growth phase (e.g., "F1", "F2", "F3")
   - origin: Origin (e.g., "Exótica", "Nativa")
   - iucn_status: IUCN conservation status
   - life_form: Growth habit (e.g., "Árbol", "Palmera")

#### Language Mapping

The command automatically maps Spanish terms in the CSV files to English choices in the Django models. For example:

- "Sano" → `PhytosanitaryStatus.HEALTHY`
- "Árbol" → `LifeForm.TREE`
- "Floración" → `ReproductiveCondition.FLOWERING`

These mappings are defined in `apps/core/utils/mappings.py` and can be extended as needed.

#### Error Handling

The import process:

- Uses transactions to ensure data integrity
- Logs errors for individual records without stopping the entire import
- Provides summary statistics upon completion
- Handles cases where references between records might not be found

#### Extending for New Data

If the CSV formats change or new fields are added:

1. Update the appropriate mapping dictionaries in `apps/core/utils/mappings.py`
2. Modify the corresponding processing methods in the command file
3. Test with a small dataset before running on the full dataset
