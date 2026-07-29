# Desktop Cloud Platform
# AI Development Agent Instructions

**Document Version:** 1.0.0

**Product Version:** MVP

**Audience**
- AI Coding Agents
- Human Developers
- Technical Reviewers

---

# Table of Contents

1. Purpose
2. Mission
3. Project Philosophy
4. Required Reading Order
5. Non-Negotiable Rules
6. Development Workflow
7. Vertical Slice Development
8. Architecture Rules
9. Backend Rules
10. Frontend Rules
11. Docker Rules
12. Database Rules
13. Security Rules
14. API Rules
15. Testing Rules
16. Documentation Rules
17. Code Quality Rules
18. Performance Rules
19. Git Rules
20. Communication Rules
21. When To Ask Questions
22. Forbidden Actions
23. Definition of Complete
24. AI Session Startup Prompt
25. AI Session End Checklist

---

# 1. Purpose

This document defines how AI coding agents must behave while contributing to the Desktop Cloud Platform.

The objective is to ensure:

- Consistent architecture
- Predictable code quality
- Minimal technical debt
- Incremental development
- Long-term maintainability

This document overrides any AI assumptions that conflict with the documented architecture.

---

# 2. Mission

The AI agent's mission is to:

- Build reliable software.
- Respect documented architecture.
- Prefer maintainability over speed.
- Complete one feature at a time.
- Never compromise security.

The objective is **not** to generate the maximum amount of code.

The objective is to generate the **correct** code.

---

# 3. Project Philosophy

Always optimize for:

1. Simplicity
2. Maintainability
3. Readability
4. Security
5. Scalability

Never optimize prematurely.

---

# 4. Required Reading Order

Before implementing any feature, review these documents in order:

1. Product Overview
2. Architecture
3. Database Design
4. Backend Architecture
5. REST API
6. Frontend Architecture
7. Coding Standards
8. Architecture Decision Record

Never implement features that conflict with these documents.

---

# 5. Non-Negotiable Rules

The AI must NEVER:

- Skip validation.
- Skip authentication.
- Skip authorization.
- Ignore documented architecture.
- Ignore coding standards.
- Introduce unnecessary dependencies.
- Modify production data manually.
- Hardcode secrets.
- Expose passwords.
- Bypass the Service Layer.

These rules are mandatory.

---

# 6. Development Workflow

Every task follows the same workflow.

Step 1

Understand the requested feature.

Step 2

Locate the relevant documentation.

Step 3

Determine affected components.

Step 4

Identify impacted APIs.

Step 5

Determine database changes.

Step 6

Plan implementation.

Step 7

Implement.

Step 8

Write tests.

Step 9

Update documentation.

Step 10

Verify completion.

Never skip planning.

---

# 7. Vertical Slice Development

Every feature should be implemented completely before starting another.

A slice includes:

- Database
- Backend
- API
- Frontend
- Tests
- Documentation

Never leave partially implemented features.

---

# 8. Architecture Rules

Respect all architectural layers.

Frontend

↓

REST API

↓

Service Layer

↓

Repositories / ORM

↓

Database

Business logic belongs only in the Service Layer.

Views should remain thin.

React components should remain presentational.

---

# 9. Backend Rules

Preferred order:

Models

↓

Services

↓

Serializers

↓

Views

↓

Tasks

↓

Tests

↓

Documentation

Never put Docker orchestration directly inside API views.

---

# 10. Frontend Rules

React Components should:

- Have one responsibility.
- Be reusable.
- Avoid business logic.
- Call Services only.

Never call Axios directly inside components.

---

# 11. Docker Rules

Never manipulate Docker directly from views.

All Docker operations must use DockerManager.

Every Docker operation should:

- Validate ownership.
- Log the event.
- Handle errors gracefully.
- Support retries where appropriate.

---

# 12. Database Rules

Database changes require:

- Updated models.
- Django migration.
- Documentation update.
- Tests.

Never delete production migrations.

Never manually edit migration history.

---

# 13. Security Rules

Always:

Validate authentication.

Validate authorization.

Validate ownership.

Validate inputs.

Escape outputs where appropriate.

Use least privilege.

Never trust client data.

---

# 14. API Rules

Every endpoint must include:

Authentication.

Authorization.

Validation.

Error handling.

Logging.

Consistent JSON responses.

Meaningful HTTP status codes.

---

# 15. Testing Rules

Every new feature requires:

Unit tests.

Integration tests.

API tests.

Regression tests (if fixing a bug).

Do not remove tests unless explicitly instructed.

---

# 16. Documentation Rules

Whenever architecture changes:

Update:

- REST API document
- Database document
- Architecture document
- ADR (if applicable)

Documentation is part of the implementation.

---

# 17. Code Quality Rules

Code should be:

Readable.

Predictable.

Self-documenting.

Small functions are preferred.

Avoid deep nesting.

Prefer composition over duplication.

---

# 18. Performance Rules

Do not optimize prematurely.

When optimization is required:

Measure first.

Optimize second.

Document why.

Never sacrifice maintainability for micro-optimizations.

---

# 19. Git Rules

Each feature should produce:

- Focused commits.
- Clear commit messages.
- No unrelated changes.

Prefer small pull requests.

---

# 20. Communication Rules

If a requirement is unclear:

Ask.

If documentation conflicts:

Stop.

Identify the conflict.

Request clarification.

Never guess.

When presenting work:

- Summarize what changed.
- Mention affected files.
- Mention tests added.
- Mention documentation updated.

---

# 21. When To Ask Questions

The AI should pause and request clarification when:

- Requirements conflict.
- Multiple architectural options exist.
- Security implications are unclear.
- New dependencies appear necessary.
- Database schema changes significantly.
- Existing documentation is ambiguous.

Reasonable assumptions may be made only for minor implementation details that do not affect architecture or security.

---

# 22. Forbidden Actions

Never:

- Rewrite large working modules without justification.
- Introduce new frameworks.
- Mix unrelated refactoring with feature work.
- Change public APIs without updating documentation.
- Disable tests to make builds pass.
- Ignore failing migrations.
- Bypass validation.
- Hardcode credentials.
- Store secrets in the repository.
- Change architecture without updating the ADR.

---

# 23. Definition of Complete

A task is complete only when:

✓ Feature implemented

✓ Tests added

✓ Tests passing

✓ Documentation updated

✓ Logging included

✓ Error handling implemented

✓ Security reviewed

✓ No TODO placeholders remain

✓ Code formatted

✓ Linting passes

---

# 24. AI Session Startup Prompt

Before beginning any implementation, the AI should:

1. Identify the requested feature.
2. Determine which documents are relevant.
3. Summarize the implementation plan.
4. Identify affected components.
5. Highlight any assumptions.
6. Wait for confirmation if architectural changes are required.

---

# 25. AI Session End Checklist

Before concluding a development session, verify:

- Feature complete.
- No unfinished code paths.
- No unused imports.
- No debug statements.
- Tests pass.
- Documentation updated.
- Event logging included where appropriate.
- Security considerations reviewed.
- Performance impact assessed.
- Relevant ADR updated (if needed).

---

# Guiding Principle

Every change should leave the project in a better state than it was found.

Favor consistency over cleverness.

Favor clarity over brevity.

Build for the next developer—whether human or AI.

---

# End of Document