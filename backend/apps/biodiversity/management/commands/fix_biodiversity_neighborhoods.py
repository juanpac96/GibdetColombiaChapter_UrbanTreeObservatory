import time

from django.contrib.gis.db.models import Extent, GeometryField
from django.contrib.gis.db.models.functions import Cast
from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from apps.biodiversity.models import BiodiversityRecord
from apps.places.models import Locality, Neighborhood


class Command(BaseCommand):
    help = "Fixes BiodiversityRecord instances assigned to the 'Desconocido' neighborhood by finding their correct neighborhoods using spatial queries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the command without making any changes to the database",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of records to process in each batch (default: 500)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of records to process",
        )
        parser.add_argument(
            "--neighborhood-id",
            type=int,
            default=688,
            help="ID of the 'Desconocido' neighborhood (default: 688)",
        )
        parser.add_argument(
            "--stats-only",
            action="store_true",
            help="Only print stats without processing records",
        )

    def handle(self, *args, **options):  # noqa: C901
        dry_run = options.get("dry_run", False)
        batch_size = options.get("batch_size", 500)
        limit = options.get("limit")
        unknown_neighborhood_id = options.get("neighborhood_id")
        stats_only = options.get("stats_only", False)

        start_time = time.time()

        # Find all records with "Desconocido" neighborhood
        base_query = BiodiversityRecord.objects.filter(
            neighborhood_id=unknown_neighborhood_id,
            location__isnull=False,
        )

        total_records = base_query.count()
        self.stdout.write(
            f"Found {total_records} biodiversity records with unknown neighborhood"
        )

        if stats_only:
            self.stdout.write("Stats-only mode, exiting without processing records")
            return

        if total_records == 0:
            self.stdout.write(self.style.WARNING("No records found to process."))
            return

        # Apply limit if specified
        if limit:
            self.stdout.write(f"Limiting to {limit} records")
            total_to_process = min(limit, total_records)
        else:
            total_to_process = total_records

        # Get all neighborhoods with boundaries
        valid_neighborhoods = Neighborhood.objects.exclude(
            id=unknown_neighborhood_id
        ).exclude(boundary__isnull=True)

        self.stdout.write(
            f"Found {valid_neighborhoods.count()} neighborhoods with boundaries"
        )

        # Get all localities with boundaries
        valid_localities = Locality.objects.exclude(boundary__isnull=True)
        self.stdout.write(
            f"Found {valid_localities.count()} localities with boundaries"
        )

        # Get the extent of all records to filter neighborhoods
        extent = base_query.annotate(
            location_geom=Cast("location", GeometryField())
        ).aggregate(extent=Extent("location_geom"))["extent"]

        if extent:
            min_lon, min_lat, max_lon, max_lat = extent
            # Add a buffer for safety
            buffer = 0.05  # approximately 5km
            min_lon -= buffer
            min_lat -= buffer
            max_lon += buffer
            max_lat += buffer

            # Bounding box for the extent
            bbox = (
                f"POLYGON(("
                f"{min_lon} {min_lat}, "
                f"{max_lon} {min_lat}, "
                f"{max_lon} {max_lat}, "
                f"{min_lon} {max_lat}, "
                f"{min_lon} {min_lat}"
                f"))"
            )

            # Filter neighborhoods that intersect with the extent
            filtered_neighborhoods = valid_neighborhoods.filter(
                boundary__intersects=bbox
            )

            # Filter localities that intersect with the extent
            filtered_localities = valid_localities.filter(boundary__intersects=bbox)

            self.stdout.write(
                f"Filtered to {filtered_neighborhoods.count()} neighborhoods and "
                f"{filtered_localities.count()} localities within records extent"
            )
        else:
            filtered_neighborhoods = valid_neighborhoods
            filtered_localities = valid_localities
            self.stdout.write(
                "Could not determine extent, using all neighborhoods and localities"
            )

        # Create a dictionary to cache "Desconocido en X" neighborhoods
        # Key: locality_id, Value: neighborhood
        unknown_neighborhood_cache = {}

        # Statistics tracking
        updated_with_neighborhood = 0
        updated_with_locality = 0
        created_neighborhoods = 0
        non_matching_records = 0
        processed_records = 0

        # Process in batches to handle potential query size limitations
        with tqdm(total=total_to_process, desc="Processing records") as progress_bar:
            # Process records in chunks to avoid query size limitations
            for offset in range(0, total_to_process, batch_size):
                end_offset = min(offset + batch_size, total_to_process)

                # Get IDs for this batch
                batch_ids = list(
                    base_query.values_list("id", flat=True)[offset:end_offset]
                )

                # Skip empty batches
                if not batch_ids:
                    self.stdout.write(
                        f"No records found in batch {offset}-{end_offset}. Stopping."
                    )
                    break

                # Fetch full records for this batch by ID to ensure we get exactly what we want
                batch = list(BiodiversityRecord.objects.filter(id__in=batch_ids))

                # Process each record in the batch
                neighborhood_updates = {}  # record_id -> neighborhood
                system_comment_updates = {}  # record_id -> comment

                for record in batch:
                    found_match = False

                    # 1. First try to find a direct neighborhood match
                    matching_neighborhoods = list(
                        filtered_neighborhoods.filter(
                            boundary__contains=record.location
                        )
                    )

                    if matching_neighborhoods:
                        # Take the first matching neighborhood
                        neighborhood_updates[record.id] = matching_neighborhoods[0]
                        system_comment_updates[record.id] = (
                            f"Automatically assigned to neighborhood '{matching_neighborhoods[0].name}' "
                            f"based on spatial location."
                        )
                        updated_with_neighborhood += 1
                        found_match = True

                    # 2. If no neighborhood match, try to find a locality match
                    if not found_match:
                        matching_localities = list(
                            filtered_localities.filter(
                                boundary__contains=record.location
                            )
                        )

                        if matching_localities:
                            # Take the first matching locality
                            locality = matching_localities[0]

                            # Check if we already have a "Desconocido en X" neighborhood for this locality
                            if locality.id in unknown_neighborhood_cache:
                                unknown_neighborhood = unknown_neighborhood_cache[
                                    locality.id
                                ]
                            else:
                                # Try to find an existing "Desconocido en X" neighborhood
                                unknown_neighborhood_name = (
                                    f"Desconocido en {locality.name}"
                                )
                                unknown_neighborhood = Neighborhood.objects.filter(
                                    name=unknown_neighborhood_name, locality=locality
                                ).first()

                                # Create a new "Desconocido en X" neighborhood if it doesn't exist
                                if not unknown_neighborhood and not dry_run:
                                    unknown_neighborhood = Neighborhood.objects.create(
                                        name=unknown_neighborhood_name,
                                        locality=locality,
                                        boundary=None,  # No boundary for these special neighborhoods
                                    )
                                    created_neighborhoods += 1
                                    self.stdout.write(
                                        f"Created new neighborhood: {unknown_neighborhood_name}"
                                    )

                                # Cache the neighborhood for future use
                                unknown_neighborhood_cache[locality.id] = (
                                    unknown_neighborhood
                                )

                            if unknown_neighborhood:
                                neighborhood_updates[record.id] = unknown_neighborhood
                                system_comment_updates[record.id] = (
                                    f"Automatically assigned to placeholder neighborhood '{unknown_neighborhood.name}' "
                                    f"as record is within locality '{locality.name}' boundary but no matching "
                                    f"neighborhood boundary was found."
                                )
                                updated_with_locality += 1
                                found_match = True

                    if not found_match:
                        non_matching_records += 1

                # Bulk update records with their new neighborhoods and comments
                if neighborhood_updates and not dry_run:
                    with transaction.atomic():
                        for record_id, new_neighborhood in neighborhood_updates.items():
                            comment = system_comment_updates.get(record_id, "")
                            BiodiversityRecord.objects.filter(id=record_id).update(
                                neighborhood=new_neighborhood, system_comment=comment
                            )

                processed_records += len(batch)
                progress_bar.update(len(batch))

                # Print interim progress report
                if processed_records % 1000 == 0 or processed_records % batch_size == 0:
                    elapsed_time = time.time() - start_time
                    records_per_second = (
                        processed_records / elapsed_time if elapsed_time > 0 else 0
                    )
                    self.stdout.write(
                        f"Processed {processed_records}/{total_to_process} records "
                        f"({records_per_second:.2f} records/sec)"
                    )

        # Final report
        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f"Processing complete in {elapsed_time:.2f} seconds:")
        )
        self.stdout.write(f"- Total records processed: {processed_records}")
        self.stdout.write(
            f"- Records assigned to existing neighborhoods: {updated_with_neighborhood}"
        )
        self.stdout.write(
            f"- Records assigned to locality-based placeholder neighborhoods: {updated_with_locality}"
        )
        self.stdout.write(
            f"- New placeholder neighborhoods created: {created_neighborhoods}"
        )
        self.stdout.write(
            f"- Records without matching neighborhood or locality: {non_matching_records}"
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "This was a dry run. No changes were made to the database."
                )
            )
