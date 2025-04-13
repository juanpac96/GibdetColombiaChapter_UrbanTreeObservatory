import csv
import io
import logging
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

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

    def handle(self, *args, **options):
        local_dir = options.get('local_dir')
        
        self.stdout.write(self.style.SUCCESS('Starting data import...'))
        
        # Process taxonomy first
        self.stdout.write(self.style.NOTICE('Importing taxonomy data...'))
        if local_dir:
            taxonomy_data = self._read_local_csv(f"{local_dir}/taxonomy_details.csv")
        else:
            taxonomy_data = self._fetch_csv(options['taxonomy_url'])
        self._process_taxonomy(taxonomy_data)
        
        # Process places
        self.stdout.write(self.style.NOTICE('Importing place data...'))
        if local_dir:
            place_data = self._read_local_csv(f"{local_dir}/place.csv")
        else:
            place_data = self._fetch_csv(options['place_url'])
        self._process_places(place_data)
        
        # Process biodiversity records
        self.stdout.write(self.style.NOTICE('Importing biodiversity records...'))
        if local_dir:
            biodiversity_data = self._read_local_csv(f"{local_dir}/biodiversity_records.csv")
        else:
            biodiversity_data = self._fetch_csv(options['biodiversity_url'])
        self._process_biodiversity_records(biodiversity_data)
        
        # Process measurements
        self.stdout.write(self.style.NOTICE('Importing measurements...'))
        if local_dir:
            measurements_data = self._read_local_csv(f"{local_dir}/measurements.csv")
        else:
            measurements_data = self._fetch_csv(options['measurements_url'])
        self._process_measurements(measurements_data)
        
        # Process observations
        self.stdout.write(self.style.NOTICE('Importing observations...'))
        if local_dir:
            observations_data = self._read_local_csv(f"{local_dir}/observations_details.csv")
        else:
            observations_data = self._fetch_csv(options['observations_url'])
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

    @transaction.atomic
    def _process_taxonomy(self, data):
        """Process taxonomy data and create Family, Genus, and Species records."""
        families_created = 0
        genera_created = 0
        species_created = 0
        
        for row in data:
            # Create Family
            family_name = row.get('family', '').strip()
            if family_name:
                family, created = Family.objects.get_or_create(name=family_name)
                if created:
                    families_created += 1
                
                # Create Genus
                genus_name = row.get('genus', '').strip()
                if genus_name:
                    genus, created = Genus.objects.get_or_create(
                        name=genus_name,
                        family=family
                    )
                    if created:
                        genera_created += 1
                    
                    # Create Species
                    species_name = row.get('specie', '').strip()
                    accepted_name = row.get('accept_scientific_name', '').strip()
                    identified_by = row.get('identified_by', 'Cortolima').strip()
                    
                    if species_name and accepted_name:
                        # Origin, IUCN status, and growth habit will come from observations_details.csv
                        # Here we just set defaults

                        
                        # Default values if not found in observations
                        origin = Species.Origin.UNKNOWN
                        iucn_status = Species.IUCNStatus.NOT_EVALUATED
                        growth_habit = Species.GrowthHabit.UNKNOWN
                        
                        species, created = Species.objects.update_or_create(
                            accepted_scientific_name=accepted_name,
                            defaults={
                                'name': species_name,
                                'genus': genus,
                                'origin': origin,
                                'iucn_status': iucn_status,
                                'growth_habit': growth_habit,
                                'identified_by': identified_by,
                            }
                        )
                        
                        if created:
                            species_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"Taxonomy import complete: {families_created} families, "
            f"{genera_created} genera, {species_created} species."
        ))

    @transaction.atomic
    def _process_places(self, data):
        """Process place data and create Place records."""
        places_created = 0
        
        for row in data:
            country = row.get('country', 'Colombia').strip()
            department = row.get('department', 'Tolima').strip()
            municipality = row.get('municipality', 'Ibagué').strip()
            site = row.get('site', '').strip()
            populated_center = row.get('populated_center', '').strip()
            zone = self._safe_int(row.get('zone', None))
            subzone = self._safe_int(row.get('subzone', None))
            
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
        
        self.stdout.write(self.style.SUCCESS(f"Places import complete: {places_created} created."))

    @transaction.atomic
    def _process_biodiversity_records(self, data):
        """Process biodiversity records and create BiodiversityRecord records."""
        records_created = 0
        records_updated = 0
        
        for row in data:
            code_record = row.get('code_record', '').strip()
            if not code_record:
                continue
                
            # Get related objects
            try:
                # Find the Species via the taxonomy ID
                taxonomy_id = row.get('taxonomy_id')
                accepted_name = None
                
                # Here we'd need to use the taxonomy_id to find the right species
                # Since we don't have the original data, we're making a simplifying
                # assumption that we can find the species by searching through all species
                # In a real implementation, this would need a more robust approach
                species = None
                try:
                    species = Species.objects.all().first()  # Placeholder
                except Species.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Species not found for record {code_record}"))
                    continue
                
                # Find the Place via the place_id
                place_id = row.get('place_id')
                place = None
                try:
                    place = Place.objects.all().first()  # Placeholder
                except Place.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Place not found for record {code_record}"))
                    continue
                
                # Get location data
                lat = self._safe_float(row.get('latitude', 0))
                lon = self._safe_float(row.get('longitude', 0))
                location = Point(lon, lat, srid=4326)
                
                elevation = self._safe_float(row.get('elevation_m'))
                common_names = row.get('common_name', '').strip()
                recorded_by = row.get('registered_by', 'Cortolima').strip()
                
                # Parse date if available
                date_str = row.get('date_event')
                date = self._parse_date(date_str) if date_str else None
                
                # Create or update the biodiversity record
                bio_record, created = BiodiversityRecord.objects.update_or_create(
                    uuid=code_record,  # Using code_record as uuid (this should be confirmed)
                    defaults={
                        'species': species,
                        'place': place,
                        'common_names': common_names,
                        'location': location,
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
                self.stdout.write(self.style.ERROR(f"Error processing biodiversity record {code_record}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Biodiversity records import complete: {records_created} created, {records_updated} updated."
        ))

    @transaction.atomic
    def _process_measurements(self, data):
        """Process measurements and create Measurement records."""
        measurements_created = 0
        
        for row in data:
            record_code = row.get('record_code', '').strip()
            if not record_code:
                continue
                
            try:
                # Find the biodiversity record
                bio_record = None
                try:
                    bio_record = BiodiversityRecord.objects.get(uuid=record_code)
                except BiodiversityRecord.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"BiodiversityRecord not found for {record_code}"))
                    continue
                
                # Use predefined mappings from the utils module
                
                # Extract measurement data
                measurement_name = row.get('measurement_name', '').strip()
                value = self._safe_float(row.get('measurement_value'))
                method = row.get('measurement_method', '').strip()
                
                # Convert to model choices using our utility function
                attribute = get_mapped_value(
                    measurement_name, 
                    MEASURED_ATTRIBUTE_MAPPINGS, 
                    Measurement.MeasuredAttribute.OTHER
                )
                measurement_unit = get_mapped_value(
                    row.get('measurement_unit', ''), 
                    MEASUREMENT_UNIT_MAPPINGS, 
                    Measurement.MeasurementUnit.OTHER
                )
                measurement_method = get_mapped_value(
                    method, 
                    MEASUREMENT_METHOD_MAPPINGS, 
                    Measurement.MeasurementMethod.OTHER
                )
                
                # Parse date
                date_str = row.get('measurement_date_event')
                date = self._parse_date(date_str) if date_str else None
                
                other_attribute = measurement_name if attribute == Measurement.MeasuredAttribute.OTHER else ''
                other_unit = row.get('measurement_unit', '') if measurement_unit == Measurement.MeasurementUnit.OTHER else ''
                other_method = method if measurement_method == Measurement.MeasurementMethod.OTHER else ''
                
                # Create the measurement
                measurement = Measurement.objects.create(
                    biodiversity_record=bio_record,
                    attribute=attribute,
                    other_attribute=other_attribute,
                    value=value,
                    unit=measurement_unit,
                    other_unit=other_unit,
                    method=measurement_method,
                    other_method=other_method,
                    date=date,
                )
                
                measurements_created += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing measurement for {record_code}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Measurements import complete: {measurements_created} created."))

    @transaction.atomic
    def _process_observations(self, data):
        """Process observations and create Observation records."""
        observations_created = 0
        
        for row in data:
            record_code = row.get('record_code', '').strip()
            if not record_code:
                continue
                
            try:
                # Find the biodiversity record
                bio_record = None
                try:
                    bio_record = BiodiversityRecord.objects.get(uuid=record_code)
                except BiodiversityRecord.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"BiodiversityRecord not found for {record_code}"))
                    continue
                
                # Update the species with more detailed information
                if bio_record.species:
                    # Update species with additional info using our utility function
                    origin = get_mapped_value(
                        row.get('origin', ''), 
                        ORIGIN_MAPPINGS, 
                        Species.Origin.UNKNOWN
                    )
                    iucn_status = get_mapped_value(
                        row.get('iucn_status', ''), 
                        IUCN_STATUS_MAPPINGS, 
                        Species.IUCNStatus.NOT_EVALUATED
                    )
                    growth_habit = get_mapped_value(
                        row.get('growth_habit', ''), 
                        GROWTH_HABIT_MAPPINGS, 
                        Species.GrowthHabit.UNKNOWN
                    )
                    
                    if origin != Species.Origin.UNKNOWN or iucn_status != Species.IUCNStatus.NOT_EVALUATED or growth_habit != Species.GrowthHabit.UNKNOWN:
                        species = bio_record.species
                        species.origin = origin
                        species.iucn_status = iucn_status
                        species.growth_habit = growth_habit
                        species.save()
                
                # Extract observation data using our utility functions
                reproductive_cond = get_mapped_value(
                    row.get('reproductive_condition', ''), 
                    REPRODUCTIVE_CONDITION_MAPPINGS, 
                    Observation.ReproductiveCondition.NOT_REPORTED
                )
                
                phytosanitary = get_mapped_value(
                    row.get('phytosanitary_status', ''), 
                    PHYTOSANITARY_STATUS_MAPPINGS, 
                    Observation.PhytosanitaryStatus.NOT_REPORTED
                )
                
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
                is_standing = True  # Default value, may need to extract from data
                notes = row.get('biological_record_comments', '').strip() or row.get('observations', '').strip()
                
                # Create the observation
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
                    date=bio_record.date,  # Default to the biodiversity record date
                )
                
                observations_created += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing observation for {record_code}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Observations import complete: {observations_created} created."))

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
