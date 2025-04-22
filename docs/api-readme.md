# Urban Tree Observatory API Documentation

## API Overview

The Urban Tree Observatory API provides access to data about urban trees in Ibagué, Colombia, including taxonomic information, geographical data, tree measurements, and observations. The API is built using Django REST Framework and follows RESTful principles.

## Authentication

The API uses JWT (JSON Web Token) authentication. To obtain a token:

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

The response will contain an access token and a refresh token:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

To use the access token, include it in the Authorization header:

```http
GET /api/v1/taxonomy/species/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```

Some endpoints are read-only and may not require authentication.

## API Endpoints

The API is organized around the following main resources:

### Taxonomy

- `GET /api/v1/taxonomy/families/` - List all plant families
- `GET /api/v1/taxonomy/families/{id}/` - Retrieve a specific family
- `GET /api/v1/taxonomy/genera/` - List all genera
- `GET /api/v1/taxonomy/genera/{id}/` - Retrieve a specific genus
- `GET /api/v1/taxonomy/species/` - List all species
- `GET /api/v1/taxonomy/species/{id}/` - Retrieve a specific species
- `GET /api/v1/taxonomy/functional-groups/` - List all functional groups
- `GET /api/v1/taxonomy/functional-groups/{id}/` - Retrieve a specific functional group
- `GET /api/v1/taxonomy/traits/` - List all traits
- `GET /api/v1/taxonomy/traits/{id}/` - Retrieve a specific trait

### Places

- `GET /api/v1/places/countries/` - List all countries
- `GET /api/v1/places/countries/{id}/` - Retrieve a specific country
- `GET /api/v1/places/departments/` - List all departments
- `GET /api/v1/places/departments/{id}/` - Retrieve a specific department
- `GET /api/v1/places/municipalities/` - List all municipalities
- `GET /api/v1/places/municipalities/{id}/` - Retrieve a specific municipality
- `GET /api/v1/places/places/` - List all places
- `GET /api/v1/places/places/{id}/` - Retrieve a specific place

### Biodiversity Records

- `GET /api/v1/biodiversity/records/` - List all biodiversity records
- `GET /api/v1/biodiversity/records/{id}/` - Retrieve a specific biodiversity record
- `GET /api/v1/biodiversity/records/near/` - List records near a specific point
- `GET /api/v1/biodiversity/records/bbox/` - List records within a bounding box

### Reports

- `GET /api/v1/reports/measurements/` - List all measurements
- `GET /api/v1/reports/measurements/{id}/` - Retrieve a specific measurement
- `GET /api/v1/reports/observations/` - List all observations
- `GET /api/v1/reports/observations/{id}/` - Retrieve a specific observation

## Query Parameters

Most list endpoints support the following query parameters:

- `search`: Search across relevant text fields
- `ordering`: Order results by specific fields (prefix with `-` for descending order)
- `page`: Page number for pagination
- `page_size`: Number of results per page (default: 20, max: 100)

### Example Queries

#### Filter species by family

```http
GET /api/v1/taxonomy/species/?genus__family=1
```

#### Search for trees by common name

```http
GET /api/v1/biodiversity/records/?search=acacia
```

#### Find trees near a location

```http
GET /api/v1/biodiversity/records/near/?lat=4.4378&lon=-75.2012&radius=500
```

#### Filter measurements by type and value range

```http
GET /api/v1/reports/measurements/?attribute=HT&value_min=10&value_max=20
```

## GeoJSON Support

The biodiversity records endpoint supports GeoJSON format:

```http
GET /api/v1/biodiversity/records/?format=geojson
```

## Pagination

The API uses page-based pagination. The response includes:

```json
{
  "count": 100,
  "next": "http://example.com/api/v1/taxonomy/species/?page=2",
  "previous": null,
  "results": [
    // Data
  ]
}
```

You can adjust the page size with the `page_size` parameter (up to 100):

```http
GET /api/v1/taxonomy/species/?page=2&page_size=50
```

## Rate Limiting

The API has rate limiting to prevent abuse. Please check the response headers for rate limit information:

- `X-RateLimit-Limit`: Maximum number of requests allowed per period
- `X-RateLimit-Remaining`: Number of requests remaining in the current period
- `X-RateLimit-Reset`: Time until the rate limit resets

## Error Handling

The API uses standard HTTP status codes to indicate success or failure:

- 200 OK: Request succeeded
- 400 Bad Request: Invalid request
- 401 Unauthorized: Authentication required
- 403 Forbidden: Permission denied
- 404 Not Found: Resource not found
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Server error

Error responses include a JSON body with details:

```json
{
  "detail": "Error message"
}
```

## Performance Considerations

Some endpoints, particularly those for biodiversity records, measurements, and observations, contain large datasets. Consider using filters to limit the results and avoid fetching too much data at once.
