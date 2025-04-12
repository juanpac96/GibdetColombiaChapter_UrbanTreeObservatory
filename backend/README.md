# Django Backend

## Database Management

### Resetting the Database

If you encounter database schema issues after model changes (such as IntegrityErrors or missing column errors), you may need to reset the database completely. Follow these steps:

1. Stop all running containers:

   ```bash
   docker-compose down
   ```

2. Run the database reset service to clear the data volume:

   ```bash
   docker-compose --profile reset run db-reset
   ```

3. Restart your application with a fresh database:

   ```bash
   docker-compose up -d
   ```

This will completely destroy the existing database data and create a fresh instance. When the backend service starts up, it will run all migrations on the new empty database.

### After Database Reset

After resetting the database, create a new superuser:

```bash
docker-compose exec backend python manage.py createsuperuser
```

## Common Django Commands

Here are instructions for running common Django management commands using Docker Compose:

### Migrations

To create new migrations based on model changes:

```bash
docker-compose exec backend python manage.py makemigrations
```

To apply pending migrations:

```bash
docker-compose exec backend python manage.py migrate
```

To show migration status:

```bash
docker-compose exec backend python manage.py showmigrations
```

### Django Shell

To access the Django interactive shell:

```bash
docker-compose exec backend python manage.py shell
```

For the shell with IPython support (if installed):

```bash
docker-compose exec backend python manage.py shell_plus
```

### Testing

To run tests:

```bash
docker-compose exec backend python manage.py test
```

To run tests with coverage:

```bash
docker-compose exec backend coverage run --source='.' manage.py test
docker-compose exec backend coverage report
```

### Custom Management Commands

To run custom management commands:

```bash
docker-compose exec backend python manage.py [command_name]
```
