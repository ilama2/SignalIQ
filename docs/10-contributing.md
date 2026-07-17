# Development Standards

This document defines coding standards for the SignalIQ project.

---

# General Principles

- Keep code clean.
- Keep components reusable.
- Avoid duplicated code.
- Write readable TypeScript.
- Prefer composition over duplication.

---

# Naming

Components

PascalCase

Example

CompanyCard.tsx

Pages

PascalCase

Dashboard.tsx

Hooks

camelCase

useCompanies.ts

Services

camelCase

companyService.ts

Types

PascalCase

Company.ts

---

# Components

Components should be small.

A component should perform one responsibility.

If a component exceeds approximately 250 lines, consider splitting it.

---

# API Calls

Never call APIs directly inside pages.

Always use

services/

---

# Business Logic

Business logic belongs inside

hooks/

or

services/

Never inside UI components.

---

# State Management

Use React Context only for global state.

Avoid unnecessary global state.

---

# Styling

Use Tailwind CSS.

Avoid inline styles.

Prefer reusable utility classes.

---

# Git

Commit frequently.

Example commits

feat: dashboard cards

feat: companies page

fix: responsive sidebar

refactor: recommendation cards

---

# Pull Requests

Every PR should

- Build successfully
- Pass linting
- Use reusable components
- Follow folder structure

---

# AI Development

OpenCode should

- Read all documentation before writing code.
- Follow the architecture.
- Never create duplicate components.
- Prefer reusable UI.
- Keep business logic separate from presentation.