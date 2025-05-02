# Fix BiodiversityRecord Neighborhoods

This document explains how to use the `fix_biodiversity_neighborhoods` command to fix biodiversity records that are incorrectly assigned to a default "unknown" neighborhood (ID 688, name="Desconocido").

## Problem Description

We have 5,707 biodiversity records that contain valid geographic location data (longitude/latitude points) but are incorrectly associated with a default neighborhood with ID 688 (name="Desconocido", no boundary). These records need to be reassigned to their correct neighborhoods based on their geographic coordinates.

## Command Overview

The `fix_biodiversity_neighborhoods` command uses spatial queries to efficiently:

- Find biodiversity records with unknown neighborhoods
- Determine which neighborhood's boundary contains each record's location
- Update records with their correct neighborhood assignment

## Usage

### Development Environment

```bash
docker compose exec backend python manage.py fix_biodiversity_neighborhoods [options]
```

### Production Environment

```bash
python manage.py fix_biodiversity_neighborhoods [options]
```

### Command Options

The command supports these options:

- `--dry-run`: Run the command without making database changes (simulation mode)
- `--limit N`: Process only N records (useful for testing)
- `--neighborhood-id ID`: Specify the ID of the unknown neighborhood (default: 688)
- `--batch-size N`: Process N records at a time (default: 500)
- `--stats-only`: Only display statistics without processing records
- `--all-records`: Process all records with unknown neighborhood, even if they have already been processed previously

## Recommended Approach

For a production environment with 5,707 records, follow these steps:

1. First, run in stats-only mode to confirm the number of records:

   ```bash
   docker compose exec backend python manage.py fix_biodiversity_neighborhoods --stats-only
   ```

2. Run a test with a small batch in dry-run mode:

   ```bash
   docker compose exec backend python manage.py fix_biodiversity_neighborhoods --limit 100 --dry-run
   ```

3. If the test looks good, process a small batch for real:

   ```bash
   docker compose exec backend python manage.py fix_biodiversity_neighborhoods --limit 100
   ```

4. Check the results in the admin panel or database.

5. Process all records:

   ```bash
   docker compose exec backend python manage.py fix_biodiversity_neighborhoods
   ```

6. For very large datasets, consider running in smaller batches or adjusting the batch size:

   ```bash
   docker compose exec backend python manage.py fix_biodiversity_neighborhoods --batch-size 200
   ```

## How It Works

The command follows this multi-step approach:

1. **Neighborhood Matching**: First attempts to find which neighborhood's boundary contains each record's point location
2. **Locality Fallback**: If no neighborhood match is found, checks if the point falls within a locality boundary
3. **Placeholder Creation**: For locality matches, creates or reuses a "Desconocido en [LOCALITY_NAME]" neighborhood
4. **Record Update**: Updates records with their proper neighborhood and adds a system comment explaining the change
5. **No-Match Handling**: Records that don't match any geographic boundary remain unchanged

The command uses batch processing and spatial optimizations to efficiently handle large numbers of records.

## Smart Record Processing

The command is designed to be run multiple times without duplicating work:

1. **Tracking Processed Records**: All processed records receive a `system_comment` explaining what was done, whether they were:

   - Assigned to a neighborhood
   - Assigned to a locality-based placeholder neighborhood
   - Found to have no matching geographic boundary

2. **Default Behavior**: By default, the command only processes records that don't have a `system_comment` yet, skipping already processed records.
3. **Reprocessing Option**: If you need to reprocess all records (e.g., after adding new neighborhood boundaries), use the `--all-records` flag.

This design ensures you can safely run the command multiple times without worrying about duplicate processing.

## Expected Output

The command will output:

- Total records found matching the criteria
- Number of neighborhoods and localities with boundaries found
- Number of records processed
- Number of records assigned to existing neighborhoods
- Number of records assigned to locality-based placeholder neighborhoods
- Number of new placeholder neighborhoods created
- Number of records that couldn't be matched to any boundary
- Processing time and performance metrics

## System Comments

The command adds detailed system comments to each updated record explaining what was done:

1. For direct neighborhood matches:

   ```text
   "Automatically assigned to neighborhood 'X' based on spatial location."
   ```

2. For locality-based placeholder neighborhoods:

   ```text
   "Automatically assigned to placeholder neighborhood 'Desconocido en Y' as record is within
   locality 'Y' boundary but no matching neighborhood boundary was found."
   ```

## Troubleshooting

If you encounter issues:

1. **Memory Errors**: Reduce the batch size with `--batch-size`
2. **Slow Performance**: The operation is CPU and I/O intensive. Consider running during off-peak hours
3. **No Neighborhoods Found**: Ensure your neighborhood data includes proper MultiPolygon boundaries
4. **Records Not Updated**: Use `--dry-run` to debug without making changes

## After Running

After running the command, you should:

1. Verify the results by checking a sample of the updated records
2. Check the remaining records that couldn't be matched (they may need manual fixing)
3. Consider creating a fallback strategy for records that still have no proper neighborhood

## Database Backup

Always back up your database before running data migration commands like this in production.
