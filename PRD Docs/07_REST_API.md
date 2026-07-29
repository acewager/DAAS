# Desktop Cloud Platform
# REST API Specification

**Document Version:** 1.0.0

**Product Version:** MVP (v1.0.0)

**Status:** Approved

**Depends On:**
- 01A_Executive_Summary.md
- 01B_Product_Overview.md
- 01C_Product_Principles.md
- 01D_Development_Roadmap.md
- 02_System_Architecture.md
- 03_Database_Design.md
- 04_Authentication_and_Security.md
- 05_Container_Architecture.md
- 06_Backend_Architecture.md

**Cross References:**
- AuthenticationService
- InstanceService
- DockerManager
- EventLogService
- Database Schema

---

# Table of Contents

1. API Overview
2. API Design Principles
3. Versioning Strategy
4. Authentication
5. Standard Request & Response Format
6. Error Handling
7. Endpoint Groups
8. Authentication Endpoints
9. Template Endpoints
10. Instance Endpoints
11. Software Request Endpoints
12. Analytics Endpoints
13. Event Log Endpoints
14. Administration Endpoints
15. Pagination & Filtering
16. Idempotency
17. API Security
18. Future API Expansion

---

# 1. API Overview

The Desktop Cloud Platform exposes all functionality through a REST API.

The React frontend communicates exclusively with these APIs.

The backend does not render HTML.

All endpoints are JSON-based.

Base URL:

```
/api/v1
```

Future versions will use:

```
/api/v2
/api/v3
```

---

# 2. API Design Principles

The API follows these principles:

- Resource-oriented
- Predictable URLs
- Standard HTTP methods
- Stateless requests
- Consistent response format
- Secure by default

---

# 3. Versioning Strategy

Current version:

```
/api/v1
```

Breaking changes require a new version.

Non-breaking additions remain within the current version.

---

# 4. Authentication

Authentication uses secure Django session cookies.

Example flow:

```mermaid
sequenceDiagram

User->>React: Login

React->>POST /api/v1/auth/login

REST API-->>Browser: Session Cookie

Browser->>GET /api/v1/instances

REST API-->>Browser: Instance List
```

---

# 5. Standard Request & Response Format

## Success Response

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}
```

---

## Error Response

```json
{
  "success": false,
  "error": {
    "code": "INSTANCE_NOT_FOUND",
    "message": "The requested instance does not exist."
  }
}
```

---

# 6. Error Handling

| HTTP Status | Meaning |
|------------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (Background Job) |
| 204 | No Content |
| 400 | Validation Error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Business Rule Failed |
| 500 | Internal Error |

---

# 7. Endpoint Groups

The API is divided into business domains.

| Domain | Prefix |
|---------|--------|
| Authentication | /auth |
| Users | /users |
| Templates | /templates |
| Instances | /instances |
| Analytics | /analytics |
| Software Requests | /software-requests |
| Event Logs | /events |
| Administration | /admin |

---

# 8. Authentication Endpoints

## Register

```
POST /api/v1/auth/register
```

Creates a new user account.

Authentication Required:

No

---

## Login

```
POST /api/v1/auth/login
```

Authentication Required:

No

Returns:

- Session Cookie

---

## Logout

```
POST /api/v1/auth/logout
```

Authentication Required:

Yes

---

## Current User

```
GET /api/v1/auth/me
```

Returns the currently authenticated user's profile.

---

# 9. Template Endpoints

## List Templates

```
GET /api/v1/templates
```

Returns all enabled templates.

---

## Template Details

```
GET /api/v1/templates/{id}
```

---

## Admin Create Template

```
POST /api/v1/templates
```

Admin Only

---

## Update Template

```
PUT /api/v1/templates/{id}
```

Admin Only

---

## Delete Template

```
DELETE /api/v1/templates/{id}
```

Admin Only

---

# 10. Instance Endpoints

## List Instances

```
GET /api/v1/instances
```

Returns all instances owned by the authenticated user.

---

## Create Instance

```
POST /api/v1/instances
```

Returns:

```
202 Accepted
```

Provisioning occurs asynchronously.

---

## Get Instance

```
GET /api/v1/instances/{id}
```

---

## Start Instance

```
POST /api/v1/instances/{id}/start
```

---

## Stop Instance

```
POST /api/v1/instances/{id}/stop
```

---

## Restart Instance

```
POST /api/v1/instances/{id}/restart
```

---

## Delete Instance

```
DELETE /api/v1/instances/{id}
```

---

## Desktop Launch

```
GET /api/v1/instances/{id}/launch
```

Returns:

Desktop launch URL.

---

# 11. Software Request Endpoints

## Create Request

```
POST /api/v1/software-requests
```

---

## List Requests

```
GET /api/v1/software-requests
```

---

## Request Details

```
GET /api/v1/software-requests/{id}
```

---

## Approve Request

```
POST /api/v1/software-requests/{id}/approve
```

Admin Only

---

## Reject Request

```
POST /api/v1/software-requests/{id}/reject
```

Admin Only

---

# 12. Analytics Endpoints

## Dashboard Statistics

```
GET /api/v1/analytics/dashboard
```

---

## Instance Usage

```
GET /api/v1/analytics/instances/{id}
```

---

## User Statistics

```
GET /api/v1/analytics/user
```

---

# 13. Event Log Endpoints

## My Event History

```
GET /api/v1/events
```

---

## Event Details

```
GET /api/v1/events/{id}
```

---

# 14. Administration Endpoints

## Users

```
GET /api/v1/admin/users
```

Admin Only

---

## Platform Analytics

```
GET /api/v1/admin/analytics
```

---

## Active Instances

```
GET /api/v1/admin/instances
```

---

## Event Logs

```
GET /api/v1/admin/events
```

---

## System Health

```
GET /api/v1/admin/health
```

---

# 15. Pagination & Filtering

List endpoints should support:

```
?page=1

?page_size=20

?ordering=created_at

?search=ubuntu

?status=running
```

Default page size:

20

Maximum page size:

100

---

# 16. Idempotency

The following operations should be idempotent:

- Start Instance
- Stop Instance
- Restart Instance
- Delete Instance (if already deleted)

Repeated requests should not produce inconsistent state.

---

# 17. API Security

Every protected endpoint must:

- Validate authentication
- Validate authorization
- Validate ownership
- Validate request payload
- Log significant actions

Rate limiting should be applied to:

- Login
- Registration
- Password reset
- Instance creation

---

# 18. Future API Expansion

Future API capabilities:

- API Tokens
- Public REST API
- GraphQL
- WebSocket Events
- CLI Support
- Mobile API
- Bulk Operations
- Project APIs

---

# Acceptance Criteria

The REST API specification is complete when:

- All business domains are documented.
- Standard request and response formats are defined.
- Endpoint groups are established.
- Authentication flow is documented.
- Error handling is standardized.
- Pagination strategy is documented.
- Security requirements are defined.
- Future expansion is considered.

---

# End of Document