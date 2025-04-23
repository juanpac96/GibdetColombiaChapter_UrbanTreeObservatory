# Django Backend

## Database Management

### Resetting the Database

If you encounter database schema issues after model changes (such as IntegrityErrors or missing column errors), you may need to reset the database completely. Follow these steps:

1. Stop all running containers:

   ```bash
   docker compose down
   ```

2. Run the database reset service to clear the data volume:

   ```bash
   docker compose --profile reset run db-reset
   ```

3. Remove orphaned containers to avoid conflicts:

   ```bash
   docker compose down --remove-orphans
   ```

4. Remove all volumes to ensure a clean slate:

   ```bash
   docker compose down -v
   ```

5. Rebuild and restart your application with a fresh database:

   ```bash
   docker compose up -d
   ```

This will completely destroy the existing database data and create a fresh instance. When the backend service starts up, it will run all migrations on the new empty database.

> **IMPORTANT**: If you encounter connection issues after resetting the database, try removing all containers, volumes, and networks, then rebuilding everything:
>
> ```bash
> docker compose down -v
> docker system prune -f
> docker volume prune -f
> docker compose up -d
> ```

### After Database Reset

After resetting the database, create a new superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Common Django Commands

Here are instructions for running common Django management commands using Docker Compose:

### Migrations

To create new migrations based on model changes:

```bash
docker compose exec backend python manage.py makemigrations
```

To apply pending migrations:

```bash
docker compose exec backend python manage.py migrate
```

To show migration status:

```bash
docker compose exec backend python manage.py showmigrations
```

### Django Shell

To access the Django interactive shell:

```bash
docker compose exec backend python manage.py shell
```

For the shell with IPython support (if installed):

```bash
docker compose exec backend python manage.py shell_plus
```

### Testing

To run tests:

```bash
docker compose exec backend python manage.py test
```

To run tests with coverage:

```bash
docker compose exec backend coverage run --source='.' manage.py test
docker compose exec backend coverage report
```

### Code Quality

This project uses pre-commit hooks to ensure code quality. Make sure to set up pre-commit as described in the main README. The hooks will automatically format your code, check for common issues, and ensure Django best practices are followed.

The CI pipeline runs these same checks, so setting up pre-commit locally will help prevent CI failures.

### Custom Management Commands

To run custom management commands:

```bash
docker compose exec backend python manage.py [command_name]
```
