# Desktop Cloud Platform
# AI Prompt Library

**Document Version:** 1.0.0

**Product Version:** MVP

**Status:** Living Document

**Purpose**

This document contains standardized prompts for AI coding assistants (ChatGPT, Claude, Gemini, GitHub Copilot, Cursor, Windsurf, etc.).

Every development session should begin with one of these prompts instead of writing instructions from scratch.

The prompts assume the AI has access to the project documentation.

---

# Table of Contents

1. General Rules
2. Session Startup Prompt
3. New Vertical Slice
4. Continue Existing Slice
5. Bug Fix
6. Refactoring
7. Code Review
8. Security Review
9. Performance Review
10. Testing
11. Documentation
12. Database Changes
13. API Development
14. Frontend Development
15. Docker Development
16. Release Preparation
17. Architecture Discussion

---

# 1. General Rules

Every prompt assumes the AI must:

- Read the relevant project documentation first.
- Follow the documented architecture.
- Respect Coding Standards.
- Respect the ADRs.
- Develop in vertical slices.
- Update documentation when architecture changes.
- Never introduce dependencies without approval.
- Never skip testing.

---

# 2. Session Startup Prompt

## Purpose

Start every coding session consistently.

### Prompt

You are working on the Desktop Cloud Platform.

Before writing code:

1. Read the relevant project documents.
2. Summarize your understanding.
3. Identify affected components.
4. List assumptions.
5. Produce an implementation plan.
6. Wait for confirmation before making architectural changes.

---

# 3. New Vertical Slice

### Purpose

Implement a completely new feature.

### Prompt

Implement the next vertical slice from the Project Task Backlog.

Requirements:

- Complete the slice end-to-end.
- Follow the documented architecture.
- Keep business logic inside the Service layer.
- Include tests.
- Update documentation.
- Explain all design decisions.

Do not begin another slice until this one is complete.

---

# 4. Continue Existing Slice

### Prompt

Continue implementing the current vertical slice.

Before coding:

- Review existing implementation.
- Identify unfinished work.
- Do not redesign completed components.
- Preserve architectural consistency.

---

# 5. Bug Fix Prompt

### Prompt

Fix the reported issue.

Requirements:

- Identify root cause.
- Explain why the bug occurred.
- Implement the smallest safe fix.
- Add regression tests.
- Do not refactor unrelated code.

---

# 6. Refactoring Prompt

### Prompt

Refactor the specified module.

Constraints:

- No behavioral changes.
- No API changes.
- Preserve existing tests.
- Improve readability.
- Reduce duplication.
- Explain improvements.

---

# 7. Code Review Prompt

### Prompt

Review this code as a senior software architect.

Evaluate:

- Architecture
- Security
- Maintainability
- Performance
- Testing
- Documentation
- Naming
- Error handling

List:

Critical Issues

Major Issues

Minor Issues

Suggestions

---

# 8. Security Review Prompt

### Prompt

Perform a security review.

Evaluate:

- Authentication
- Authorization
- Secrets
- Docker isolation
- Input validation
- Session security
- CSRF
- XSS
- SQL Injection
- Command Injection
- File access
- Logging

Provide:

Risk Level

Recommendations

---

# 9. Performance Review Prompt

### Prompt

Review this implementation for performance.

Evaluate:

- Database queries
- API latency
- Docker operations
- React rendering
- Background jobs
- Memory usage
- Scalability

Recommend improvements only if justified.

---

# 10. Testing Prompt

### Prompt

Generate tests for this feature.

Include:

- Unit tests
- Integration tests
- API tests
- Error cases
- Edge cases

Explain what each test validates.

---

# 11. Documentation Prompt

### Prompt

Review whether the implementation requires documentation updates.

If required:

List:

- Documents affected
- Sections affected
- Suggested updates

Do not modify documentation unnecessarily.

---

# 12. Database Prompt

### Prompt

Implement database changes.

Requirements:

- Update Django models.
- Create migrations.
- Preserve data integrity.
- Explain relationships.
- Update Database Design documentation.

---

# 13. API Development Prompt

### Prompt

Design and implement a REST endpoint.

Include:

- URL
- Method
- Request schema
- Response schema
- Validation
- Authentication
- Authorization
- Error handling
- Tests

---

# 14. Frontend Prompt

### Prompt

Implement the frontend for this feature.

Requirements:

- React + TypeScript
- Tailwind CSS
- shadcn/ui
- Reusable components
- Responsive layout
- Loading states
- Error states

Avoid business logic in components.

---

# 15. Docker Prompt

### Prompt

Implement Docker-related functionality.

Requirements:

- Use DockerManager.
- Validate ownership.
- Log events.
- Handle failures.
- Support retries where appropriate.
- Respect resource limits.

---

# 16. Release Prompt

### Prompt

Prepare this feature for release.

Verify:

- Tests pass.
- Documentation updated.
- Logging included.
- Security reviewed.
- Performance reviewed.
- No TODOs remain.

Provide a release summary.

---

# 17. Architecture Discussion Prompt

### Prompt

Before implementing this feature:

Review the architecture.

Identify:

- Impacted modules
- Design trade-offs
- Alternative approaches
- Long-term implications

Do not write code.

Produce only the architectural discussion.

---

# Best Practices

Use one prompt per task.

Avoid combining unrelated requests.

Keep development focused on a single vertical slice.

Always preserve architectural consistency.

---

# End of Document