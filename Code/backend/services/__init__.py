"""
Business service layer.

Per 01C_Product_Principles.md (AP-001 Separation of Concerns) and
06_Backend_Architecture.md Section 6:

- Views/serializers never contain business logic — they validate input,
  call a service, and return a response.
- Services never know about HTTP (no `request` objects).
- Services are the only code permitted to coordinate across models,
  DockerManager, and Celery.

Concrete services (AuthenticationService, InstanceService, ...) are
added one vertical slice at a time starting in Sprint 1.
"""
