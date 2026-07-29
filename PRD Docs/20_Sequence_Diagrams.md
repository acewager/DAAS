# Desktop Cloud Platform
# Sequence Diagrams

**Document Version:** 1.0.0

**Product Version:** MVP

**Status:** Approved

---

# Table of Contents

1. Purpose
2. Diagram Standards
3. User Registration
4. User Login
5. Create Instance
6. Start Instance
7. Launch Desktop
8. Stop Instance
9. Delete Instance
10. Software Installation Request
11. Admin Software Installation
12. Auto Stop Workflow
13. Event Logging
14. Future Workflows

---

# 1. Purpose

This document defines the runtime interaction between the platform components.

These diagrams complement the architecture documentation and serve as implementation references for developers and AI coding agents.

---

# 2. Diagram Standards

Participants:

- User
- React Frontend
- Django Backend
- Service Layer
- Celery
- Docker Engine
- PostgreSQL
- Redis
- Traefik
- Desktop Container

All diagrams use Mermaid sequence syntax.

---

# 3. User Registration

```mermaid
sequenceDiagram

actor User

participant React

participant Django

participant PostgreSQL

User->>React: Fill registration form

React->>Django: POST /register

Django->>PostgreSQL: Validate uniqueness

PostgreSQL-->>Django: OK

Django->>PostgreSQL: Create user

PostgreSQL-->>Django: Success

Django-->>React: Registration successful

React-->>User: Redirect to Login
```

---

# 4. User Login

```mermaid
sequenceDiagram

actor User

participant React

participant Django

participant PostgreSQL

User->>React: Enter credentials

React->>Django: POST /login

Django->>PostgreSQL: Validate credentials

PostgreSQL-->>Django: User found

Django-->>React: Session Cookie

React-->>User: Dashboard
```

---

# 5. Create Instance

```mermaid
sequenceDiagram

actor User

participant React

participant Django

participant Service

participant PostgreSQL

participant Celery

participant Docker

participant Traefik

User->>React: Submit Instance Form

React->>Django: POST /instances

Django->>Service: Validate request

Service->>PostgreSQL: Save pending instance

Service->>Celery: Queue provisioning

Celery->>Docker: Create container

Docker-->>Celery: Container created

Celery->>Traefik: Register routing labels

Celery->>PostgreSQL: Update status

Celery-->>React: Instance Ready
```

---

# 6. Start Instance

```mermaid
sequenceDiagram

actor User

participant React

participant Django

participant Service

participant Docker

User->>React: Start Instance

React->>Django: POST /start

Django->>Service: Validate ownership

Service->>Docker: Start container

Docker-->>Service: Running

Service-->>React: Success
```

---

# 7. Launch Desktop

```mermaid
sequenceDiagram

actor User

participant Browser

participant React

participant Django

participant Traefik

participant Container

User->>React: Launch Desktop

React->>Django: Request desktop token

Django-->>React: Session validated

Browser->>Traefik: Access hashed subdomain

Traefik->>Container: Forward request

Container-->>Browser: noVNC Desktop
```

---

# 8. Stop Instance

```mermaid
sequenceDiagram

actor User

participant React

participant Django

participant Docker

User->>React: Stop Instance

React->>Django: POST /stop

Django->>Docker: Stop container

Docker-->>Django: Success

Django-->>React: Updated status
```

---

# 9. Delete Instance

```mermaid
sequenceDiagram

actor User

participant React

participant Django

participant Service

participant Celery

participant Docker

participant PostgreSQL

User->>React: Delete Instance

React->>Django: DELETE /instance

Django->>Service: Validate ownership

Service->>Celery: Queue deletion

Celery->>Docker: Remove container

Docker-->>Celery: Deleted

Celery->>PostgreSQL: Delete record

Celery-->>React: Success
```

---

# 10. Software Installation Request

```mermaid
sequenceDiagram

actor User

participant React

participant Django

participant PostgreSQL

User->>React: Submit request

React->>Django: POST /software-request

Django->>PostgreSQL: Save request

PostgreSQL-->>Django: Success

Django-->>React: Request Submitted
```

---

# 11. Admin Software Installation

```mermaid
sequenceDiagram

actor Admin

participant React

participant Django

participant Celery

participant Docker

participant PostgreSQL

Admin->>React: Approve request

React->>Django: Approve API

Django->>Celery: Queue install

Celery->>Docker: Install software

Docker-->>Celery: Complete

Celery->>PostgreSQL: Update request

Celery-->>React: Installed
```

---

# 12. Auto Stop Workflow

```mermaid
sequenceDiagram

participant Scheduler

participant PostgreSQL

participant Celery

participant Docker

Scheduler->>PostgreSQL: Find idle instances

PostgreSQL-->>Scheduler: Idle list

Scheduler->>Celery: Queue stop

Celery->>Docker: Stop container

Docker-->>Celery: Success

Celery->>PostgreSQL: Update state
```

---

# 13. Event Logging

```mermaid
sequenceDiagram

participant Service

participant PostgreSQL

Service->>PostgreSQL: Save Event Log

PostgreSQL-->>Service: Success
```

Every important operation should create an Event Log entry.

Examples:

- Login
- Logout
- Instance Created
- Instance Started
- Instance Stopped
- Instance Deleted
- Software Request
- Admin Actions

---

# 14. Future Workflows

Reserved for:

- Billing
- Multi-host scheduling
- Kubernetes orchestration
- Team workspaces
- Snapshots
- Volume migration
- Firecracker provisioning
- API token authentication
- OAuth
- Marketplace deployments

---

# Sequence Diagram Principles

Every major feature added to the platform should include a corresponding sequence diagram.

Sequence diagrams are considered part of the architecture documentation.

---

# End of Document