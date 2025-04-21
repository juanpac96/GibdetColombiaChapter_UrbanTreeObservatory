# Data Exploration Script

The `explore_csv_data.py` script analyzes CSV files to identify unique values for fields that map to TextChoices in Django models, helping you understand your data before importing it.

```bash
python scripts/explore_csv_data.py --data-dir=/path/to/csv/files [--output-dir=./reports]
```

**Output:**

- `csv_exploration_report.txt`: A plain text report with unique values.
- `csv_exploration_report.html`: An HTML report with more detailed information, including data types and value frequencies.
- `mapping_template.json`: A JSON template that can be edited to define mappings for TextChoices.
