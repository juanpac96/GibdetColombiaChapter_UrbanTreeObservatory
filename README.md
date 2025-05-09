# Urban Tree Observatory Project

![CI](https://github.com/OmdenaAI/GibdetColombiaChapter_UrbanTreeObservatory/workflows/CI/badge.svg)

## Project Overview

The Urban Tree Observatory is a data-driven platform for monitoring and conserving urban trees in Ibagué, Colombia. The project centralizes tree data and tracks conservation efforts.

## Development Environment Setup

### Prerequisites

- Docker and Docker Compose
- Git

### Getting Started

1. Clone this repository:

   ```bash
   git clone https://github.com/OmdenaAI/GibdetColombiaChapter_UrbanTreeObservatory
   cd GibdetColombiaChapter_UrbanTreeObservatory
   ```

2. Start the development environment:

   ```bash
   docker compose up
   ```

3. Access the different components:
   - Django backend: <http://localhost:8000/>
   - Django admin: <http://localhost:8000/admin/>
   - Angular frontend: <http://localhost:4200/>
   - PostgreSQL database: localhost:5432
   - PgAdmin: <http://localhost:5050/>

### Setting up PgAdmin

To connect to the database through PgAdmin:

1. Go to <http://localhost:5050/browser/>
2. Login with:
   - Email: <admin@omdena.com>
   - Password: admin
3. Right-click on "Servers" and select "Register > Server"
4. In the General tab, name it "Local PostgreSQL"
5. In the Connection tab, enter:
   - Host: db
   - Port: 5432
   - Database: urban_tree_db
   - Username: postgres
   - Password: postgres

### First-Time Setup

After starting the containers for the first time, you'll need to create a superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

### Initial Data Import

To import initial data into the database:

1. Download the latest version of the CSV snd JSON files from the project's shared Google Drive.
2. Save the CSV files to `backend/data/csv` and the JSON files to `backend/data/json`.
3. Run the import command:

   ```bash
   docker compose exec backend python manage.py import_initial_data --local-dir=data
   ```

## Project Structure

### Backend (Django REST API)

- `backend/` - Django project
  - `config/` - Django project settings
  - `apps/` - Django apps
    - `core/` - Core functionality
    - `users/` - User management
    - `places/` - Geographic locations and spatial data
    - `taxonomy/` - Family, genus, and species management
    - `biodiversity/` - Tree data management with GIS
    - `reports/` - Tree measurements and observations
    - `climate/` - Climate data management

### Frontend (Angular)

- `frontend/` - Angular application
  - `src/app/` - Angular components and modules
    - `core/` - Core functionality
    - `shared/` - Shared components
    - `features/` - Feature modules
      - `map/` - Map visualization
      - `trees/` - Tree management interfaces
      - `reports/` - Reporting interface
      - `analysis/` - Data analysis dashboards

### Database

- PostgreSQL with PostGIS for geospatial data

## Development Workflow

1. Run the application with Docker Compose
2. Make changes to your code (the development server will auto-reload)
3. Run tests to verify your changes
4. Commit and push your changes

### Setting up Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. To set up pre-commit:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

Pre-commit will now run automatically on every commit. You can also run it manually:

```bash
pre-commit run --all-files
```

### Running Tests

```bash
# Backend tests
docker compose exec backend pytest

# Backend tests with coverage
docker compose exec backend pytest --cov=. --cov-config=.coveragerc

# Frontend tests
docker compose exec frontend ng test
```

## API Documentation

The API documentation is available at:

- Swagger UI: <http://localhost:8000/api/v1/swagger/>
- ReDoc: <http://localhost:8000/api/v1/redoc/>
