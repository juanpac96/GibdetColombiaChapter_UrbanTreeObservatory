#!/usr/bin/env python3
"""
Data exploration script for Urban Tree Observatory CSV files.

This script analyzes CSV files from the Urban Tree Observatory dataset 
and extracts unique values for fields that map to TextChoices in Django models.
It generates both a text report and an HTML report for easy reference.

Usage:
    python scripts/explore_csv_data.py --data-dir=/path/to/csv/files

Output:
    - csv_exploration_report.txt: Plain text report with unique values
    - csv_exploration_report.html: HTML report with more detailed information
"""

import os
import csv
import argparse
import json
from collections import defaultdict, Counter
import datetime


# Fields that map to TextChoices in Django models
TEXT_CHOICE_FIELDS = {
    "taxonomy_details.csv": ["origin", "iucn_status", "growth_habit"],
    "biodiversity_records.csv": [],
    "measurements.csv": ["measurement_name", "measurement_unit", "measurement_method"],
    "observations_details.csv": [
        "reproductive_condition", "phytosanitary_status", "physical_condition",
        "foliage_density", "aesthetic_value", "growth_phase", "origin", 
        "iucn_status", "growth_habit"
    ],
    "place.csv": []
}

# Other interesting fields to analyze
ADDITIONAL_FIELDS = {
    "taxonomy_details.csv": ["family", "genus", "specie", "accept_scientific_name", "identified_by"],
    "biodiversity_records.csv": ["common_name", "registered_by"],
    "measurements.csv": [],
    "observations_details.csv": ["accompanying_collectors"],
    "place.csv": ["country", "department", "municipality", "populated_center", "site"]
}

def read_csv(file_path):
    """Read a CSV file and return its contents as a list of dictionaries."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def extract_unique_values(data, fields):
    """Extract unique values for specified fields in the data."""
    result = {}
    for field in fields:
        values = [row.get(field, '').strip() for row in data if row.get(field)]
        # Remove empty values
        values = [v for v in values if v]
        # Count occurrences of each value
        value_counts = Counter(values)
        # Sort by frequency (most common first)
        sorted_values = sorted(value_counts.items(), key=lambda x: (-x[1], x[0]))
        result[field] = sorted_values
    return result

def analyze_data_types(data, fields):
    """Analyze potential data types of fields."""
    result = {}
    for field in fields:
        values = [row.get(field, '').strip() for row in data if row.get(field)]
        # Remove empty values
        values = [v for v in values if v]
        
        # Sample up to 100 values
        sample = values[:100]
        
        # Check if values look like numbers
        numeric = all(v.replace('.', '', 1).isdigit() for v in sample if v and v.count('.') <= 1)
        
        # Check if values look like dates (simple check)
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        dates = False
        for date_format in date_formats:
            try:
                if sample and all(
                    datetime.datetime.strptime(v, date_format) for v in sample if v
                ):
                    dates = True
                    break
            except ValueError:
                continue
        
        # Determine likely type
        if numeric:
            data_type = "numeric"
        elif dates:
            data_type = "date"
        else:
            data_type = "text"
        
        result[field] = data_type
    return result

def generate_text_report(analysis_results, column_lists, output_file):
    """Generate a plain text report from the analysis results."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Urban Tree Observatory Data Exploration Report\n")
        f.write("=" * 50 + "\n\n")
        
        # First, list all files and their columns
        f.write("CSV Files and Their Columns\n")
        f.write("=" * 30 + "\n\n")
        
        for csv_file, columns in column_lists.items():
            f.write(f"File: {csv_file}\n")
            f.write("-" * 30 + "\n")
            f.write(f"  Total columns: {len(columns)}\n")
            f.write("  Column list:\n")
            for col in columns:
                f.write(f"    - {col}\n")
            f.write("\n")
        
        f.write("\n" + "=" * 50 + "\n\n")
        
        # Then, the unique values analysis
        f.write("Field Value Analysis\n")
        f.write("=" * 30 + "\n\n")
        
        for csv_file, field_values in analysis_results.items():
            f.write(f"File: {csv_file}\n")
            f.write("-" * 30 + "\n\n")
            
            for field, values in field_values.items():
                f.write(f"  Field: {field}\n")
                for value, count in values:
                    f.write(f"    - '{value}' ({count} occurrences)\n")
                f.write("\n")
            
            f.write("\n")

def generate_html_report(analysis_results, data_types, row_counts, column_lists, output_file):
    """Generate an HTML report from the analysis results."""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Urban Tree Observatory Data Exploration Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #2980b9;
                margin-top: 30px;
            }
            h3 {
                color: #16a085;
            }
            .file-section {
                margin-bottom: 40px;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .field-section {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .value-count {
                color: #7f8c8d;
                font-size: 0.9em;
            }
            .data-type {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 0.8em;
                margin-left: 10px;
            }
            .type-text {
                background-color: #e74c3c;
                color: white;
            }
            .type-numeric {
                background-color: #3498db;
                color: white;
            }
            .type-date {
                background-color: #2ecc71;
                color: white;
            }
            .summary {
                margin-bottom: 30px;
                padding: 15px;
                background-color: #e8f4f8;
                border-radius: 5px;
            }
            .columns-section {
                margin-bottom: 20px;
            }
            .columns-table {
                max-width: 800px;
            }
            .tag {
                display: inline-block;
                padding: 2px 6px;
                margin: 2px;
                border-radius: 3px;
                background-color: #f39c12;
                color: white;
                font-size: 0.8em;
            }
            .nav-tabs {
                display: flex;
                margin-bottom: 20px;
                border-bottom: 1px solid #ddd;
                padding-left: 0;
                list-style: none;
            }
            .nav-tabs li {
                margin-bottom: -1px;
            }
            .nav-tabs a {
                display: block;
                padding: 10px 15px;
                margin-right: 2px;
                text-decoration: none;
                color: #555;
                border: 1px solid transparent;
                border-radius: 4px 4px 0 0;
            }
            .nav-tabs a:hover {
                border-color: #eee #eee #ddd;
                background-color: #f5f5f5;
            }
            .nav-tabs .active a {
                color: #555;
                background-color: #fff;
                border: 1px solid #ddd;
                border-bottom-color: transparent;
            }
        </style>
        <script>
            function showTab(tabId) {
                // Hide all tabs
                const tabs = document.querySelectorAll('.tab-content');
                tabs.forEach(tab => tab.style.display = 'none');
                
                // Remove active class from all tab links
                const tabLinks = document.querySelectorAll('.nav-tabs a');
                tabLinks.forEach(link => link.parentElement.classList.remove('active'));
                
                // Show the selected tab
                document.getElementById(tabId).style.display = 'block';
                
                // Add active class to selected tab link
                document.querySelector(`[href="#${tabId}"]`).parentElement.classList.add('active');
                
                // Save active tab to localStorage
                localStorage.setItem('activeTab', tabId);
                
                return false;
            }
            
            window.onload = function() {
                // Restore active tab from localStorage or default to first tab
                const activeTab = localStorage.getItem('activeTab') || 'summary-tab';
                showTab(activeTab);
            }
        </script>
    </head>
    <body>
        <h1>Urban Tree Observatory Data Exploration Report</h1>
        
        <ul class="nav-tabs">
            <li><a href="#summary-tab" onclick="return showTab('summary-tab')">Summary</a></li>
            <li><a href="#columns-tab" onclick="return showTab('columns-tab')">Columns</a></li>
            <li><a href="#values-tab" onclick="return showTab('values-tab')">Field Values</a></li>
        </ul>
        
        <div id="summary-tab" class="tab-content summary">
            <h2>Dataset Summary</h2>
    """
    
    # Add summary information
    html += "<table>"
    html += "<tr><th>CSV File</th><th>Row Count</th><th>Column Count</th></tr>"
    for csv_file, count in row_counts.items():
        column_count = len(column_lists.get(csv_file, []))
        html += f"<tr><td>{csv_file}</td><td>{count}</td><td>{column_count}</td></tr>"
    html += "</table>"
    html += "</div>"
    
    # Add columns section
    html += '<div id="columns-tab" class="tab-content columns-section">'
    html += '<h2>CSV File Columns</h2>'
    
    for csv_file, columns in column_lists.items():
        html += f'<div class="file-section">'
        html += f'<h3>File: {csv_file} ({len(columns)} columns)</h3>'
        
        html += '<table class="columns-table">'
        html += '<tr><th>#</th><th>Column Name</th><th>Data Type</th><th>Field Type</th></tr>'
        
        for i, column in enumerate(columns):
            # Determine data type
            data_type = data_types.get(csv_file, {}).get(column, "unknown")
            type_class = f"type-{data_type}"
            
            # Determine field type
            field_type = "Regular Field"
            if column in TEXT_CHOICE_FIELDS.get(csv_file, []):
                field_type = '<span class="tag">TextChoice</span>'
            elif column in ADDITIONAL_FIELDS.get(csv_file, []):
                field_type = '<span class="tag">Analyzed</span>'
            
            html += f'<tr><td>{i+1}</td><td>{column}</td><td><span class="data-type {type_class}">{data_type}</span></td><td>{field_type}</td></tr>'
        
        html += '</table>'
        html += '</div>'
    
    html += '</div>'
    
    # Add values section
    html += '<div id="values-tab" class="tab-content">'
    html += '<h2>Field Value Analysis</h2>'
    
    # Add detailed information for each file
    for csv_file, field_values in analysis_results.items():
        html += f'<div class="file-section">'
        html += f'<h3>File: {csv_file}</h3>'
        
        for field, values in field_values.items():
            data_type = data_types.get(csv_file, {}).get(field, "unknown")
            type_class = f"type-{data_type}"
            
            # Determine field type
            field_type = ""
            if field in TEXT_CHOICE_FIELDS.get(csv_file, []):
                field_type = ' <span class="tag">TextChoice</span>'
            
            html += f'<div class="field-section">'
            html += f'<h3>Field: {field} <span class="data-type {type_class}">{data_type}</span>{field_type}</h3>'
            
            html += '<table>'
            html += '<tr><th>Value</th><th>Occurrences</th></tr>'
            
            for value, count in values:
                html += f'<tr><td>{value}</td><td>{count}</td></tr>'
            
            html += '</table>'
            html += '</div>'
        
        html += '</div>'
    
    html += '</div>'  # Close values-tab
    
    html += """
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def get_csv_columns(file_path):
    """Get the column names from a CSV file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            return header
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading header from {file_path}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Explore CSV data for the Urban Tree Observatory project.')
    parser.add_argument('--data-dir', required=True, help='Directory containing CSV files')
    parser.add_argument('--output-dir', default='scripts/data', help='Directory for output reports')
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    analysis_results = {}
    data_types_results = {}
    row_counts = {}
    column_lists = {}
    
    # Process each CSV file
    for csv_file in TEXT_CHOICE_FIELDS.keys():
        file_path = os.path.join(args.data_dir, csv_file)
        print(f"Processing {file_path}...")
        
        # Get column names
        columns = get_csv_columns(file_path)
        column_lists[csv_file] = columns
        
        data = read_csv(file_path)
        row_counts[csv_file] = len(data)
        
        if data:
            # Get field data types for ALL columns
            all_columns_data_types = analyze_data_types(data, columns)
            data_types_results[csv_file] = all_columns_data_types
            
            # Analyze fields that map to TextChoices and additional fields
            choice_fields = TEXT_CHOICE_FIELDS[csv_file]
            additional_fields = ADDITIONAL_FIELDS[csv_file]
            all_analyzed_fields = choice_fields + additional_fields
            
            unique_values = extract_unique_values(data, all_analyzed_fields)
            analysis_results[csv_file] = unique_values
    
    # Generate reports
    text_report_path = os.path.join(args.output_dir, 'csv_exploration_report.txt')
    html_report_path = os.path.join(args.output_dir, 'csv_exploration_report.html')
    
    generate_text_report(analysis_results, column_lists, text_report_path)
    generate_html_report(analysis_results, data_types_results, row_counts, column_lists, html_report_path)
    
    print(f"Reports generated at:")
    print(f"  - {text_report_path}")
    print(f"  - {html_report_path}")
    
    # Also create a JSON mapping template that can be used to update the mappings
    mapping_template = {}
    for csv_file, fields in TEXT_CHOICE_FIELDS.items():
        for field in fields:
            if csv_file in analysis_results and field in analysis_results[csv_file]:
                values = [value for value, _ in analysis_results[csv_file][field]]
                if values:
                    field_name = f"{csv_file.split('.')[0]}_{field}".upper()
                    mapping_template[field_name] = {value: "" for value in values}
    
    mapping_template_path = os.path.join(args.output_dir, 'mapping_template.json')
    with open(mapping_template_path, 'w', encoding='utf-8') as f:
        json.dump(mapping_template, f, ensure_ascii=False, indent=2)
    
    print(f"  - {mapping_template_path}")

if __name__ == "__main__":
    main()
