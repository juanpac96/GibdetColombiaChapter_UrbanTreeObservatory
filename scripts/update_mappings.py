#!/usr/bin/env python3
"""
Script to update the mappings.py file with new mappings from a JSON file.

After running explore_csv_data.py and manually updating the mapping_template.json
with the correct Django model choices, this script will update the mappings.py
file with the new mappings.

Usage:
    python scripts/update_mappings.py --mappings-file=mapping_template.json

This script will:
1. Read the current mappings.py file
2. Parse the JSON file with the new mappings
3. Update the corresponding dictionaries in mappings.py
4. Write the updated mappings.py file
"""

import os
import re
import json
import argparse
from collections import defaultdict


def read_mappings_file(file_path):
    """Read the current mappings.py file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_mappings_content(content):
    """Parse the content of the mappings.py file to extract dictionaries."""
    # Find all dictionary definitions using regex
    pattern = r'(\w+)_MAPPINGS\s*=\s*\{([^}]*)\}'
    matches = re.findall(pattern, content, re.DOTALL)
    
    dictionaries = {}
    for name, dict_content in matches:
        dictionaries[name] = dict_content.strip()
    
    return dictionaries


def update_dictionary_content(original_content, new_mappings):
    """Update a dictionary content with new mappings."""
    # Parse the original dictionary content into key-value pairs
    original_pairs = {}
    lines = original_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Extract key and value using regex
        match = re.match(r"'([^']*)'\s*:\s*([^,]*),?", line)
        if match:
            key, value = match.groups()
            original_pairs[key] = value.strip()
    
    # Merge with new mappings
    updated_pairs = original_pairs.copy()
    updated_pairs.update(new_mappings)
    
    # Generate updated content
    updated_content = []
    for key, value in sorted(updated_pairs.items()):
        updated_content.append(f"    '{key}': {value},")
    
    return '\n'.join(updated_content)


def update_mappings_file(file_path, updated_dictionaries):
    """Update the mappings.py file with updated dictionaries."""
    content = read_mappings_file(file_path)
    
    for dict_name, dict_content in updated_dictionaries.items():
        # Replace the dictionary content
        pattern = f'({dict_name}_MAPPINGS\\s*=\\s*\\{{)([^}}]*)(\\}})'
        replacement = f'\\1\n{dict_content}\n\\3'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description='Update mappings.py with new mappings from a JSON file.')
    parser.add_argument('--mappings-file', required=True, help='JSON file with new mappings')
    parser.add_argument('--output-file', default='apps/core/utils/mappings.py', help='Path to mappings.py file')
    args = parser.parse_args()
    
    # Read and parse the current mappings.py file
    mappings_content = read_mappings_file(args.output_file)
    dictionaries = parse_mappings_content(mappings_content)
    
    # Read the JSON file with new mappings
    with open(args.mappings_file, 'r', encoding='utf-8') as f:
        new_mappings = json.load(f)
    
    # Map JSON keys to dictionary names
    mapping_dict_map = {
        'TAXONOMY_DETAILS_ORIGIN': 'ORIGIN',
        'TAXONOMY_DETAILS_IUCN_STATUS': 'IUCN_STATUS',
        'TAXONOMY_DETAILS_GROWTH_HABIT': 'GROWTH_HABIT',
        'MEASUREMENTS_MEASUREMENT_NAME': 'MEASURED_ATTRIBUTE',
        'MEASUREMENTS_MEASUREMENT_UNIT': 'MEASUREMENT_UNIT',
        'MEASUREMENTS_MEASUREMENT_METHOD': 'MEASUREMENT_METHOD',
        'OBSERVATIONS_DETAILS_REPRODUCTIVE_CONDITION': 'REPRODUCTIVE_CONDITION',
        'OBSERVATIONS_DETAILS_PHYTOSANITARY_STATUS': 'PHYTOSANITARY_STATUS',
        'OBSERVATIONS_DETAILS_PHYSICAL_CONDITION': 'PHYSICAL_CONDITION',
        'OBSERVATIONS_DETAILS_FOLIAGE_DENSITY': 'FOLIAGE_DENSITY',
        'OBSERVATIONS_DETAILS_AESTHETIC_VALUE': 'AESTHETIC_VALUE',
        'OBSERVATIONS_DETAILS_GROWTH_PHASE': 'GROWTH_PHASE',
        'OBSERVATIONS_DETAILS_ORIGIN': 'ORIGIN',
        'OBSERVATIONS_DETAILS_IUCN_STATUS': 'IUCN_STATUS',
        'OBSERVATIONS_DETAILS_GROWTH_HABIT': 'GROWTH_HABIT',
    }
    
    # Update dictionaries
    updated_dictionaries = {}
    for json_key, dict_name in mapping_dict_map.items():
        if json_key in new_mappings and dict_name in dictionaries:
            # Convert the JSON mappings to the format needed for the dictionary
            dict_mappings = {}
            for key, value in new_mappings[json_key].items():
                if value:  # Only include non-empty values
                    dict_mappings[key] = value
            
            # Update the dictionary content
            if dict_mappings:
                updated_content = update_dictionary_content(dictionaries[dict_name], dict_mappings)
                updated_dictionaries[dict_name] = updated_content
    
    # Update the mappings.py file
    if updated_dictionaries:
        update_mappings_file(args.output_file, updated_dictionaries)
        print(f"Updated mappings in {args.output_file}")
    else:
        print("No updates needed for mappings.py")


if __name__ == "__main__":
    main()
