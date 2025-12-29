# API Conventions

**Last Updated:** 2025-12-29

## REST Principles

### Resource Naming
- Use **plural nouns** for collections: `/users`, `/projects`
- Use **path parameters** for specific resources: `/users/{user_id}`
- Use **query parameters** for filtering/pagination: `/users?role=admin&limit=50`

### HTTP Methods

| Method | Purpose | Example | Idempotent? |
|--------|---------|---------|-------------|
| GET | Retrieve resource(s) | `GET /users/123` | Yes |
| POST | Create new resource | `POST /users` | No |
| PUT | Full update | `PUT /users/123` | Yes |
| PATCH | Partial update | `PATCH /users/123` | No |
| DELETE | Remove resource | `DELETE /users/123` | Yes |

---

## URL Structure

### Versioning
All endpoints prefixed with API version:
```
/api/v1/users
/api/v1/projects/{project_id}/wbes
```

### Nested Resources
Use nesting for clear relationships (max 2 levels):
```
/api/v1/projects/{project_id}/wbes/{wbe_id}/cost-elements
```

Avoid deep nesting; use query parameters instead:
```
# Good: /api/v1/cost-elements?project_id=xxx&wbe_id=yyy
# Avoid: /api/v1/projects/{id}/wbes/{id}/cost-elements
```

---

## Request/Response Format

### Content Type
- **Request:** `Content-Type: application/json`
- **Response:** `Content-Type: application/json`

### Request Body Structure

**Create/Update requests:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "viewer",
  "department": "Engineering"
}
```

### Response Structure

**Single Resource:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "viewer",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Collection:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 50
}
```

---

## Pagination

### Query Parameters
- `limit`: Number of items per page (default: 50, max: 100)
- `skip` or `offset`: Number of items to skip (default: 0)

### Response Headers
```
X-Total-Count: 150
Link: </api/v1/users?limit=50&skip=50>; rel="next"
```

---

## Filtering and Sorting

### Filtering
Use query parameters:
```
GET /api/v1/users?role=admin&is_active=true&department=Engineering
```

### Sorting
```
GET /api/v1/users?sort=created_at&order=desc
```

---

## Status Codes

### Success Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 OK | Success | GET, PUT, PATCH |
| 201 Created | Resource created | POST |
| 204 No Content | Success, no body | DELETE |

### Client Error Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 400 Bad Request | Invalid input | Validation errors |
| 401 Unauthorized | Not authenticated | Missing/invalid token |
| 403 Forbidden | Not authorized | Insufficient permissions |
| 404 Not Found | Resource doesn't exist | Invalid ID |
| 409 Conflict | Resource conflict | Duplicate email |
| 422 Unprocessable Entity | Validation failed | Pydantic validation |

### Server Error Codes

| Code | Meaning |
|------|---------|
| 500 Internal Server Error | Unexpected error |
| 503 Service Unavailable | Maintenance mode |

---

## Error Response Format

### Standard Error Structure
```json
{
  "detail": "User not found",
  "error_code": "USER_NOT_FOUND",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Validation Errors
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

---

## Authentication

### Header Format
```
Authorization: Bearer <jwt_token>
```

### Token Lifetime
- Access tokens: 30 minutes
- Refresh tokens: 7 days (future enhancement)

---

## Rate Limiting

### Limits (Future)
- Authenticated users: 1000 requests/hour
- Unauthenticated: 100 requests/hour

### Response Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1610715600
```

---

## Deprecation Policy

### Announcing Deprecation
1. Add `Deprecated: true` to OpenAPI spec
2. Add `Warning` header to responses: `Warning: 299 - "Deprecated, use /v2/endpoint"`
3. Update documentation with migration guide
4. Minimum 6 months notice before removal

---

## CORS Policy

### Allowed Origins
- Development: `http://localhost:3000`
- Production: `https://app.example.com`

### Allowed Methods
```
GET, POST, PUT, PATCH, DELETE, OPTIONS
```

### Allowed Headers
```
Content-Type, Authorization, X-Requested-With
```

---

## OpenAPI Documentation

### Auto-generation
FastAPI automatically generates:
- OpenAPI 3.0 spec at `/api/v1/openapi.json`
- Interactive docs at `/api/v1/docs` (Swagger UI)
- ReDoc at `/api/v1/redoc`

### Documentation Standards
- All endpoints must have description
- All request/response models documented via Pydantic schemas
- Examples provided for complex endpoints
