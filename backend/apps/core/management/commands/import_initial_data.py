"""
Import initial data from CSV files into the database.

This Django management command imports data for an Urban Tree Observatory including:
- Taxonomy (families, genera, species)
- Places and locations
- Functional groups and traits
- Biodiversity records
- Measurements and observations

Prerequisites:
1. Required migrations must be completed
2. Target tables must be empty (except for country, department, municipality)
3. Municipality of Ibagué (Tolima, Colombia) must exist in the database

Assumptions:
- All records are for the municipality of Ibagué, Tolima, Colombia.
- The CSV files are structured correctly and contain all necessary data.

Usage:
    python manage.py import_initial_data <data_dir>

Arguments:
    data_dir - Path to directory containing the required CSV files

Example:
    python manage.py import_initial_data /path/to/data
"""

from pathlib import Path

from tqdm import tqdm
import pandas as pd

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection

from apps.taxonomy.models import (
    Family,
    Genus,
    Species,
    FunctionalGroup,
    Trait,
    TraitValue,
)
from apps.places.models import Municipality, Place
from apps.biodiversity.models import BiodiversityRecord
from apps.reports.models import Measurement, Observation


class Command(BaseCommand):
    help = "Import CSV data into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "data_dir", type=str, help="Path to directory containing CSV files"
        )

    def parse_date(self, date_string):
        """Convert a date-time string from CSV to a date object for Django DateField.

        Args:
            date_string: String in format 'YYYY-MM-DD HH:MM:SS' or None/NaN

        Returns:
            date object or None if input is empty/NaN
        """
        if pd.isna(date_string) or not date_string:
            return None

        try:
            # Parse the datetime string and extract just the date part
            return pd.to_datetime(date_string).date()
        except ValueError:
            return None

    def handle(self, *args, **options):
        self.data_dir = Path(options["data_dir"])
        self.stdout.write(self.style.SUCCESS(f"Starting import from {self.data_dir}"))

        # Check that required migrations have run
        self.check_required_data()

        # Check that tables to be populated are empty
        self.check_empty_tables()

        try:
            with transaction.atomic():
                # Call import methods in order of dependencies
                self.import_taxonomy()
                self.import_places()
                self.import_functional_groups()
                self.import_biodiversity_records()
                self.import_measurements()
                self.import_observations()

            self.stdout.write(self.style.SUCCESS("Import completed successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))
            raise

    def check_required_data(self):
        """Check that required initial data exists (from migrations)."""
        try:
            # Check that Ibagué exists (if so, Colombia and Tolima are assumed present)
            ibague = Municipality.objects.get(name="Ibagué")
            self.stdout.write(
                self.style.SUCCESS("Required initial location data confirmed")
            )

            # Store for later use
            self.ibague = ibague
        except Municipality.DoesNotExist:
            raise CommandError(
                "Municipality 'Ibagué' not found. Please ensure initial migrations have run."
            )

    def check_empty_tables(self):
        """Check that all tables to be populated are empty before import."""
        tables_to_check = [
            (Family, "Family"),
            (Genus, "Genus"),
            (Species, "Species"),
            (Place, "Place"),
            (FunctionalGroup, "FunctionalGroup"),
            (Trait, "Trait"),
            (TraitValue, "TraitValue"),
            (BiodiversityRecord, "BiodiversityRecord"),
            (Measurement, "Measurement"),
            (Observation, "Observation"),
        ]

        non_empty_tables = []

        for model, name in tables_to_check:
            if model.objects.exists():
                non_empty_tables.append(name)

        if non_empty_tables:
            message = (
                f"The following tables are not empty: {', '.join(non_empty_tables)}. "
                "Please empty these tables before running the import to avoid ID conflicts."
            )
            raise CommandError(message)

        self.stdout.write(
            self.style.SUCCESS("All required tables are empty - ready to import")
        )

    def import_taxonomy(self):
        self.stdout.write("Importing taxonomy data...")

        # Read CSV with pandas for easier handling
        # Prevent pandas from interpreting "NA" as NaN (missing value)
        # NA is a valid value for origin ("native").
        df = pd.read_csv(
            self.data_dir / "taxonomy_details.csv",
            keep_default_na=False,  # Don't convert "NA" to NaN
            na_values=[],  # Empty list means don't interpret any values as NaN
        )

        # Add a temporary taxonomy_id column (1-indexed)
        df["taxonomy_id"] = range(1, len(df) + 1)

        # Create families (track created ones to avoid duplicates)
        families = {}
        for family_name in tqdm(df["family"].unique(), desc="Importing families"):
            family, created = Family.objects.get_or_create(name=family_name)
            families[family_name] = family

        # Create genera
        genera = {}
        for _, row in tqdm(
            df[["family", "genus"]].drop_duplicates().iterrows(),
            desc="Importing genera",
            total=len(df[["family", "genus"]].drop_duplicates()),
        ):
            genus, created = Genus.objects.get_or_create(
                name=row["genus"], family=families[row["family"]]
            )
            genera[row["genus"]] = genus

        # Create species (all rows, as each represents a unique species)
        species_batch = []
        # species_map = {}  # To store id -> Species mapping for later use

        for _, row in tqdm(df.iterrows(), desc="Preparing species", total=len(df)):
            # Map the origin, iucn_status, etc from CSV to model choices
            # Note: We assume the CSV values match the model choices' values
            species = Species(
                genus=genera[row["genus"]],
                name=row["specie"].replace(
                    row["genus"] + " ", ""
                ),  # Remove genus prefix if present
                accepted_scientific_name=row["accept_scientific_name"],
                origin=row["origin"],
                iucn_status=row["iucn_category"],
                life_form=row["lifeForm"],
                canopy_shape=row["canopy_shape_code"],
                flower_color=row["flower_color_code"],
                gbif_id=row["gbif_id"] if row["gbif_id"] != "0" else None,
                identified_by=row["identified_by"],
                date=self.parse_date(row["date_of_identification"])
                if pd.notna(row["date_of_identification"])
                else None,
                # functional_group will be set later
            )
            species_batch.append(species)

        # Bulk create species
        created_species = Species.objects.bulk_create(species_batch, batch_size=100)

        # Map taxonomy_id to created species objects for later use
        species_by_id = {}
        for i, (_, row_data) in enumerate(df.iterrows()):
            species_by_id[row_data["taxonomy_id"]] = created_species[i]

        self.species_by_id = species_by_id  # Save for later

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(families)} families, {len(genera)} genera, {len(created_species)} species"
            )
        )

    def import_places(self):
        self.stdout.write("Importing place data...")

        # Read place.csv
        df = pd.read_csv(self.data_dir / "place.csv")

        # Create places using the ibague reference we stored earlier
        places_batch = []
        for _, row in tqdm(df.iterrows(), desc="Preparing places", total=len(df)):
            place = Place(
                id=row["id_place"],  # Primary key
                municipality=self.ibague,  # Using the stored reference
                site=row["site"],
                populated_center=row["populated_center"],
                zone=row["zone"] if pd.notna(row["zone"]) else None,
                subzone=row["subzone"] if pd.notna(row["subzone"]) else None,
            )
            places_batch.append(place)

        # Bulk create places
        places = Place.objects.bulk_create(places_batch, batch_size=100)

        # Create mapping for use in biodiversity records
        self.places_by_id = {place.id: place for place in places}

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(places)} places in Ibagué, Tolima, Colombia"
            )
        )

    def import_functional_groups(self):
        self.stdout.write("Importing functional groups and traits...")

        # Read functional_groups_traits.csv
        df = pd.read_csv(self.data_dir / "functional_groups_traits.csv")

        # Create the four traits (if they don't exist already)
        traits = {
            "carbon": Trait.objects.get_or_create(
                type=Trait.TraitType.CARBON_SEQUESTRATION
            )[0],
            "shade": Trait.objects.get_or_create(type=Trait.TraitType.SHADE_IDX)[0],
            "canopy": Trait.objects.get_or_create(type=Trait.TraitType.CANOPY_DIAMETER)[
                0
            ],
            "height": Trait.objects.get_or_create(type=Trait.TraitType.HEIGHT_MAX)[0],
        }

        # Create functional groups
        fg_batch = []
        for pft_id in tqdm(df["pft_id"].unique(), desc="Creating functional groups"):
            fg = FunctionalGroup(group_id=pft_id)
            fg_batch.append(fg)

        functional_groups = FunctionalGroup.objects.bulk_create(fg_batch)

        # Create mapping of pft_id to FunctionalGroup objects
        fg_map = {fg.group_id: fg for fg in functional_groups}

        # Create trait values
        trait_values = []
        for _, row in tqdm(df.iterrows(), desc="Creating trait values"):
            # Carbon sequestration trait values
            trait_values.append(
                TraitValue(
                    trait=traits["carbon"],
                    functional_group=fg_map[row["pft_id"]],
                    min_value=row["carbon_sequestration_min"]
                    if pd.notna(row["carbon_sequestration_min"])
                    else None,
                    max_value=row["carbon_sequestration_max"]
                    if pd.notna(row["carbon_sequestration_max"])
                    else None,
                )
            )

            # Shade index trait values
            trait_values.append(
                TraitValue(
                    trait=traits["shade"],
                    functional_group=fg_map[row["pft_id"]],
                    min_value=row["shade_index_min"]
                    if pd.notna(row["shade_index_min"])
                    else None,
                    max_value=row["shade_index_max"]
                    if pd.notna(row["shade_index_max"])
                    else None,
                )
            )

            # Canopy diameter trait values
            trait_values.append(
                TraitValue(
                    trait=traits["canopy"],
                    functional_group=fg_map[row["pft_id"]],
                    min_value=row["canopy_diameter_min"]
                    if pd.notna(row["canopy_diameter_min"])
                    else None,
                    max_value=row["canopy_diameter_max"]
                    if pd.notna(row["canopy_diameter_max"])
                    else None,
                )
            )

            # Height max trait values
            trait_values.append(
                TraitValue(
                    trait=traits["height"],
                    functional_group=fg_map[row["pft_id"]],
                    min_value=row["height_max_min"]
                    if pd.notna(row["height_max_min"])
                    else None,
                    max_value=row["height_max_max"]
                    if pd.notna(row["height_max_max"])
                    else None,
                )
            )

        # Bulk create all trait values
        TraitValue.objects.bulk_create(trait_values, batch_size=500)

        # Update species with functional group references
        # Group by taxonomy_id to get functional group for each species
        taxonomy_to_fg = {}
        for _, row in df.iterrows():
            taxonomy_to_fg[row["taxonomy_id"]] = fg_map[row["pft_id"]]

        # Batch update species with functional groups
        species_updates = []
        for taxonomy_id, fg in taxonomy_to_fg.items():
            if taxonomy_id in self.species_by_id:
                species = self.species_by_id[taxonomy_id]
                species.functional_group = fg
                species_updates.append(species)

        # Batch update species
        Species.objects.bulk_update(
            species_updates, ["functional_group"], batch_size=100
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(functional_groups)} functional groups, {len(trait_values)} trait values"
            )
        )

    def import_biodiversity_records(self):
        self.stdout.write("Importing biodiversity records...")

        # Read biodiversity_records.csv
        df = pd.read_csv(self.data_dir / "biodiversity_records.csv")

        # Create biodiversity records in batches to manage memory
        batch_size = 1000
        total_batches = (len(df) // batch_size) + (1 if len(df) % batch_size > 0 else 0)

        records_created = 0
        self.bio_records_by_id = {}  # To store mapping for later use with measurements/observations

        for batch_idx in tqdm(
            range(total_batches), desc="Importing biodiversity records"
        ):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]

            batch_records = []
            for _, row in batch_df.iterrows():
                # Create a Point geometry for the location
                location = f"POINT({row['longitude']} {row['latitude']})"

                bio_record = BiodiversityRecord(
                    id=row["code_record"],  # Primary key
                    common_name=row["common_name"],
                    species=self.species_by_id[row["taxonomy_id"]],
                    place=self.places_by_id[row["place_id"]],
                    location=location,
                    elevation_m=row["elevation_m"]
                    if pd.notna(row["elevation_m"])
                    else None,
                    recorded_by=row["registered_by"],
                    date=self.parse_date(row["date_event"])
                    if pd.notna(row["date_event"])
                    else None,
                )
                batch_records.append(bio_record)

            # Bulk create the batch
            created_records = BiodiversityRecord.objects.bulk_create(batch_records)
            records_created += len(created_records)

            # Update mapping
            for record in created_records:
                self.bio_records_by_id[record.id] = record

        self.stdout.write(
            self.style.SUCCESS(f"Imported {records_created} biodiversity records")
        )

    def import_measurements(self):
        self.stdout.write("Importing measurements...")

        # Read measurements.csv
        # We'll process this in chunks due to the large number of rows
        chunksize = 50000  # Adjust based on available memory

        reader = pd.read_csv(self.data_dir / "measurements.csv", chunksize=chunksize)

        total_measurements = 0

        for chunk in tqdm(reader, desc="Importing measurements"):
            # Process each chunk
            batch_measurements = []

            for _, row in chunk.iterrows():
                measurement = Measurement(
                    biodiversity_record_id=row["record_code"],  # Foreign key
                    attribute=row["measurement_name"],
                    value=row["measurement_value"],
                    unit=row["measurement_unit"],
                    method=row["measurement_method"],
                    date=self.parse_date(row["measurement_date_event"])
                    if pd.notna(row["measurement_date_event"])
                    else None,
                )
                batch_measurements.append(measurement)

            # Bulk create the measurements in this chunk
            created = Measurement.objects.bulk_create(
                batch_measurements, batch_size=5000
            )
            total_measurements += len(created)

        self.stdout.write(
            self.style.SUCCESS(f"Imported {total_measurements} measurements")
        )

    def import_observations(self):
        self.stdout.write("Importing observations...")

        # Read observations_details.csv with specified data types to handle mixed types warning
        df = pd.read_csv(
            self.data_dir / "observations_details.csv",
            # Convert the problematic columns (8,9,10,11,13,34) to string type
            # Column index starts at 0, so we need to adjust the numbers from the warning
            dtype={
                "rd": str,  # Column 8
                "dm": str,  # Column 9
                "bbs": str,  # Column 10
                "ab": str,  # Column 11
                "pi": str,  # Column 13
                "photo_url": str,  # Column 34
            },
        )

        # Process in batches
        batch_size = 1000
        total_batches = (len(df) // batch_size) + (1 if len(df) % batch_size > 0 else 0)

        observations_created = 0

        for batch_idx in tqdm(range(total_batches), desc="Importing observations"):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]

            batch_observations = []
            for _, row in batch_df.iterrows():
                observation = Observation(
                    biodiversity_record_id=row["record_code"],  # Foreign key
                    reproductive_condition=row["reproductive_condition"],
                    phytosanitary_status=row["phytosanitary_status"],
                    physical_condition=row["physical_condition"],
                    foliage_density=row["foliage_density"],
                    aesthetic_value=row["aesthetic_value"],
                    growth_phase=row["growth_phase"],
                    field_notes=row["field_notes"]
                    if pd.notna(row["field_notes"])
                    else "",
                    standing=row["general_state"],  # Renamed field
                    # Add all the coded fields
                    rd=row["rd"],
                    dm=row["dm"],
                    bbs=row["bbs"],
                    ab=row["ab"],
                    ed=row["ed"],
                    pi=row["pi"],
                    ph=row["ph"],
                    pa=row["pa"],
                    hc=row["hc"],
                    hcf=row["hcf"],
                    pd=row["pd"],
                    pe=row["pe"],
                    pp=row["pp"],
                    po=row["po"],
                    cre=row["cre"],
                    crh=row["crh"],
                    cra=row["cra"],
                    coa=row["coa"],
                    ce=row["ce"],
                    civ=row["civ"],
                    crt=row["crt"],
                    crg=row["crg"],
                    cap=row["cap"],
                    r_vol=row["r_vol"],
                    r_cr=row["r_cr"],
                    r_ce=row["r_ce"],
                    recorded_by="Cortolima",  # Default from model
                    photo_url=""
                    if pd.isna(row["photo_url"]) or row["photo_url"] == "0"
                    else row["photo_url"],
                    accompanying_collectors=row["accompanying_collectors"]
                    if pd.notna(row["accompanying_collectors"])
                    else "",
                )
                batch_observations.append(observation)

            # Bulk create the observations in this batch
            created = Observation.objects.bulk_create(
                batch_observations, batch_size=1000
            )
            observations_created += len(created)

        self.stdout.write(
            self.style.SUCCESS(f"Imported {observations_created} observations")
        )

    def reset_sequences(self):
        """Reset ID sequences after import for PostgreSQL."""
        with connection.cursor() as cursor:
            tables = [
                "taxonomy_family",
                "taxonomy_genus",
                "taxonomy_species",
                "places_country",
                "places_department",
                "places_municipality",
                "places_place",
                "taxonomy_functionalgroup",
                "taxonomy_trait",
                "taxonomy_traitvalue",
                "biodiversity_biodiversityrecord",
                "reports_measurement",
                "reports_observation",
            ]

            for table in tables:
                cursor.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)"
                )

        self.stdout.write(self.style.SUCCESS("Sequence IDs reset successfully"))
