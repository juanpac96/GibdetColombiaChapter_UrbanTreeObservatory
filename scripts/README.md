# Urban Tree Observatory Scripts

This directory contains utility scripts for the Urban Tree Observatory project.

## Data Exploration and Mapping Tools

### 1. `explore_csv_data.py`

This script analyzes CSV files to identify unique values for fields that map to TextChoices in Django models, helping you understand your data before importing it.

```bash
python scripts/explore_csv_data.pypython scripts/explore_csv_data.py --data-dir=/path/to/csv/files [--output-dir=./reports]
```

#### Output

- `csv_exploration_report.txt`: A plain text report with unique values.
- `csv_exploration_report.html`: An HTML report with more detailed information, including data types and value frequencies.
- `mapping_template.json`: A JSON template that can be edited to define mappings for TextChoices.

### 2. `update_mappings.py`

After running `explore_csv_data.py` and editing the generated `mapping_template.json` file, this script updates the mappings in the Django project.

```bash
python scripts/update_mappings.py --mappings-file=mapping_template.json [--output-file=apps/core/utils/mappings.py]
```

## Workflow for Updating Mappings

1. **Explore your data**:

   ```bash
   python scripts/explore_csv_data.py --data-dir=/path/to/csv/files
   ```

2. **Review the reports**:
   - Open `csv_exploration_report.html` in a browser to see detailed information about your data.
   - Look for unique values in fields that map to TextChoices.

3. **Update the mapping template**:
   - Edit `mapping_template.json` to specify the appropriate Django model choices for each value.
   - For example:

     ```json
     {
       "OBSERVATIONS_DETAILS_PHYTOSANITARY_STATUS": {
         "Sano": "Observation.PhytosanitaryStatus.HEALTHY",
         "Enfermo": "Observation.PhytosanitaryStatus.SICK",
         "Muerto": "Observation.PhytosanitaryStatus.DEAD"
       }
     }
     ```

4. **Update the mappings in your Django project**:

   ```bash
   python scripts/update_mappings.py --mappings-file=mapping_template.json
   ```

5. **Test the data import with the new mappings**:

   ```bash
   python manage.py import_data --local-dir=/path/to/csv/files
   ```

## Notes

- These scripts are designed to be run from the project root directory.
- The output files are not intended to be committed to version control.
- You may need to run these scripts multiple times as your data evolves.
