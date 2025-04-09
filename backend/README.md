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
