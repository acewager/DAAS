# Desktop Cloud Platform
# Coding Standards & Engineering Guidelines

**Document Version:** 1.0.0

**Product Version:** MVP (v1.0.0)

**Status:** Approved

**Depends On:**
- All Architecture Documents
- REST API Specification
- Database Design
- Frontend Architecture
- Backend Architecture

---

# Table of Contents

1. Purpose
2. Engineering Principles
3. Repository Structure
4. Python & Django Standards
5. React & TypeScript Standards
6. API Design Standards
7. Database Standards
8. Docker Standards
9. Git Workflow
10. Commit Message Standards
11. Code Review Checklist
12. AI Development Rules
13. Documentation Standards
14. Definition of Done
15. Future Improvements

---

# 1. Purpose

This document defines the engineering standards for the Desktop Cloud Platform.

Its goals are to:

- Ensure consistent code quality.
- Reduce technical debt.
- Make AI-generated code predictable.
- Improve maintainability.
- Enable multiple developers to work consistently.

These standards apply to all contributors, whether human or AI.

---

# 2. Engineering Principles

The platform follows these principles:

- Keep solutions simple.
- Prefer readability over cleverness.
- Follow the Single Responsibility Principle.
- Minimize dependencies.
- Fail safely.
- Write code for maintainability.
- Design for future scalability without premature optimization.

---

# 3. Repository Structure

The repository should be organized into clear top-level directories.

```
backend/
frontend/
docker/
docs/
scripts/
deployment/
```

Each directory should have a focused responsibility.

Avoid placing unrelated files together.

---

# 4. Python & Django Standards

## Language

- Python 3.12+
- Django LTS
- Django REST Framework

### Code Style

- Follow PEP 8.
- Use Black for formatting.
- Use Ruff for linting.
- Use type hints where practical.

### Project Structure

Separate concerns into:

- Models
- Serializers
- Views
- Services
- Tasks
- Utilities

Business logic belongs in the Service layer.

Views should remain thin.

Models should not contain orchestration logic.

---

# 5. React & TypeScript Standards

## Language

- TypeScript only.
- No JavaScript files.

## Components

- Functional components only.
- One component per file.
- Use hooks instead of class components.

### State

Use:

- React Context for global application state.
- TanStack Query for server state.
- Local component state for UI interactions.

Avoid unnecessary global state.

---

# 6. API Design Standards

REST principles must be followed.

Guidelines:

- Resource-oriented endpoints.
- Predictable URLs.
- Consistent response formats.
- Proper HTTP status codes.
- No business logic in controllers.

Validation occurs on both the client and server.

---

# 7. Database Standards

Database changes must always use Django migrations.

Rules:

- Never modify production tables manually.
- Never delete migrations already applied.
- Use foreign keys instead of duplicated data.
- Prefer explicit relationships.
- Avoid nullable fields unless justified.

Database schema changes require updates to the documentation.

---

# 8. Docker Standards

Container images should:

- Use official base images where possible.
- Run as non-root users.
- Minimize image size.
- Pin image versions.
- Define resource limits.

Desktop templates should remain immutable after release.

---

# 9. Git Workflow

Primary branch:

```
main
```

Development branch:

```
develop
```

Feature branches:

```
feature/<feature-name>
```

Bug fixes:

```
fix/<issue-name>
```

Hotfixes:

```
hotfix/<issue-name>
```

Merge requests should require review before merging.

---

# 10. Commit Message Standards

Follow the Conventional Commits specification.

Examples:

```
feat: add instance provisioning service

fix: resolve Traefik routing issue

docs: update deployment guide

refactor: simplify DockerManager

test: add API integration tests

chore: update dependencies
```

Commit messages should describe **why** a change was made, not just what changed.

---

# 11. Code Review Checklist

Every pull request should verify:

- Code follows project architecture.
- Tests pass.
- Documentation is updated.
- No unnecessary dependencies introduced.
- Security implications reviewed.
- Performance considerations evaluated.
- Naming conventions followed.
- Error handling implemented.
- Logging added where appropriate.

---

# 12. AI Development Rules

AI coding agents are expected to follow these rules without exception.

## Architecture

- Respect the documented architecture.
- Do not introduce new architectural patterns without approval.
- Do not bypass the Service layer.
- Do not place business logic inside views or React components.

## Vertical Slice Development

Implement features one complete slice at a time.

Each slice should include:

- Backend
- API
- Database (if needed)
- Frontend
- Tests
- Documentation updates

Avoid implementing half-finished features across multiple slices.

## Dependencies

Do not introduce new third-party libraries without approval.

Prefer built-in framework capabilities whenever practical.

## Database

Never modify models without creating migrations.

Update database documentation when schema changes.

## Security

Never expose secrets.

Never disable authentication or authorization.

Always validate user input.

## Testing

Every new feature should include appropriate tests.

Do not remove tests without approval.

## Documentation

When implementing architectural changes:

- Update relevant markdown documentation.
- Keep diagrams synchronized where applicable.

---

# 13. Documentation Standards

Documentation is part of the codebase.

Requirements:

- Keep documents versioned.
- Update documentation with architectural changes.
- Use Markdown.
- Include diagrams where helpful.
- Cross-reference related documents.

Documentation should be understandable without reading the source code.

---

# 14. Definition of Done

A feature is considered complete only when:

- Requirements implemented.
- Code reviewed.
- Tests pass.
- Documentation updated.
- Logging implemented.
- Error handling completed.
- Security reviewed.
- API documented.
- Database migrations included (if required).
- Frontend integrated.
- No known blocking defects remain.

---

# 15. Future Improvements

Future engineering practices may include:

- Automated code formatting in CI.
- Static analysis gates.
- Dependency vulnerability scanning.
- Architecture compliance checks.
- Automated documentation generation.
- AI-assisted code review.
- Performance regression testing.

These improvements should enhance, not replace, the engineering standards defined in this document.

---

# Acceptance Criteria

The coding standards are complete when:

- Engineering principles are documented.
- Language-specific standards are defined.
- Repository structure is established.
- Git workflow is documented.
- AI development rules are explicit.
- Documentation expectations are defined.
- Definition of Done is established.

---

# End of Document