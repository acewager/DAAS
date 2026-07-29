# Desktop Cloud Platform
# UI Design System

**Document Version:** 1.0.0

**Product Version:** MVP

**Status:** Approved

---

# Table of Contents

1. Purpose
2. Design Philosophy
3. Visual Identity
4. Color System
5. Typography
6. Spacing System
7. Border Radius & Elevation
8. Icons
9. Layout Principles
10. Navigation
11. Components
12. Forms
13. Tables
14. Cards
15. Dialogs
16. Notifications
17. Loading States
18. Empty States
19. Error States
20. Responsive Design
21. Accessibility
22. Dark Mode
23. Future Enhancements

---

# 1. Purpose

This document defines the visual language of the Desktop Cloud Platform.

Its objectives are:

- Consistent UI
- Predictable interactions
- Clean appearance
- Easy maintenance
- Professional user experience

All frontend development should follow this document.

---

# 2. Design Philosophy

The interface should feel like a cloud platform, not a traditional business application.

Design principles:

- Simple
- Modern
- Spacious
- Fast
- Functional
- Professional

The UI should resemble platforms such as:

- GitHub
- Vercel
- Railway
- DigitalOcean
- Cloudflare Dashboard

Avoid excessive animations or decorative elements.

---

# 3. Visual Identity

Theme:

Modern cloud infrastructure platform.

Characteristics:

- Flat design
- Minimal gradients
- Rounded corners
- Generous whitespace
- Clear hierarchy

Primary focus should always remain on the user's running instances.

---

# 4. Color System

Primary Color

Used for:

- Primary buttons
- Active navigation
- Links
- Selected items

Success

Used for:

- Running containers
- Successful actions

Warning

Used for:

- Pending operations
- Auto-stop warnings
- Resource limits approaching

Danger

Used for:

- Delete actions
- Errors
- Failed operations

Neutral

Used for:

- Backgrounds
- Cards
- Borders
- Text hierarchy

The exact palette should be defined using CSS variables to support future theming.

---

# 5. Typography

Font:

Inter

Fallback:

System UI fonts

Hierarchy:

H1

Page titles

H2

Sections

H3

Cards

Body

Standard content

Caption

Supporting information

Avoid more than five text sizes across the application.

---

# 6. Spacing System

Use an 8px spacing grid.

Examples:

8px

16px

24px

32px

48px

64px

Avoid arbitrary spacing values.

---

# 7. Border Radius & Elevation

Border Radius

Small:

Inputs

Medium:

Cards

Large:

Dialogs

Elevation

Use subtle shadows only.

Avoid heavy shadow effects.

---

# 8. Icons

Preferred library:

Lucide Icons

Rules:

- Consistent sizing
- Outline style
- No mixed icon libraries
- Icons should support labels

Do not rely solely on icons to convey meaning.

---

# 9. Layout Principles

Desktop-first.

Maximum content width where appropriate.

Standard layout:

Header

↓

Sidebar

↓

Content

↓

Footer (minimal)

Important actions should remain visible without excessive scrolling.

---

# 10. Navigation

Primary Navigation

Sidebar

Contains:

- Dashboard
- Instances
- Templates
- Software Requests
- Analytics
- Settings

Secondary Navigation

Breadcrumbs where useful.

Highlight current location.

---

# 11. Components

Standard components include:

Buttons

Inputs

Selects

Checkboxes

Radio Buttons

Switches

Tabs

Badges

Progress Bars

Cards

Tables

Dialogs

Dropdown Menus

Tooltips

Skeleton Loaders

Use shadcn/ui as the primary component library.

---

# 12. Forms

Forms should:

- Validate in real time where appropriate.
- Clearly indicate required fields.
- Display helpful error messages.
- Preserve entered values after validation failures.

Primary actions should appear at the bottom-right.

---

# 13. Tables

Used for:

- Instances
- Users
- Event Logs
- Software Requests

Features:

- Sorting
- Pagination
- Search
- Filtering

Avoid horizontal scrolling when practical.

---

# 14. Cards

Cards represent individual entities.

Examples:

Instance Card

Template Card

Analytics Widget

Cards should contain:

Title

Status

Metadata

Primary Action

Secondary Actions

---

# 15. Dialogs

Dialogs are used for:

Delete confirmation

Software request approval

Persistent storage warning

Dialogs should always:

Explain consequences.

Offer Cancel.

Require explicit confirmation for destructive actions.

---

# 16. Notifications

Notification types:

Success

Information

Warning

Error

Use toast notifications for temporary feedback.

Critical failures should use dialogs.

---

# 17. Loading States

Every asynchronous action should display feedback.

Preferred order:

Skeleton UI

↓

Spinner (if necessary)

↓

Progress indicator (long operations)

Never leave users wondering whether the system is working.

---

# 18. Empty States

Every empty page should explain:

Why it is empty.

What the user can do next.

Examples:

"No instances yet."

"Create your first instance."

Include a clear call-to-action button.

---

# 19. Error States

Errors should:

Explain the problem.

Avoid technical jargon.

Offer recovery actions.

Example:

"Your container is currently stopped."

Button:

Start Container

---

# 20. Responsive Design

Primary target:

Desktop

Secondary:

Tablet

Mobile:

Basic usability only for MVP.

Administrative functions should remain desktop-oriented.

---

# 21. Accessibility

Minimum requirements:

Keyboard navigation

Visible focus states

Color contrast compliance

ARIA labels where appropriate

Meaningful button labels

Icons paired with text

Accessibility should be considered from the beginning rather than added later.

---

# 22. Dark Mode

The platform should support:

Light Mode

Dark Mode

System Preference

Theme switching should be implemented using CSS variables.

All components must function correctly in both themes.

---

# 23. Future Enhancements

Future versions may include:

- Custom branding
- Multiple themes
- User-selectable accent colors
- High contrast mode
- Compact density mode
- Custom dashboard layouts

---

# Design Principles Summary

Every screen should answer three questions immediately:

1. Where am I?
2. What can I do?
3. What is the current status?

If a screen does not answer these questions within a few seconds, it should be redesigned.

---

# End of Document