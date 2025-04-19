# CSV and Django Models Data Structure Overview

We have several CSV files that represent different aspects of the database to which the data will be imported. Below is a summary of the files and their contents:

* **taxonomy_details.csv** - Contains species taxonomy information
* **biodiversity_records.csv** - Contains individual tree records with location data
* **measurements.csv** - Contains measurements for each tree (height, diameter, etc.)
* **observations_details.csv** - Contains qualitative observations about each tree
* **place.csv** - Contains location hierarchy information
* **functional_groups_traits.csv** - Contains functional traits for species groups

## Model to CSV Mapping

### Taxonomy Models

* Family, Genus, and Species classes map to data in **taxonomy_details.csv**
* The CSV includes taxonomic information (family, genus, species) plus metadata like origin, IUCN category, etc.
* The `gbif_id` field is present in both the model and CSV

### BiodiversityRecord Model

* Maps to **biodiversity_records.csv**
* Contains location information, common name, and links to taxonomy and place
* The `code_record` in CSV is the primary key
* `taxonomy_id` links to Species model
* `place_id` links to Place model

### Place Model

* Maps to **place.csv**
* Contains hierarchical location information (country, department, municipality, populated center, zone, etc.)
* In the CSV, these are separate columns while in the model they're relationships

### Measurement Model

* Maps to **measurements.csv**
* Contains quantitative measurements of trees
* The model has defined choices for measurements (TH, HT, CD, DBH, VO, WD)
* These exact codes appear in the CSV's `measurement_name` field
* Methods and units also match between CSV and model choices

### Observation Model

* Maps to **observations_details.csv**
* Contains qualitative assessments of trees
* Many coded fields (like phytosanitary_status, physical_condition, etc.)
* The same codes appear in both the model and CSV (e.g., HE for healthy)
* Percentage damage fields use the same scale (0, 20, 40, 60, 80, 100)

### Functional Group and Traits

* Maps to **functional_groups_traits.csv**
* Contains species trait information organized by functional groups
* Links species to quantifiable traits like carbon sequestration, shade index, etc.

#### Mapping functional_groups_traits.csv to Django Models

##### CSV Structure

The CSV file **functional_groups_traits.csv** has flattened columns like:

* `pft_id` (functional group ID)
* `carbon_sequestration_min`
* `carbon_sequestration_max`
* `shade_index_min`
* `shade_index_max`
* `canopy_diameter_min`
* `canopy_diameter_max`
* `height_max_min`
* `height_max_max`
* `taxonomy_id` (links to species)

##### Django Model Structure

This maps to three interrelated models:

##### FunctionalGroup Model

* Identified by `group_id` which maps to the CSV's `pft_id`
* Serves as the container for grouping species with similar traits
* The `description` field isn't directly mapped from the CSV
* Connected to traits through the many-to-many relationship via `TraitValue`

##### Trait Model

* Defines the different types of measurable traits
* Has a `TraitType` enumeration with four options that correspond to column prefixes:
  * `CARBON` for "carbon sequestration index"
  * `SHADE` for "shade index"
  * `CANOPY` for "maximum diameter of canopy"
  * `HEIGHT` for "maximum total height"
* These traits need to be created as discrete rows, one for each trait type

##### TraitValue Model

* Junction table that connects `FunctionalGroup` to `Trait`
* Contains `min_value` and `max_value` fields that store the actual values
* For each trait (carbon sequestration, shade, etc.), there would be a row linking:
  * The functional group (from `pft_id`)
  * The specific trait type
  * The min value (e.g., `carbon_sequestration_min`)
  * The max value (e.g., `carbon_sequestration_max`)

##### Transformation Required

To normalize the flat CSV into these three models:

1. Extract unique `pft_id` values to create `FunctionalGroup` records
2. Create four `Trait` records for the trait types (one-time setup)
3. For each row in the CSV, create four `TraitValue` records:
   * One linking the functional group to the carbon sequestration trait with min/max values
   * One linking the functional group to the shade index trait with min/max values
   * One linking the functional group to the canopy diameter trait with min/max values
   * One linking the functional group to the height max trait with min/max values
4. Update `Species` records to link to the appropriate functional group using the `taxonomy_id` field

This normalization allows for more flexibility in the data model, as new trait types could be added without changing the schema, and trait values can be efficiently queried across functional groups.

## Key Relationship Points

* There's a 1:1 relationship between biodiversity records, measurements, and observations based on `record_code`
* Each biodiversity record belongs to a species and a place
* Species are organized into a taxonomic hierarchy
* Places follow a geographic hierarchy
* Functional groups categorize species based on similar traits
