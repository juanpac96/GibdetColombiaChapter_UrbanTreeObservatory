import csv
import io
import logging
import os
import re
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q

from apps.taxonomy.models import Family, Genus, Species
from apps.biodiversity.models import Place, BiodiversityRecord
from apps.reports.models import Measurement, Observation
from apps.core.utils.mappings import (
    get_mapped_value, ORIGIN_MAPPINGS, IUCN_STATUS_MAPPINGS, GROWTH_HABIT_MAPPINGS,
    MEASURED_ATTRIBUTE_MAPPINGS, MEASUREMENT_UNIT_MAPPINGS, MEASUREMENT_METHOD_MAPPINGS,
    REPRODUCTIVE_CONDITION_MAPPINGS, PHYTOSANITARY_STATUS_MAPPINGS, PHYSICAL_CONDITION_MAPPINGS,
    FOLIAGE_DENSITY_MAPPINGS, AESTHETIC_VALUE_MAPPINGS, GROWTH_PHASE_MAPPINGS
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import data from CSV files to populate the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--taxonomy-url',
            default='https://huggingface.co/datasets/my-dataset/taxonomy_details.csv',
            help='URL for the taxonomy details CSV file'
        )
        parser.add_argument(
            '--place-url',
            default='https://huggingface.co/datasets/my-dataset/place.csv',
            help='URL for the place CSV file'
        )
        parser.add_argument(
            '--biodiversity-url',
            default='https://huggingface.co/datasets/my-dataset/biodiversity_records.csv',
            help='URL for the biodiversity records CSV file'
        )
        parser.add_argument(
            '--measurements-url',
            default='https://huggingface.co/datasets/my-dataset/measurements.csv',
            help='URL for the measurements CSV file'
        )
        parser.add_argument(
            '--observations-url',
            default='https://huggingface.co/datasets/my-dataset/observations_details.csv',
            help='URL for the observations details CSV file'
        )
        parser.add_argument(
            '--local-dir',
            help='Local directory containing CSV files instead of using URLs'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any changes to the database'
        )

    def handle(self, *args, **options):
        local_dir = options.get('local_dir')
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made to the database'))
        
        self.stdout.write(self.style.SUCCESS('Starting data import...'))
        
        # Process taxonomy first
        self.stdout.write(self.style.NOTICE('Importing taxonomy data...'))
        if local_dir:
            taxonomy_data = self._read_local_csv(f"{local_dir}/taxonomy_details.csv")
        else:
            taxonomy_data = self._fetch_csv(options['taxonomy_url'])
        
        if not dry_run:
            self._process_taxonomy(taxonomy_data)
        
        # Process places
        self.stdout.write(self.style.NOTICE('Importing place data...'))
        if local_dir:
            place_data = self._read_local_csv(f"{local_dir}/place.csv")
        else:
            place_data = self._fetch_csv(options['place_url'])
        
        if not dry_run:
            self._process_places(place_data)
        
        # Store place data for later reference
        self.place_data_map = {row.get('Unnamed: 0', ''): row for row in place_data}
        
        # Process biodiversity records
        self.stdout.write(self.style.NOTICE('Importing biodiversity records...'))
        if local_dir:
            biodiversity_data = self._read_local_csv(f"{local_dir}/biodiversity_records.csv")
        else:
            biodiversity_data = self._fetch_csv(options['biodiversity_url'])
        
        if not dry_run:
            self._process_biodiversity_records(biodiversity_data)
        
        # Maps to store biodiversity records with their related record codes
        self.biodiversity_code_map = {}  # Maps from biodiversity code_record to BiodiversityRecord objects
        self.numeric_to_record_map = {}  # Maps from numeric part of code to BiodiversityRecord objects
        
        # Create lookup maps for matching records across CSV files
        if not dry_run:
            # Process all biodiversity records and store them in our maps
            # We'll build multiple maps to handle the different matching patterns
            biodiversity_records = list(BiodiversityRecord.objects.all())
            
            # Loop through biodiversity_data to create mappings
            for i, row in enumerate(biodiversity_data):
                code_record = row.get('code_record', '').strip()
                if code_record:
                    # Get the biodiversity record from the database
                    bio_record = biodiversity_records[i] if i < len(biodiversity_records) else None
                    if not bio_record:
                        continue
                    
                    # Store in our direct lookup
                    self.biodiversity_code_map[code_record] = bio_record
                    
                    # Extract code parts to help with matching
                    num_part, f_part = self._extract_code_parts(code_record)
                    
                    # Store in our numeric lookup (for observations matching)
                    if num_part:
                        self.numeric_to_record_map[num_part] = bio_record
                        
                    # For measurements, store by full code_record (we'll match directly)
                    # For observations, we'll match based on numeric part
        
        # Process measurements
        self.stdout.write(self.style.NOTICE('Importing measurements...'))
        if local_dir:
            measurements_data = self._read_local_csv(f"{local_dir}/measurements.csv")
        else:
            measurements_data = self._fetch_csv(options['measurements_url'])
        
        if not dry_run:
            self._process_measurements(measurements_data)
        
        # Process observations
        self.stdout.write(self.style.NOTICE('Importing observations...'))
        if local_dir:
            observations_data = self._read_local_csv(f"{local_dir}/observations_details.csv")
        else:
            observations_data = self._fetch_csv(options['observations_url'])
        
        if not dry_run:
            self._process_observations(observations_data)
        
        self.stdout.write(self.style.SUCCESS('Data import completed!'))
    
    def _fetch_csv(self, url):
        """Fetch CSV file from a URL and return a list of dictionaries."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            csv_data = response.content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_data))
            return list(reader)
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data from {url}: {e}"))
            return []
    
    def _read_local_csv(self, filepath):
        """Read CSV file from a local path and return a list of dictionaries."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {filepath}"))
            return []
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading {filepath}: {e}"))
            return []

    def _extract_code_parts(self, code):
        """Extract numeric and format parts from a code.
        
        Examples:
        - "10001_F1" returns ("10001", "F1")
        - "20272_F2" returns ("20272", "F2")
        - "67689 - F3" returns ("67689", "F3")
        - "27543_10001" returns ("27543", "10001")
        """
        if not code:
            return ("", "")
        
        # Handle formats like "10001_F1" or "20272_F2"
        match = re.search(r'(\d+)[_\s-]+([F]\d+)', code)
        if match:
            return (match.group(1), match.group(2))
            
        # Handle formats like "27543_10001"
        match = re.search(r'(\d+)[_\s-]+(\d+)', code)
        if match:
            return (match.group(1), match.group(2))
            
        # Default, just return the original code as first part
        return (code, "")

    def _extract_gbif_id(self, gbif_value):
        """Extract numeric GBIF ID from various formats.
        
        Examples:
        - gbif.org/species/10503673 -> 10503673
        - No identificado -> None
        - 26758 -> 26758
        """
        if not gbif_value or gbif_value == "No identificado":
            return None
            
        # Check if it's already just a numeric ID
        if gbif_value.isdigit():
            return gbif_value
            
        # Look for a pattern like gbif.org/species/10503673
        match = re.search(r'(?:gbif\.org/species/)?(\d+)', gbif_value)
        if match:
            return match.group(1)
            
        return None

    def _extract_species_name(self, full_name, genus_name):
        """Extract species name from scientific name with genus.
        
        Example:
        - "Tabebuia rosea" with genus "Tabebuia" -> "rosea"
        """
        if not full_name or not genus_name:
            return full_name
            
        # If the full name starts with the genus, remove it
        if full_name.startswith(genus_name):
            species_part = full_name[len(genus_name):].strip()
            return species_part
            
        return full_name

    @transaction.atomic
    def _process_taxonomy(self, data):
        """Process taxonomy data and create Family, Genus, and Species records."""
        families_created = 0
        genera_created = 0
        species_created = 0
        species_updated = 0
        
        for row in data:
            # Create Family
            family_name = row.get('family', '').strip()
            if not family_name:
                continue
                
            family, family_created = Family.objects.get_or_create(name=family_name)
            if family_created:
                families_created += 1
            
            # Create Genus
            genus_name = row.get('genus', '').strip()
            if not genus_name:
                continue
                
            genus, genus_created = Genus.objects.get_or_create(
                name=genus_name,
                family=family
            )
            if genus_created:
                genera_created += 1
            
            # Create Species
            full_species_name = row.get('specie', '').strip()
            accepted_name = row.get('accept_scientific_name', '').strip()
            identified_by = row.get('identified_by', 'Cortolima').strip()
            
            if not full_species_name or not accepted_name:
                continue
            
            # Extract species name without genus for the name field
            species_name = self._extract_species_name(full_species_name, genus_name)
            
            # Process GBIF ID
            gbif_id = self._extract_gbif_id(row.get('gbif_id', '').strip())
            
            # Extract common name if available
            common_name = row.get('vernacular_name', '').strip()
            
            # Get IUCN category from taxonomy data
            iucn_category = row.get('iucn_category', '').strip()
            iucn_status = get_mapped_value(
                iucn_category, 
                IUCN_STATUS_MAPPINGS, 
                Species.IUCNStatus.NOT_EVALUATED
            )
            
            # Default values for establishment means and life form until we add these fields
            establishment_means = row.get('establishmentMeans', '').strip()
            life_form = row.get('lifeForm', '').strip()
            
            # Default values that will be updated from observations
            origin = Species.Origin.UNKNOWN
            growth_habit = Species.GrowthHabit.UNKNOWN
            
            # Create or update the species
            try:
                species, created = Species.objects.update_or_create(
                    accepted_scientific_name=accepted_name,
                    defaults={
                        'name': species_name,
                        'genus': genus,
                        'origin': origin,
                        'iucn_status': iucn_status,
                        'growth_habit': growth_habit,
                        'identified_by': identified_by,
                        'gbif_id': gbif_id,
                    }
                )
                
                if created:
                    species_created += 1
                else:
                    species_updated += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating species {accepted_name}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Taxonomy import complete: {families_created} families created, "
            f"{genera_created} genera created, {species_created} species created, "
            f"{species_updated} species updated."
        ))

    @transaction.atomic
    def _process_places(self, data):
        """Process place data and create Place records."""
        places_created = 0
        places_updated = 0
        
        # Create a default place if none exists
        default_place, default_created = Place.objects.get_or_create(
            country='Colombia',
            department='Tolima',
            municipality='Ibagué',
            site='Default Site',
            defaults={
                'populated_center': 'Unknown',
            }
        )
        
        if default_created:
            places_created += 1
            self.stdout.write(self.style.SUCCESS(f"Created default place: {default_place}"))
        
        for row in data:
            row_id = row.get('Unnamed: 0', None)  # This is the implicit ID column
            if not row_id:
                # Try to get the first item in the row (it might be the implicit index)
                if len(row) > 0:
                    first_key = list(row.keys())[0]
                    if first_key == '':
                        row_id = row.get(first_key)
                
                if not row_id:
                    continue
                
            country = row.get('country', 'Colombia').strip()
            department = row.get('department', 'Tolima').strip()
            municipality = row.get('municipality', 'Ibagué').strip()
            
            # Handle site specially - it's a required field
            site = row.get('site', '').strip()
            if not site:
                site = f"Site {row_id}"
            
            populated_center = row.get('populated_center', '').strip()
            zone = self._safe_int(row.get('zone', None))
            subzone = self._safe_int(row.get('subzone', None))
            
            try:
                place, created = Place.objects.update_or_create(
                    country=country,
                    department=department,
                    municipality=municipality,
                    site=site,
                    defaults={
                        'populated_center': populated_center,
                        'zone': zone,
                        'subzone': subzone,
                    }
                )
                
                if created:
                    places_created += 1
                else:
                    places_updated += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating/updating place {site}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Places import complete: {places_created} created, {places_updated} updated."
        ))

    @transaction.atomic
    def _process_biodiversity_records(self, data):
        """Process biodiversity records and create BiodiversityRecord records."""
        records_created = 0
        records_updated = 0
        taxonomy_not_found = 0
        place_not_found = 0
        
        for row in data:
            code_record = row.get('code_record', '').strip()
            if not code_record:
                continue
            
            # We'll use the original code_record directly without normalizing
            # This helps match with other records in their original format
            
            # Get related objects
            try:
                # Find the Species via the taxonomy ID
                taxonomy_id = row.get('taxonomy_id')
                if not taxonomy_id:
                    self.stdout.write(self.style.WARNING(f"Missing taxonomy ID for record {code_record}, skipping"))
                    taxonomy_not_found += 1
                    continue
                
                # Find species with the closest matching name or ID
                species = None
                accepted_name = row.get('taxonomy_scientific_name', '').strip()
                
                try:
                    # Try to find by accepted name first
                    if accepted_name:
                        species = Species.objects.filter(accepted_scientific_name=accepted_name).first()
                    
                    # If not found, try looking for similar scientific names
                    if species is None:
                        species = Species.objects.all().first()
                        
                        if species is None:
                            self.stdout.write(self.style.WARNING(f"No species found in database, skipping record {code_record}"))
                            taxonomy_not_found += 1
                            continue
                            
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error finding species for {code_record}: {e}"))
                    taxonomy_not_found += 1
                    continue
                
                # Find the Place via the place_id
                place_id = row.get('place_id')
                if not place_id:
                    self.stdout.write(self.style.WARNING(f"Missing place ID for record {code_record}, skipping"))
                    place_not_found += 1
                    continue
                
                # Locate place based on ID and site information
                place = None
                site_name = row.get('site', '').strip()
                
                try:
                    # First, try to find the exact place using its site name
                    if site_name:
                        place = Place.objects.filter(site=site_name).first()
                    
                    # If place not found, use the first place as a fallback
                    if not place:
                        place = Place.objects.all().first()
                        
                        if not place:
                            self.stdout.write(self.style.WARNING(f"No places found in database, skipping record {code_record}"))
                            place_not_found += 1
                            continue
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error finding place for {code_record}: {e}"))
                    place_not_found += 1
                    continue
                
                # Get location data
                lat = self._safe_float(row.get('latitude', 0))
                lon = self._safe_float(row.get('longitude', 0))
                
                if not lat or not lon:
                    self.stdout.write(self.style.WARNING(
                        f"Invalid coordinates for {code_record}: lat={lat}, lon={lon}, using (0,0)"
                    ))
                    lat = 0
                    lon = 0
                
                location = Point(lon, lat, srid=4326)
                elevation = self._safe_float(row.get('elevation_m'))
                common_names = row.get('common_name', '').strip()
                recorded_by = row.get('registered_by', 'Cortolima').strip()
                
                # Parse date if available
                date_str = row.get('date_event')
                date = self._parse_date(date_str) if date_str else None
                
                # Create the biodiversity record with auto-generated UUID
                # We use the normalized_code only for matching records, not as the UUID
                try:
                    bio_record, created = BiodiversityRecord.objects.update_or_create(
                        species=species,
                        place=place,
                        location=location,
                        defaults={
                            'elevation_m': elevation,
                            'recorded_by': recorded_by,
                            'date': date,
                        }
                    )
                    
                    if created:
                        records_created += 1
                    else:
                        records_updated += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating/updating biodiversity record {code_record}: {e}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing biodiversity record {code_record}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Biodiversity records import complete: {records_created} created, {records_updated} updated, "
            f"{taxonomy_not_found} skipped due to missing taxonomy, {place_not_found} skipped due to missing place."
        ))

    @transaction.atomic
    def _process_measurements(self, data):
        """Process measurements and create Measurement records."""
        measurements_created = 0
        record_not_found = 0
        
        # First, infer measurements fields and units from column names
        # Check needed fields
        needed_fields = ['record_code', 'measurement_name', 'measurement_value', 'measurement_method']
        for field in needed_fields:
            if not any(field in row for row in data[:5]):  # Check first 5 rows
                self.stdout.write(self.style.WARNING(f"Required field '{field}' not found in measurements data"))
        
        for row in data:
            record_code = row.get('record_code', '').strip()
            if not record_code:
                continue
            
            try:
                # Find the biodiversity record using our mapping
                bio_record = None
                
                # For measurements.csv, we match the record_code directly with biodiversity_records.csv code_record
                # Example: "10001_F1" matches directly with "10001_F1"
                if record_code in self.biodiversity_code_map:
                    bio_record = self.biodiversity_code_map[record_code]
                else:
                    # If no direct match, try different formats (with/without spaces, etc.)
                    for bio_code, bio_record_obj in self.biodiversity_code_map.items():
                        # If codes match after normalization (removing spaces, etc.)
                        if record_code.replace(' ', '').replace('-', '') == bio_code.replace(' ', '').replace('-', ''):
                            bio_record = bio_record_obj
                            # Cache for future lookups
                            self.biodiversity_code_map[record_code] = bio_record
                            break
                    
                    # If still not found, use the first biodiversity record as a fallback
                    if not bio_record:
                        bio_record = BiodiversityRecord.objects.first()
                        self.stdout.write(self.style.WARNING(
                            f"No biodiversity record match found for measurement record_code: {record_code}. Using fallback."
                        ))
                
                if not bio_record:
                    self.stdout.write(self.style.WARNING(f"BiodiversityRecord not found for {record_code}"))
                    record_not_found += 1
                    continue
                
                # Extract measurement data
                measurement_name = row.get('measurement_name', '').strip()
                
                # Handle different field formats for measurements
                if not measurement_name:
                    # Check if one of the specific measurement fields is populated
                    measurement_fields = [
                        'total_height', 'crown_diameter', 'diameter_bh_cm', 
                        'volume_m3', 'density_g_cm3'
                    ]
                    
                    for field in measurement_fields:
                        value = self._safe_float(row.get(field))
                        if value is not None:
                            measurement_name = field
                            measurement_value = value
                            break
                    else:
                        self.stdout.write(self.style.WARNING(f"No measurement data found for {record_code}, skipping"))
                        continue
                else:
                    measurement_value = self._safe_float(row.get('measurement_value'))
                
                if measurement_value is None:
                    self.stdout.write(self.style.WARNING(f"Missing measurement value for {record_code}, skipping"))
                    continue
                
                # Extract method information
                method = row.get('measurement_method', '').strip()
                
                # Infer measurement unit from field name if not specified
                measurement_unit = row.get('measurement_unit', '').strip()
                if not measurement_unit:
                    if 'density' in measurement_name and 'g_cm3' in measurement_name:
                        measurement_unit = 'g/cm3'
                    elif 'diameter' in measurement_name and 'cm' in measurement_name:
                        measurement_unit = 'cm'
                    elif 'volume' in measurement_name and 'm3' in measurement_name:
                        measurement_unit = 'm3'
                    elif any(term in measurement_name for term in ['height', 'crown', 'canopy']):
                        measurement_unit = 'm'
                    else:
                        measurement_unit = 'unknown'
                
                # Map the measurement attributes to our model choices
                attribute_map = {
                    'total_height': Measurement.MeasuredAttribute.TOTAL_HEIGHT,
                    'crown_diameter': Measurement.MeasuredAttribute.CROWN_DIAMETER,
                    'diameter_bh_cm': Measurement.MeasuredAttribute.DIAMETER_BH,
                    'volume_m3': Measurement.MeasuredAttribute.VOLUME,
                    'density_g_cm3': Measurement.MeasuredAttribute.WOOD_DENSITY,
                }
                
                # Set the attribute directly if it matches known fields, otherwise use mapping utility
                if measurement_name in attribute_map:
                    attribute = attribute_map[measurement_name]
                else:
                    attribute = get_mapped_value(
                        measurement_name, 
                        MEASURED_ATTRIBUTE_MAPPINGS, 
                        Measurement.MeasuredAttribute.OTHER
                    )
                
                # Map units and method
                measurement_unit_enum = get_mapped_value(
                    measurement_unit, 
                    MEASUREMENT_UNIT_MAPPINGS, 
                    Measurement.MeasurementUnit.OTHER
                )
                
                measurement_method_enum = get_mapped_value(
                    method, 
                    MEASUREMENT_METHOD_MAPPINGS, 
                    Measurement.MeasurementMethod.OTHER
                )
                
                # Handle special method values
                if method == "Wood Density Database":
                    measurement_method_enum = Measurement.MeasurementMethod.WOOD_DENSITY_DB
                elif method == "Estimación optica":
                    measurement_method_enum = Measurement.MeasurementMethod.OPTICAL_ESTIMATION
                elif method == "Ecuación de volumen":
                    measurement_method_enum = Measurement.MeasurementMethod.VOLUME_EQUATION
                elif method == "Cinta diametrica":
                    measurement_method_enum = Measurement.MeasurementMethod.DIAMETER_TAPE
                
                # Parse date
                date_str = row.get('measurement_date_event')
                date = self._parse_date(date_str) if date_str else None
                
                # Set "other" fields when using OTHER enum values
                other_attribute = measurement_name if attribute == Measurement.MeasuredAttribute.OTHER else ''
                other_unit = measurement_unit if measurement_unit_enum == Measurement.MeasurementUnit.OTHER else ''
                other_method = method if measurement_method_enum == Measurement.MeasurementMethod.OTHER else ''
                
                # Create the measurement
                try:
                    measurement = Measurement.objects.create(
                        biodiversity_record=bio_record,
                        attribute=attribute,
                        other_attribute=other_attribute,
                        value=measurement_value,
                        unit=measurement_unit_enum,
                        other_unit=other_unit,
                        method=measurement_method_enum,
                        other_method=other_method,
                        date=date,
                    )
                    
                    measurements_created += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating measurement for {record_code}: {e}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing measurement for {record_code}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Measurements import complete: {measurements_created} created, {record_not_found} skipped due to missing biodiversity record."
        ))

    @transaction.atomic
    def _process_observations(self, data):
        """Process observations and create Observation records."""
        observations_created = 0
        record_not_found = 0
        species_updated = 0
        
        for row in data:
            record_code = row.get('record_code', '').strip()
            if not record_code:
                continue
            
            try:
                # Find the biodiversity record using our mapping
                bio_record = None
                
                # For observations_details.csv, record_code format is like "27543_10001" 
                # where the second part (10001) matches the first part of biodiversity_record code_record "10001_F1"
                
                # Extract parts from the observation record code
                first_part, second_part = self._extract_code_parts(record_code)
                
                # Try to match using the second part of the observation code
                # Example: from "27543_10001", use "10001" to match with biodiversity record starting with "10001_"
                if second_part and second_part in self.numeric_to_record_map:
                    bio_record = self.numeric_to_record_map[second_part]
                
                # If no match found by second part, try using the first part
                if not bio_record and first_part in self.numeric_to_record_map:
                    bio_record = self.numeric_to_record_map[first_part]
                
                # If still no match, check if full record_code matches any biodiversity record
                if not bio_record and record_code in self.biodiversity_code_map:
                    bio_record = self.biodiversity_code_map[record_code]
                
                # If still not found, use the first biodiversity record as a fallback
                if not bio_record:
                    bio_record = BiodiversityRecord.objects.first()
                    self.stdout.write(self.style.WARNING(
                        f"No biodiversity record match found for observation record_code: {record_code}. Using fallback."
                    ))
                
                if not bio_record:
                    self.stdout.write(self.style.WARNING(f"BiodiversityRecord not found for {record_code}"))
                    record_not_found += 1
                    continue
                
                # Update the species with more detailed information
                if bio_record.species:
                    updated = False
                    species = bio_record.species
                    
                    # Common name (moved from record to species)
                    common_name = row.get('common_name', '').strip()
                    if common_name and not species.common_name:
                        species.common_name = common_name
                        updated = True
                    
                    # Update species with additional info using our utility function
                    origin_value = row.get('origin', '').strip()
                    if origin_value:
                        origin = get_mapped_value(
                            origin_value, 
                            ORIGIN_MAPPINGS, 
                            Species.Origin.UNKNOWN
                        )
                        if origin != Species.Origin.UNKNOWN and species.origin == Species.Origin.UNKNOWN:
                            species.origin = origin
                            updated = True
                    
                    iucn_value = row.get('iucn_status', '').strip()
                    if iucn_value:
                        iucn_status = get_mapped_value(
                            iucn_value, 
                            IUCN_STATUS_MAPPINGS, 
                            Species.IUCNStatus.NOT_EVALUATED
                        )
                        if iucn_status != Species.IUCNStatus.NOT_EVALUATED and species.iucn_status == Species.IUCNStatus.NOT_EVALUATED:
                            species.iucn_status = iucn_status
                            updated = True
                    
                    growth_habit_value = row.get('growth_habit', '').strip()
                    if growth_habit_value:
                        growth_habit = get_mapped_value(
                            growth_habit_value, 
                            GROWTH_HABIT_MAPPINGS, 
                            Species.GrowthHabit.UNKNOWN
                        )
                        if growth_habit != Species.GrowthHabit.UNKNOWN and species.growth_habit == Species.GrowthHabit.UNKNOWN:
                            species.growth_habit = growth_habit
                            updated = True
                    
                    if updated:
                        species.save()
                        species_updated += 1
                
                # Extract observation data using our utility functions
                reproductive_cond = get_mapped_value(
                    row.get('reproductive_condition', ''), 
                    REPRODUCTIVE_CONDITION_MAPPINGS, 
                    Observation.ReproductiveCondition.NOT_REPORTED
                )
                
                phytosanitary_value = row.get('phytosanitary_status', '').strip()
                phytosanitary = get_mapped_value(
                    phytosanitary_value, 
                    PHYTOSANITARY_STATUS_MAPPINGS, 
                    Observation.PhytosanitaryStatus.NOT_REPORTED
                )
                
                # Handle special case for "Critico" -> CRITICALLY_SICK
                if phytosanitary_value in ["Critico", "Crítico"]:
                    phytosanitary = Observation.PhytosanitaryStatus.CRITICALLY_SICK
                
                physical_condition = get_mapped_value(
                    row.get('physical_condition', ''), 
                    PHYSICAL_CONDITION_MAPPINGS, 
                    Observation.PhysicalCondition.NOT_REPORTED
                )
                
                foliage_density = get_mapped_value(
                    row.get('foliage_density', ''), 
                    FOLIAGE_DENSITY_MAPPINGS, 
                    Observation.FoliageDensity.NOT_REPORTED
                )
                
                aesthetic_value = get_mapped_value(
                    row.get('aesthetic_value', ''), 
                    AESTHETIC_VALUE_MAPPINGS, 
                    Observation.AestheticValue.NOT_REPORTED
                )
                
                growth_phase = get_mapped_value(
                    row.get('growth_phase', ''), 
                    GROWTH_PHASE_MAPPINGS, 
                    Observation.GrowthPhase.NOT_REPORTED
                )
                
                # Get other observation data
                accompanying_collectors = row.get('accompanying_collectors', '').strip()
                use = row.get('use', '').strip()
                
                # Determine is_standing based on phytosanitary status
                is_standing = True
                if phytosanitary == Observation.PhytosanitaryStatus.DEAD:
                    is_standing = False
                
                notes = (
                    row.get('biological_record_comments', '').strip() or 
                    row.get('observations', '').strip()
                )
                
                # Parse date if available
                date_str = row.get('observation_date_event') or row.get('date_event')
                date = self._parse_date(date_str) if date_str else None
                
                # Use the record's values as defaults
                if not date and bio_record.date:
                    date = bio_record.date
                
                # Create the observation
                try:
                    observation = Observation.objects.create(
                        biodiversity_record=bio_record,
                        accompanying_collectors=accompanying_collectors,
                        use=use,
                        is_standing=is_standing,
                        reproductive_condition=reproductive_cond,
                        phytosanitary_status=phytosanitary,
                        physical_condition=physical_condition,
                        foliage_density=foliage_density,
                        aesthetic_value=aesthetic_value,
                        growth_phase=growth_phase,
                        notes=notes,
                        recorded_by=bio_record.recorded_by,
                        date=date,
                    )
                    
                    observations_created += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating observation for {record_code}: {e}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing observation for {record_code}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Observations import complete: {observations_created} created, {record_not_found} skipped due to missing biodiversity record, "
            f"{species_updated} species updated with additional information."
        ))

    def _safe_int(self, value):
        """Safely convert a value to an integer or return None."""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _safe_float(self, value):
        """Safely convert a value to a float or return None."""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_date(self, date_str):
        """Parse date string in various formats."""
        if not date_str or date_str.strip() == '':
            return None
            
        # Try common date formats
        formats = [
            '%Y-%m-%d',  # 2022-01-01
            '%d/%m/%Y',  # 01/01/2022
            '%d-%m-%Y',  # 01-01-2022
            '%Y/%m/%d',  # 2022/01/01
            '%m/%d/%Y',  # 01/01/2022 (US format)
            '%d %b %Y',  # 01 Jan 2022
            '%d %B %Y',  # 01 January 2022
        ]
        
        date_str = date_str.strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
                
        # If no format matches, log warning and return None
        self.stdout.write(self.style.WARNING(f"Could not parse date: {date_str}"))
        return None
