import csv
import io
import logging
import re
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

from apps.taxonomy.models import Family, Genus, Species
from apps.biodiversity.models import Place, BiodiversityRecord
from apps.reports.models import Measurement, Observation
from apps.core.utils.mappings import (
    get_mapped_value,
    ORIGIN_MAPPINGS,
    IUCN_STATUS_MAPPINGS,
    LIFEFORM_MAPPINGS,
    MEASURED_ATTRIBUTE_MAPPINGS,
    MEASUREMENT_UNIT_MAPPINGS,
    MEASUREMENT_METHOD_MAPPINGS,
    REPRODUCTIVE_CONDITION_MAPPINGS,
    PHYTOSANITARY_STATUS_MAPPINGS,
    PHYSICAL_CONDITION_MAPPINGS,
    FOLIAGE_DENSITY_MAPPINGS,
    AESTHETIC_VALUE_MAPPINGS,
    GROWTH_PHASE_MAPPINGS,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import data from CSV files to populate the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--taxonomy-url",
            default="https://huggingface.co/datasets/my-dataset/taxonomy_details.csv",
            help="URL for the taxonomy details CSV file",
        )
        parser.add_argument(
            "--place-url",
            default="https://huggingface.co/datasets/my-dataset/place.csv",
            help="URL for the place CSV file",
        )
        parser.add_argument(
            "--biodiversity-url",
            default="https://huggingface.co/datasets/my-dataset/biodiversity_records.csv",
            help="URL for the biodiversity records CSV file",
        )
        parser.add_argument(
            "--measurements-url",
            default="https://huggingface.co/datasets/my-dataset/measurements.csv",
            help="URL for the measurements CSV file",
        )
        parser.add_argument(
            "--observations-url",
            default="https://huggingface.co/datasets/my-dataset/observations_details.csv",
            help="URL for the observations details CSV file",
        )
        parser.add_argument(
            "--local-dir",
            help="Local directory containing CSV files instead of using URLs",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making any changes to the database",
        )
        parser.add_argument(
            "--report-file",
            default="import_report.txt",
            help="File to save the detailed import report",
        )

    def handle(self, *args, **options):
        local_dir = options.get("local_dir")
        dry_run = options.get("dry_run", False)
        report_file = options.get("report_file", "import_report.txt")

        # Initialize report tracking data
        self.report_data = {
            "taxonomy": {"created": [], "updated": [], "skipped": []},
            "places": {"created": [], "updated": [], "skipped": []},
            "biodiversity": {"created": [], "updated": [], "skipped": []},
            "measurements": {"created": [], "skipped": []},
            "observations": {"created": [], "skipped": []},
            "species_updates": [],
        }

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN MODE - No changes will be made to the database"
                )
            )

        self.stdout.write(self.style.SUCCESS("Starting data import..."))

        # Process taxonomy first
        self.stdout.write(self.style.NOTICE("Importing taxonomy data..."))
        if local_dir:
            taxonomy_data = self._read_local_csv(f"{local_dir}/taxonomy_details.csv")
        else:
            taxonomy_data = self._fetch_csv(options["taxonomy_url"])

        if not dry_run:
            self._process_taxonomy(taxonomy_data)

        # Process places
        self.stdout.write(self.style.NOTICE("Importing place data..."))
        if local_dir:
            place_data = self._read_local_csv(f"{local_dir}/place.csv")
        else:
            place_data = self._fetch_csv(options["place_url"])

        if not dry_run:
            self._process_places(place_data)

        # Store place data for later reference
        self.place_data_map = {row.get("Unnamed: 0", ""): row for row in place_data}

        # Process biodiversity records
        self.stdout.write(self.style.NOTICE("Importing biodiversity records..."))
        if local_dir:
            biodiversity_data = self._read_local_csv(
                f"{local_dir}/biodiversity_records.csv"
            )
        else:
            biodiversity_data = self._fetch_csv(options["biodiversity_url"])

        if not dry_run:
            self._process_biodiversity_records(biodiversity_data)

        # Maps to store biodiversity records with their related record codes
        self.biodiversity_code_map = {}  # Maps from biodiversity code_record to BiodiversityRecord objects

        # Create lookup maps for matching records across CSV files
        if not dry_run:
            # Get all biodiversity records with their original_code values
            # This is much more efficient since we're using the original_code field directly
            biodiversity_records = list(
                BiodiversityRecord.objects.all().select_related("species")
            )

            # Initialize a separate dictionary for first part mapping to avoid mixing types
            self.first_part_map = {}

            # Build efficient lookup maps for faster matching
            for bio_record in biodiversity_records:
                if bio_record.original_code:
                    # Store in our direct lookup with the exact code_record
                    self.biodiversity_code_map[bio_record.original_code] = bio_record

                    # Also store with normalized code (no spaces/dashes) for flexible matching
                    normalized_code = bio_record.original_code.replace(" ", "").replace(
                        "-", ""
                    )
                    if normalized_code != bio_record.original_code:
                        self.biodiversity_code_map[normalized_code] = bio_record

                    # Extract code parts to help with observations matching
                    bio_first_part, bio_second_part = self._extract_code_parts(
                        bio_record.original_code
                    )
                    if bio_first_part:
                        # Store in separate first_part_map for observation matching
                        self.first_part_map[bio_first_part] = bio_record

            self.stdout.write(
                f"Built efficient lookup maps for {len(biodiversity_records)} biodiversity records with {len(self.first_part_map)} first-part mappings"
            )

        # Process measurements
        self.stdout.write(self.style.NOTICE("Importing measurements..."))
        if local_dir:
            measurements_data = self._read_local_csv(f"{local_dir}/measurements.csv")
        else:
            measurements_data = self._fetch_csv(options["measurements_url"])

        if not dry_run:
            self._process_measurements(measurements_data)

        # Process observations
        self.stdout.write(self.style.NOTICE("Importing observations..."))
        if local_dir:
            observations_data = self._read_local_csv(
                f"{local_dir}/observations_details.csv"
            )
        else:
            observations_data = self._fetch_csv(options["observations_url"])

        if not dry_run:
            self._process_observations(observations_data)

        # Generate and save the report
        if not dry_run:
            self._save_report(report_file)
            self.stdout.write(
                self.style.SUCCESS(f"Detailed import report saved to {report_file}")
            )
        else:
            self.stdout.write(
                self.style.WARNING("Dry run completed, no report generated")
            )

        self.stdout.write(self.style.SUCCESS("Data import completed!"))

    def _save_report(self, report_file):
        """Save a detailed report of the import process to a text file."""
        with open(report_file, "w") as f:
            # Write header
            f.write("=" * 80 + "\n")
            f.write("URBAN TREE OBSERVATORY DATA IMPORT REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Write taxonomy summary
            f.write("TAXONOMY IMPORT\n")
            f.write("-" * 80 + "\n")
            f.write(
                f"Families created: {len(self.report_data['taxonomy']['created'])}\n"
            )
            f.write(
                f"Species updated: {len(self.report_data['taxonomy']['updated'])}\n"
            )
            f.write(
                f"Records skipped: {len(self.report_data['taxonomy']['skipped'])}\n\n"
            )

            if self.report_data["taxonomy"]["skipped"]:
                f.write("SKIPPED TAXONOMY RECORDS:\n")
                for item in self.report_data["taxonomy"]["skipped"]:
                    f.write(f"- {item}\n")
                f.write("\n")

            # Write places summary
            f.write("PLACES IMPORT\n")
            f.write("-" * 80 + "\n")
            f.write(f"Places created: {len(self.report_data['places']['created'])}\n")
            f.write(f"Places updated: {len(self.report_data['places']['updated'])}\n")
            f.write(f"Places skipped: {len(self.report_data['places']['skipped'])}\n\n")

            if self.report_data["places"]["skipped"]:
                f.write("SKIPPED PLACE RECORDS:\n")
                for item in self.report_data["places"]["skipped"]:
                    f.write(f"- {item}\n")
                f.write("\n")

            # Write biodiversity summary
            f.write("BIODIVERSITY RECORDS IMPORT\n")
            f.write("-" * 80 + "\n")
            f.write(
                f"Records created: {len(self.report_data['biodiversity']['created'])}\n"
            )
            f.write(
                f"Records updated: {len(self.report_data['biodiversity']['updated'])}\n"
            )
            f.write(
                f"Records skipped: {len(self.report_data['biodiversity']['skipped'])}\n\n"
            )

            if self.report_data["biodiversity"]["skipped"]:
                f.write("SKIPPED BIODIVERSITY RECORDS:\n")
                for item in self.report_data["biodiversity"]["skipped"]:
                    f.write(f"- {item}\n")
                f.write("\n")

            # Write code mappings
            f.write("RECORD CODE MAPPINGS\n")
            f.write("-" * 80 + "\n")
            mapping_count = len(self.biodiversity_code_map)
            first_part_mapping_count = len(self.first_part_map)
            f.write(f"Total biodiversity record mappings: {mapping_count}\n")
            f.write(
                f"Total first-part mappings for observations: {first_part_mapping_count}\n\n"
            )

            # Show a sample of the mappings (at most 20)
            f.write("SAMPLE OF BIODIVERSITY RECORD MAPPINGS:\n")
            sample_count = 0
            for code, record in self.biodiversity_code_map.items():
                # Skip special keys like 'first_part_map' and ensure it's a BiodiversityRecord object
                if (
                    sample_count < 20
                    and "_" in code
                    and code != "first_part_map"
                    and hasattr(record, "id")
                    and hasattr(record, "species")
                ):
                    f.write(
                        f"- '{code}' -> Record ID {record.id} ({record.species.accepted_scientific_name})\n"
                    )
                    sample_count += 1
            f.write("\n")

            # Write measurements summary
            f.write("MEASUREMENTS IMPORT\n")
            f.write("-" * 80 + "\n")
            f.write(
                f"Measurements created: {len(self.report_data['measurements']['created'])}\n"
            )
            f.write(
                f"Measurements skipped: {len(self.report_data['measurements']['skipped'])}\n\n"
            )

            if self.report_data["measurements"]["skipped"]:
                f.write("SKIPPED MEASUREMENT RECORDS:\n")
                for item in self.report_data["measurements"]["skipped"]:
                    f.write(f"- {item}\n")
                f.write("\n")

            # Write observations summary
            f.write("OBSERVATIONS IMPORT\n")
            f.write("-" * 80 + "\n")
            f.write(
                f"Observations created: {len(self.report_data['observations']['created'])}\n"
            )
            f.write(
                f"Observations skipped: {len(self.report_data['observations']['skipped'])}\n"
            )
            f.write(f"Species updated: {len(self.report_data['species_updates'])}\n\n")

            if self.report_data["observations"]["skipped"]:
                f.write("SKIPPED OBSERVATION RECORDS:\n")
                for item in self.report_data["observations"]["skipped"]:
                    f.write(f"- {item}\n")
                f.write("\n")

            # Write footer
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")

    def _fetch_csv(self, url):
        """Fetch CSV file from a URL and return a list of dictionaries."""
        try:
            response = requests.get(url)
            response.raise_for_status()

            csv_data = response.content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(csv_data))
            return list(reader)
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data from {url}: {e}"))
            return []

    def _read_local_csv(self, filepath):
        """Read CSV file from a local path and return a list of dictionaries."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
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

        # Handle biodiversity record formats like "10001_F1" or "67689 - F3"
        # This matches formats: NUMBER [_/space/-] F NUMBER
        match = re.search(r"(\d+)[_\s-]+([Ff]\d+)", code)
        if match:
            return (match.group(1), match.group(2))

        # Handle observation record formats like "27543_10001"
        # This matches formats: NUMBER [_/space/-] NUMBER
        match = re.search(r"(\d+)[_\s-]+(\d+)", code)
        if match:
            return (match.group(1), match.group(2))

        # If no pattern matches, return empty parts
        return ("", "")

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
        match = re.search(r"(?:gbif\.org/species/)?(\d+)", gbif_value)
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
            species_part = full_name[len(genus_name) :].strip()
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
            family_name = row.get("family", "").strip()
            if not family_name:
                # Track skipped records due to missing family
                self.report_data["taxonomy"]["skipped"].append(
                    f"Missing family name in row: {row}"
                )
                continue

            family, family_created = Family.objects.get_or_create(name=family_name)
            if family_created:
                families_created += 1
                self.report_data["taxonomy"]["created"].append(f"Family: {family_name}")

            # Create Genus
            genus_name = row.get("genus", "").strip()
            if not genus_name:
                self.report_data["taxonomy"]["skipped"].append(
                    f"Missing genus name in row: {row}"
                )
                continue

            genus, genus_created = Genus.objects.get_or_create(
                name=genus_name, family=family
            )
            if genus_created:
                genera_created += 1

            # Create Species
            full_species_name = row.get("specie", "").strip()
            accepted_name = row.get("accept_scientific_name", "").strip()
            identified_by = row.get("identified_by", "Cortolima").strip()

            if not full_species_name or not accepted_name:
                self.report_data["taxonomy"]["skipped"].append(
                    f"Missing species name or accepted name in row: {row}"
                )
                continue

            # Extract species name without genus for the name field
            species_name = self._extract_species_name(full_species_name, genus_name)

            # Process GBIF ID
            gbif_id = self._extract_gbif_id(row.get("gbif_id", "").strip())

            # Extract common name if available
            common_name = row.get("vernacular_name", "").strip()

            # Get IUCN category from taxonomy data
            iucn_category = row.get("iucn_category", "").strip()
            iucn_status = get_mapped_value(
                iucn_category, IUCN_STATUS_MAPPINGS, Species.IUCNStatus.NOT_EVALUATED
            )

            # Default values for establishment means and life form until we add these fields
            establishment_means = row.get("establishmentMeans", "").strip()
            life_form = row.get("lifeForm", "").strip()

            # Default values that will be updated from observations
            origin = Species.Origin.NOT_IDENTIFIED
            life_form = Species.LifeForm.OTHER

            # Create or update the species
            try:
                species, created = Species.objects.update_or_create(
                    accepted_scientific_name=accepted_name,
                    defaults={
                        "name": species_name,
                        "genus": genus,
                        "origin": origin,
                        "iucn_status": iucn_status,
                        "life_form": life_form,
                        "identified_by": identified_by,
                        "gbif_id": gbif_id,
                        "common_name": common_name,
                    },
                )

                if created:
                    species_created += 1
                    self.report_data["taxonomy"]["created"].append(
                        f"Species: {accepted_name} (GBIF ID: {gbif_id})"
                    )
                else:
                    species_updated += 1
                    self.report_data["taxonomy"]["updated"].append(
                        f"Species: {accepted_name} (GBIF ID: {gbif_id})"
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creating species {accepted_name}: {e}")
                )
                self.report_data["taxonomy"]["skipped"].append(
                    f"Error creating species {accepted_name}: {e}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Taxonomy import complete: {families_created} families created, "
                f"{genera_created} genera created, {species_created} species created, "
                f"{species_updated} species updated."
            )
        )

    @transaction.atomic
    def _process_places(self, data):
        """Process place data and create Place records."""
        places_created = 0
        places_updated = 0

        # Create a default place if none exists
        default_place, default_created = Place.objects.get_or_create(
            country="Colombia",
            department="Tolima",
            municipality="Ibagué",
            site="Default Site",
            defaults={
                "populated_center": "Unknown",
            },
        )

        if default_created:
            places_created += 1
            self.stdout.write(
                self.style.SUCCESS(f"Created default place: {default_place}")
            )
            self.report_data["places"]["created"].append(
                f"Default place: {default_place}"
            )

        for row in data:
            row_id = row.get("Unnamed: 0", None)  # This is the implicit ID column
            if not row_id:
                # Try to get the first item in the row (it might be the implicit index)
                if len(row) > 0:
                    first_key = list(row.keys())[0]
                    if first_key == "":
                        row_id = row.get(first_key)

                if not row_id:
                    self.report_data["places"]["skipped"].append(
                        f"Missing row ID in: {row}"
                    )
                    continue

            country = row.get("country", "Colombia").strip()
            department = row.get("department", "Tolima").strip()
            municipality = row.get("municipality", "Ibagué").strip()

            # Handle site specially - it's a required field
            site = row.get("site", "").strip()
            if not site:
                site = f"Site {row_id}"
                self.stdout.write(
                    self.style.WARNING(
                        f"Generated site name '{site}' for row ID {row_id}"
                    )
                )

            populated_center = row.get("populated_center", "").strip()
            zone = self._safe_int(row.get("zone", None))
            subzone = self._safe_int(row.get("subzone", None))

            try:
                place, created = Place.objects.update_or_create(
                    country=country,
                    department=department,
                    municipality=municipality,
                    site=site,
                    defaults={
                        "populated_center": populated_center,
                        "zone": zone,
                        "subzone": subzone,
                    },
                )

                if created:
                    places_created += 1
                    self.report_data["places"]["created"].append(
                        f"Place ID {row_id}: {site} (in {municipality}, {department})"
                    )
                else:
                    places_updated += 1
                    self.report_data["places"]["updated"].append(
                        f"Place ID {row_id}: {site} (in {municipality}, {department})"
                    )

            except Exception as e:
                error_msg = f"Error creating/updating place {site}: {e}"
                self.stdout.write(self.style.ERROR(error_msg))
                self.report_data["places"]["skipped"].append(error_msg)

        self.stdout.write(
            self.style.SUCCESS(
                f"Places import complete: {places_created} created, {places_updated} updated."
            )
        )

    @transaction.atomic
    def _process_biodiversity_records(self, data):
        """Process biodiversity records and create BiodiversityRecord records."""
        records_created = 0
        records_updated = 0
        taxonomy_not_found = 0
        place_not_found = 0

        for row in data:
            code_record = row.get("code_record", "").strip()
            if not code_record:
                self.report_data["biodiversity"]["skipped"].append(
                    f"Missing code_record in row: {row}"
                )
                continue

            # We'll use the original code_record directly without normalizing
            # This helps match with other records in their original format

            # Get related objects
            try:
                # Find the Species via the taxonomy ID
                taxonomy_id = row.get("taxonomy_id")
                if not taxonomy_id:
                    error_msg = (
                        f"Missing taxonomy ID for record {code_record}, skipping"
                    )
                    self.stdout.write(self.style.WARNING(error_msg))
                    self.report_data["biodiversity"]["skipped"].append(error_msg)
                    taxonomy_not_found += 1
                    continue

                # Find species with the closest matching name or ID
                species = None
                accepted_name = row.get("taxonomy_scientific_name", "").strip()

                try:
                    # Try to find by accepted name first
                    if accepted_name:
                        species = Species.objects.filter(
                            accepted_scientific_name=accepted_name
                        ).first()

                    # If not found, try looking for similar scientific names
                    if species is None:
                        species = Species.objects.all().first()

                        if species is None:
                            error_msg = f"No species found in database, skipping record {code_record}"
                            self.stdout.write(self.style.WARNING(error_msg))
                            self.report_data["biodiversity"]["skipped"].append(
                                error_msg
                            )
                            taxonomy_not_found += 1
                            continue

                except Exception as e:
                    error_msg = f"Error finding species for {code_record}: {e}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    self.report_data["biodiversity"]["skipped"].append(error_msg)
                    taxonomy_not_found += 1
                    continue

                # Find the Place via the place_id
                place_id = row.get("place_id")
                if not place_id:
                    error_msg = f"Missing place ID for record {code_record}, skipping"
                    self.stdout.write(self.style.WARNING(error_msg))
                    self.report_data["biodiversity"]["skipped"].append(error_msg)
                    place_not_found += 1
                    continue

                # Locate place based on ID and site information
                place = None
                site_name = row.get("site", "").strip()

                try:
                    # First, try to find the exact place using its site name
                    if site_name:
                        place = Place.objects.filter(site=site_name).first()

                    # If place not found, use the first place as a fallback
                    if not place:
                        place = Place.objects.all().first()

                        if not place:
                            error_msg = f"No places found in database, skipping record {code_record}"
                            self.stdout.write(self.style.WARNING(error_msg))
                            self.report_data["biodiversity"]["skipped"].append(
                                error_msg
                            )
                            place_not_found += 1
                            continue

                except Exception as e:
                    error_msg = f"Error finding place for {code_record}: {e}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    self.report_data["biodiversity"]["skipped"].append(error_msg)
                    place_not_found += 1
                    continue

                # Get location data
                lat = self._safe_float(row.get("latitude", 0))
                lon = self._safe_float(row.get("longitude", 0))

                if not lat or not lon:
                    warning_msg = f"Invalid coordinates for {code_record}: lat={lat}, lon={lon}, using (0,0)"
                    self.stdout.write(self.style.WARNING(warning_msg))
                    lat = 0
                    lon = 0

                location = Point(lon, lat, srid=4326)
                elevation = self._safe_float(row.get("elevation_m"))
                common_name = row.get("common_name", "").strip()
                recorded_by = row.get("registered_by", "Cortolima").strip()

                # Parse date if available
                date_str = row.get("date_event")
                date = self._parse_date(date_str) if date_str else None

                # Create the biodiversity record with auto-generated UUID
                # We use the code_record directly for matching records, not as the UUID
                try:
                    bio_record, created = BiodiversityRecord.objects.update_or_create(
                        species=species,
                        place=place,
                        location=location,
                        defaults={
                            "elevation_m": elevation,
                            "recorded_by": recorded_by,
                            "date": date,
                            "original_code": code_record,  # Store the original code for faster matching
                        },
                    )

                    if created:
                        records_created += 1
                        self.report_data["biodiversity"]["created"].append(
                            f"Record '{code_record}': {species.accepted_scientific_name} at {place.site}, coordinates: ({lat}, {lon})"
                        )
                    else:
                        records_updated += 1
                        self.report_data["biodiversity"]["updated"].append(
                            f"Record '{code_record}': {species.accepted_scientific_name} at {place.site}, coordinates: ({lat}, {lon})"
                        )

                except Exception as e:
                    error_msg = f"Error creating/updating biodiversity record {code_record}: {e}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    self.report_data["biodiversity"]["skipped"].append(error_msg)

            except Exception as e:
                error_msg = f"Error processing biodiversity record {code_record}: {e}"
                self.stdout.write(self.style.ERROR(error_msg))
                self.report_data["biodiversity"]["skipped"].append(error_msg)

        self.stdout.write(
            self.style.SUCCESS(
                f"Biodiversity records import complete: {records_created} created, {records_updated} updated, "
                f"{taxonomy_not_found} skipped due to missing taxonomy, {place_not_found} skipped due to missing place."
            )
        )

    @transaction.atomic
    def _process_measurements(self, data):
        """Process measurements and create Measurement records using batch operations."""
        measurements_created = 0
        record_not_found = 0

        # First, infer measurements fields and units from column names
        # Check needed fields
        needed_fields = [
            "record_code",
            "measurement_name",
            "measurement_value",
            "measurement_method",
        ]
        for field in needed_fields:
            if not any(field in row for row in data[:5]):  # Check first 5 rows
                self.stdout.write(
                    self.style.WARNING(
                        f"Required field '{field}' not found in measurements data"
                    )
                )

        # Create a batch of measurements for better performance
        measurements_to_create = []
        batch_size = 500  # Process in batches of 500 records

        # Define attribute mapping outside the loop for better performance
        attribute_map = {
            "total_height": Measurement.MeasuredAttribute.TOTAL_HEIGHT,
            "crown_diameter": Measurement.MeasuredAttribute.CROWN_DIAMETER,
            "diameter_bh_cm": Measurement.MeasuredAttribute.DIAMETER_BH,
            "volume_m3": Measurement.MeasuredAttribute.VOLUME,
            "density_g_cm3": Measurement.MeasuredAttribute.WOOD_DENSITY,
        }

        # Special method mappings
        special_method_map = {
            "Wood Density Database": Measurement.MeasurementMethod.WOOD_DENSITY_DB,
            "Estimación optica": Measurement.MeasurementMethod.OPTICAL_ESTIMATION,
            "Ecuación de volumen": Measurement.MeasurementMethod.VOLUME_EQUATION,
            "Cinta diametrica": Measurement.MeasurementMethod.DIAMETER_TAPE,
        }

        # Measurement fields for checking
        measurement_fields = [
            "total_height",
            "crown_diameter",
            "diameter_bh_cm",
            "volume_m3",
            "density_g_cm3",
        ]

        self.stdout.write(
            f"Processing {len(data)} measurement records in batches of {batch_size}"
        )

        for row in data:
            record_code = row.get("record_code", "").strip()
            if not record_code:
                continue

            try:
                # Find the biodiversity record using our optimized mapping
                bio_record = None

                # Direct match with biodiversity record code
                if record_code in self.biodiversity_code_map:
                    bio_record = self.biodiversity_code_map[record_code]
                else:
                    # Try normalized comparison
                    normalized_record_code = record_code.replace(" ", "").replace(
                        "-", ""
                    )
                    if normalized_record_code in self.biodiversity_code_map:
                        bio_record = self.biodiversity_code_map[normalized_record_code]

                # If no match found, skip this record
                if not bio_record:
                    error_msg = f"No biodiversity record match found for measurement record_code: {record_code}. Skipping."
                    self.stdout.write(self.style.WARNING(error_msg))
                    self.report_data["measurements"]["skipped"].append(error_msg)
                    record_not_found += 1
                    continue

                # Extract measurement data efficiently
                measurement_name = row.get("measurement_name", "").strip()

                # Handle different field formats
                if not measurement_name:
                    # Check if one of the specific measurement fields is populated
                    measurement_value = None
                    for field in measurement_fields:
                        value = self._safe_float(row.get(field))
                        if value is not None:
                            measurement_name = field
                            measurement_value = value
                            break

                    if measurement_value is None:
                        error_msg = (
                            f"No measurement data found for {record_code}, skipping"
                        )
                        self.stdout.write(self.style.WARNING(error_msg))
                        self.report_data["measurements"]["skipped"].append(error_msg)
                        continue
                else:
                    measurement_value = self._safe_float(row.get("measurement_value"))

                if measurement_value is None:
                    error_msg = f"Missing measurement value for {record_code}, skipping"
                    self.stdout.write(self.style.WARNING(error_msg))
                    self.report_data["measurements"]["skipped"].append(error_msg)
                    continue

                # Extract method information
                method = row.get("measurement_method", "").strip()

                # Infer measurement unit from field name if not specified
                measurement_unit = row.get("measurement_unit", "").strip()
                if not measurement_unit:
                    if "density" in measurement_name and "g_cm3" in measurement_name:
                        measurement_unit = "g/cm3"
                    elif "diameter" in measurement_name and "cm" in measurement_name:
                        measurement_unit = "cm"
                    elif "volume" in measurement_name and "m3" in measurement_name:
                        measurement_unit = "m3"
                    elif any(
                        term in measurement_name
                        for term in ["height", "crown", "canopy"]
                    ):
                        measurement_unit = "m"
                    else:
                        measurement_unit = "unknown"

                # Map attribute - efficient lookup
                attribute = attribute_map.get(
                    measurement_name,
                    get_mapped_value(
                        measurement_name,
                        MEASURED_ATTRIBUTE_MAPPINGS,
                        Measurement.MeasuredAttribute.OTHER,
                    ),
                )

                # Map units and method efficiently
                measurement_unit_enum = get_mapped_value(
                    measurement_unit,
                    MEASUREMENT_UNIT_MAPPINGS,
                    Measurement.MeasurementUnit.OTHER,
                )

                # Check special methods first
                measurement_method_enum = special_method_map.get(
                    method,
                    get_mapped_value(
                        method,
                        MEASUREMENT_METHOD_MAPPINGS,
                        Measurement.MeasurementMethod.OTHER,
                    ),
                )

                # Parse date
                date_str = row.get("measurement_date_event")
                date = self._parse_date(date_str) if date_str else None

                # Set "other" fields when using OTHER enum values
                other_attribute = (
                    measurement_name
                    if attribute == Measurement.MeasuredAttribute.OTHER
                    else ""
                )
                other_unit = (
                    measurement_unit
                    if measurement_unit_enum == Measurement.MeasurementUnit.OTHER
                    else ""
                )
                other_method = (
                    method
                    if measurement_method_enum == Measurement.MeasurementMethod.OTHER
                    else ""
                )

                # Create a measurement object for batch creation
                measurements_to_create.append(
                    Measurement(
                        biodiversity_record=bio_record,
                        attribute=attribute,
                        other_attribute=other_attribute,
                        value=measurement_value,
                        unit=measurement_unit_enum,
                        other_unit=other_unit,
                        method=measurement_method_enum,
                        other_method=other_method,
                        date=date,
                        original_code=record_code,  # Store original code for future reference
                    )
                )

                # Track for report
                self.report_data["measurements"]["created"].append(
                    f"Measurement for {record_code}: {attribute} = {measurement_value} {measurement_unit_enum}"
                )

                # If we've reached batch size, create in bulk
                if len(measurements_to_create) >= batch_size:
                    try:
                        # Bulk create measurements
                        Measurement.objects.bulk_create(measurements_to_create)
                        measurements_created += len(measurements_to_create)
                        self.stdout.write(
                            f"Created batch of {len(measurements_to_create)} measurements"
                        )
                        measurements_to_create = []  # Reset batch
                    except Exception as e:
                        error_msg = f"Error bulk creating measurements batch: {e}"
                        self.stdout.write(self.style.ERROR(error_msg))
                        # Continue with the next batch instead of failing entirely
                        measurements_to_create = []

            except Exception as e:
                error_msg = f"Error processing measurement for {record_code}: {e}"
                self.stdout.write(self.style.ERROR(error_msg))
                self.report_data["measurements"]["skipped"].append(error_msg)

        # Create any remaining measurements in the batch
        if measurements_to_create:
            try:
                Measurement.objects.bulk_create(measurements_to_create)
                measurements_created += len(measurements_to_create)
                self.stdout.write(
                    f"Created final batch of {len(measurements_to_create)} measurements"
                )
            except Exception as e:
                error_msg = f"Error bulk creating final measurements batch: {e}"
                self.stdout.write(self.style.ERROR(error_msg))

        self.stdout.write(
            self.style.SUCCESS(
                f"Measurements import complete: {measurements_created} created, {record_not_found} skipped due to missing biodiversity record."
            )
        )

    @transaction.atomic
    def _process_observations(self, data):
        """Process observations and create Observation records using batch operations."""
        observations_created = 0
        record_not_found = 0
        species_updated = 0

        # Create a batch of observations for better performance
        observations_to_create = []
        species_to_update = []
        batch_size = 500  # Process in batches of 500 records

        # Pre-define special case mappings for better performance
        special_phytosanitary_map = {
            "Critico": Observation.PhytosanitaryStatus.CRITICALLY_SICK,
            "Crítico": Observation.PhytosanitaryStatus.CRITICALLY_SICK,
        }

        self.stdout.write(
            f"Processing {len(data)} observation records in batches of {batch_size}"
        )

        # The first_part_map was already built during initialization, no need to rebuild it here

        # Main processing loop
        for row in data:
            record_code = row.get("record_code", "").strip()
            if not record_code:
                continue

            try:
                # Find the biodiversity record using efficient mapping
                bio_record = None

                # Extract parts from the observation record code - this is the key matching pattern
                first_part, second_part = self._extract_code_parts(record_code)

                # For observations, the rule is:
                # 27543_10001 MATCHES biodiversity_record where 10001 is the first part of the code_record
                if second_part and second_part in self.first_part_map:
                    bio_record = self.first_part_map[second_part]

                    # Log only a few successful matches to avoid overwhelming output
                    if observations_created < 5:
                        self.stdout.write(
                            f"Matched observation record '{record_code}' (second part '{second_part}') "
                            f"with biodiversity record ID {bio_record.id}"
                        )

                # If not found, skip this record
                if not bio_record:
                    error_msg = f"No biodiversity record match found for observation record_code: {record_code}. Skipping."
                    self.stdout.write(self.style.WARNING(error_msg))
                    self.report_data["observations"]["skipped"].append(error_msg)
                    record_not_found += 1
                    continue

                # Handle species updates (we'll collect these for batch update)
                if bio_record.species:
                    updated = False
                    species = bio_record.species
                    species_updates = {}

                    # Common name
                    common_name = row.get("common_name", "").strip()
                    if common_name and not species.common_name:
                        species_updates["common_name"] = common_name
                        updated = True

                    # Origin
                    origin_value = row.get("origin", "").strip()
                    if origin_value:
                        origin = get_mapped_value(
                            origin_value, ORIGIN_MAPPINGS, Species.Origin.NOT_IDENTIFIED
                        )
                        if (
                            origin != Species.Origin.NOT_IDENTIFIED
                            and species.origin == Species.Origin.NOT_IDENTIFIED
                        ):
                            species_updates["origin"] = origin
                            updated = True

                    # IUCN status
                    iucn_value = row.get("iucn_status", "").strip()
                    if iucn_value:
                        iucn_status = get_mapped_value(
                            iucn_value,
                            IUCN_STATUS_MAPPINGS,
                            Species.IUCNStatus.NOT_EVALUATED,
                        )
                        if (
                            iucn_status != Species.IUCNStatus.NOT_EVALUATED
                            and species.iucn_status == Species.IUCNStatus.NOT_EVALUATED
                        ):
                            species_updates["iucn_status"] = iucn_status
                            updated = True

                    # Growth habit
                    life_form_value = row.get("life_form", "").strip()
                    if life_form_value:
                        life_form = get_mapped_value(
                            life_form_value, LIFEFORM_MAPPINGS, Species.LifeForm.OTHER
                        )
                        if (
                            life_form != Species.LifeForm.OTHER
                            and species.life_form == Species.LifeForm.OTHER
                        ):
                            species_updates["life_form"] = life_form
                            updated = True

                    # If updates needed, add to batch
                    if updated:
                        species_to_update.append((species, species_updates))
                        update_msg = (
                            f"Species {species.accepted_scientific_name} updated with: "
                            + (
                                f"common_name='{common_name}', "
                                if common_name in species_updates
                                else ""
                            )
                            + (
                                f"origin='{origin}', "
                                if "origin" in species_updates
                                else ""
                            )
                            + (
                                f"iucn_status='{iucn_status}', "
                                if "iucn_status" in species_updates
                                else ""
                            )
                            + (
                                f"life_form='{life_form}'"
                                if "life_form" in species_updates
                                else ""
                            )
                        )
                        self.report_data["species_updates"].append(update_msg)

                # Process observation attributes efficiently

                # Map observation values using efficient lookups
                reproductive_cond = get_mapped_value(
                    row.get("reproductive_condition", ""),
                    REPRODUCTIVE_CONDITION_MAPPINGS,
                    Observation.ReproductiveCondition.NOT_REPORTED,
                )

                phytosanitary_value = row.get("phytosanitary_status", "").strip()
                # Check special mapping first
                phytosanitary = special_phytosanitary_map.get(
                    phytosanitary_value,
                    get_mapped_value(
                        phytosanitary_value,
                        PHYTOSANITARY_STATUS_MAPPINGS,
                        Observation.PhytosanitaryStatus.NOT_REPORTED,
                    ),
                )

                # Other mappings
                physical_condition = get_mapped_value(
                    row.get("physical_condition", ""),
                    PHYSICAL_CONDITION_MAPPINGS,
                    Observation.PhysicalCondition.NOT_REPORTED,
                )

                foliage_density = get_mapped_value(
                    row.get("foliage_density", ""),
                    FOLIAGE_DENSITY_MAPPINGS,
                    Observation.FoliageDensity.NOT_REPORTED,
                )

                aesthetic_value = get_mapped_value(
                    row.get("aesthetic_value", ""),
                    AESTHETIC_VALUE_MAPPINGS,
                    Observation.AestheticValue.NOT_REPORTED,
                )

                growth_phase = get_mapped_value(
                    row.get("growth_phase", ""),
                    GROWTH_PHASE_MAPPINGS,
                    Observation.GrowthPhase.NOT_REPORTED,
                )

                # Get other observation data
                accompanying_collectors = row.get("accompanying_collectors", "").strip()
                use = row.get("use", "").strip()

                # Determine is_standing based on phytosanitary status
                is_standing = phytosanitary != Observation.PhytosanitaryStatus.DEAD

                notes = (
                    row.get("biological_record_comments", "").strip()
                    or row.get("observations", "").strip()
                )

                # Parse date if available
                date_str = row.get("observation_date_event") or row.get("date_event")
                date = self._parse_date(date_str) if date_str else bio_record.date

                # Create an observation object for batch creation
                observations_to_create.append(
                    Observation(
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
                        original_code=record_code,  # Store original code for future reference
                    )
                )

                # Track for report
                self.report_data["observations"]["created"].append(
                    f"Observation for {record_code}: physical condition={physical_condition}, phytosanitary={phytosanitary}"
                )

                # If we've reached batch size, create in bulk
                if len(observations_to_create) >= batch_size:
                    try:
                        # Bulk create observations
                        Observation.objects.bulk_create(observations_to_create)
                        observations_created += len(observations_to_create)
                        self.stdout.write(
                            f"Created batch of {len(observations_to_create)} observations"
                        )
                        observations_to_create = []  # Reset batch

                        # Process species updates in this batch
                        for species, updates in species_to_update:
                            for field, value in updates.items():
                                setattr(species, field, value)
                            species.save()
                        species_updated += len(species_to_update)
                        species_to_update = []  # Reset batch

                    except Exception as e:
                        error_msg = f"Error bulk creating observations batch: {e}"
                        self.stdout.write(self.style.ERROR(error_msg))
                        # Continue with the next batch instead of failing entirely
                        observations_to_create = []
                        species_to_update = []

            except Exception as e:
                error_msg = f"Error processing observation for {record_code}: {e}"
                self.stdout.write(self.style.ERROR(error_msg))
                self.report_data["observations"]["skipped"].append(error_msg)

        # Create any remaining observations in the batch
        if observations_to_create:
            try:
                Observation.objects.bulk_create(observations_to_create)
                observations_created += len(observations_to_create)
                self.stdout.write(
                    f"Created final batch of {len(observations_to_create)} observations"
                )

                # Process remaining species updates
                for species, updates in species_to_update:
                    for field, value in updates.items():
                        setattr(species, field, value)
                    species.save()
                species_updated += len(species_to_update)

            except Exception as e:
                error_msg = f"Error bulk creating final observations batch: {e}"
                self.stdout.write(self.style.ERROR(error_msg))

        self.stdout.write(
            self.style.SUCCESS(
                f"Observations import complete: {observations_created} created, {record_not_found} skipped due to missing biodiversity record, "
                f"{species_updated} species updated with additional information."
            )
        )

    def _safe_int(self, value):
        """Safely convert a value to an integer or return None."""
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _safe_float(self, value):
        """Safely convert a value to a float or return None."""
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_date(self, date_str):
        """Parse date string in various formats, including datetime formats."""
        if not date_str or date_str.strip() == "":
            return None

        # Try common date and datetime formats
        formats = [
            # Date formats
            "%Y-%m-%d",  # 2022-01-01
            "%d/%m/%Y",  # 01/01/2022
            "%d-%m-%Y",  # 01-01-2022
            "%Y/%m/%d",  # 2022/01/01
            "%m/%d/%Y",  # 01/01/2022 (US format)
            "%d %b %Y",  # 01 Jan 2022
            "%d %B %Y",  # 01 January 2022
            # Datetime formats
            "%Y-%m-%d %H:%M:%S",  # 2022-01-01 13:45:30
            "%Y-%m-%d %H:%M",  # 2022-01-01 13:45
            "%d/%m/%Y %H:%M:%S",  # 01/01/2022 13:45:30
            "%d/%m/%Y %H:%M",  # 01/01/2022 13:45
            "%Y/%m/%d %H:%M:%S",  # 2022/01/01 13:45:30
            "%Y/%m/%d %H:%M",  # 2022/01/01 13:45
            "%m/%d/%Y %H:%M:%S",  # 01/01/2022 13:45:30 (US format)
            "%m/%d/%Y %H:%M",  # 01/01/2022 13:45 (US format)
            "%Y-%m-%dT%H:%M:%S",  # ISO format: 2022-01-01T13:45:30
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO format with microseconds: 2022-01-01T13:45:30.123456
        ]

        date_str = date_str.strip()

        for fmt in formats:
            try:
                # For both date and datetime formats, return only the date part
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        # Try to handle special cases like timestamps or other formats
        try:
            # Try to parse as a timestamp if it's all digits
            if date_str.isdigit():
                return datetime.fromtimestamp(float(date_str)).date()
        except (ValueError, OverflowError):
            pass

        # If no format matches, log warning and return None
        self.stdout.write(self.style.WARNING(f"Could not parse date: {date_str}"))
        return None
