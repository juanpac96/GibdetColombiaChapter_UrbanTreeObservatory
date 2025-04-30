# GeoDjango Admin Map Customization

This document explains the customizations made to the Django admin interface to properly display geographic data (MultiPolygon geometries) on OpenStreetMap in the Django admin.

## Overview

The Urban Tree Observatory project uses GeoDjango and django-leaflet to manage and display geographic data. While the project is primarily API-focused, the admin interface has been customized to provide better visualization of geographic data, particularly for polygon and multipolygon fields.

## Components

### 1. Admin Class Customization (`places/admin.py`)

We've replaced the standard `ModelAdmin` with `LeafletGeoAdmin` for models with geometry fields. This provides:

- Interactive maps for editing geographic data
- Custom settings for each model to ensure appropriate zoom levels and centering
- Consistent use of OpenStreetMap tiles

Each `LeafletGeoAdmin` class includes:

- `settings_overrides` to customize the map display per model type
- Appropriate zoom levels for different geographic scopes (country, department, municipality, etc.)

### 2. Leaflet Configuration (`settings/base.py`)

The `LEAFLET_CONFIG` dictionary in settings configures the behavior of all Leaflet maps:

```python
LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (4.4378, -75.2012),  # Ibagué, Colombia
    "DEFAULT_ZOOM": 13,
    "ATTRIBUTION_PREFIX": "Urban Tree Observatory",
    "TILES": [
        (
            "OpenStreetMap",
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            },
        ),
    ],
    "PLUGINS": {
        "forms": {"auto-include": True},
        "draw": {"auto-include": True},
    },
    "SCALE": 'both',
    "MINIMAP": False,
    "RESET_VIEW": False,
    "NO_GLOBALS": False,
    "FORCE_IMAGE_PATH": True,
    "MAX_ZOOM": 18,
    "MIN_ZOOM": 3,
    "DEFAULT_PRECISION": 6,
}
```

This configuration:

- Sets default map center to Ibagué, Colombia
- Uses OpenStreetMap as the base layer
- Enables drawing tools for polygon creation/editing
- Adds a scale indicator
- Sets zoom limits

### 3. Custom CSS (`static/css/leaflet_admin.css`)

Although this is primarily an API-only project, we've added custom CSS to enhance the visualization of polygons in the admin:

```css
/* Make polygons more visible */
.leaflet-interactive {
    stroke: #2200ff !important;
    stroke-width: 3 !important;
    stroke-opacity: 0.8 !important;
    fill-opacity: 0.2 !important;
    fill: #4d7cff !important;
}

/* Make the map container better sized */
.leaflet-container {
    min-height: 500px !important;
    width: 100% !important;
}
```

This CSS makes polygon boundaries thicker and more visible with better coloring.

### 4. Custom Admin Template (`templates/admin/base_site.html`)

To include our custom CSS, we've created a simple template extension:

```html
{% extends "admin/base_site.html" %}
{% load static %}

{% block extrahead %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="{% static 'css/leaflet_admin.css' %}" />
{% endblock %}
```

This extends the default admin template and adds our custom CSS.

## Why These Customizations?

1. **Problem**: By default, GeoDjango displays MultiPolygon geometries as simple shapes on a "NASA Worldview base image" instead of OpenStreetMap.

2. **Solution**: Custom admin classes and Leaflet configuration ensure that:
   - All geometry types (including MultiPolygon) display on OpenStreetMap
   - Polygons have better visibility with enhanced styling
   - Each geographic level has appropriate default zoom

## Maintenance Notes

If you need to modify how geographic data is displayed in the admin:

1. **To change map appearance**: Edit `static/css/leaflet_admin.css`
2. **To change default map settings**: Modify `LEAFLET_CONFIG` in `settings/base.py`
3. **To adjust model-specific settings**: Edit the `settings_overrides` in each admin class in `places/admin.py`

### Docker Environment

When running in Docker:

1. Static files are automatically handled by the development server in debug mode
2. For production deployment, the entrypoint script handles running `collectstatic`
3. Static files are stored in mounted volumes to persist between container restarts

No manual `collectstatic` command is needed in the Docker environment.

## Technical Details

### Directory Structure

```text
backend/
├── static/
│   └── css/
│       └── leaflet_admin.css      # Custom CSS for admin maps
├── templates/
│   └── admin/
│       └── base_site.html         # Custom admin template to include CSS
├── apps/
│   └── places/
│       └── admin.py               # Customized admin classes
├── config/
│   └── settings/
│       └── base.py                # Contains LEAFLET_CONFIG
├── docker-entrypoint.sh           # Script that runs on container startup
└── Dockerfile                     # Docker build configuration
```

### Docker Configuration

The project is configured to run in Docker with the following setup:

1. **Volumes**:
   - `static_volume`: Persists collected static files
   - `media_volume`: Persists uploaded media files

2. **Environment Variables**:
   - `STATIC_ROOT`: Set to `/app/staticfiles` in the container
   - `MEDIA_ROOT`: Set to `/app/media` in the container

3. **Entrypoint Script**:
   - Automatically runs migrations
   - Collects static files in production mode (`DEBUG=0`)
   - Starts the Django development server

### Key Dependencies

- **django-leaflet**: Provides integration between Django and Leaflet.js
- **GeoDjango**: Django's built-in geographic framework that depends on:
  - PostGIS database extension
  - GDAL/OGR libraries

### Best Practices

1. **Keep CSS minimal**: Only override what's necessary to maintain compatibility with future django-leaflet versions
2. **Separate concerns**: Use `settings_overrides` for model-specific customizations
3. **Static file organization**: Keep admin customizations separate from frontend assets

## Troubleshooting

If maps aren't displaying correctly:

1. Check browser console for JavaScript errors
2. Verify that collectstatic has run successfully
3. Ensure PostGIS is properly installed and configured
4. Verify that geometry fields contain valid data
5. Check that GDAL libraries are properly installed

## References

- [Django-leaflet Documentation](https://django-leaflet.readthedocs.io/)
- [GeoDjango Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/gis/)
- [Leaflet.js Documentation](https://leafletjs.com/reference.html)
