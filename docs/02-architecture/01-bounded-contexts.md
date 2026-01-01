# Bounded Contexts

**Last Updated:** 2026-01-01

This document defines the bounded contexts used to partition the Backcast EVS system. Each context represents a cohesive functional area with clear boundaries.

### 0. EVCS Core (Entity Versioning Control System)

**Responsibility:** Bitemporal versioning framework, branching, soft delete, time-travel  
**Owner:** Backend Team  
**Documentation:** [backend/contexts/evcs-core/](backend/contexts/evcs-core/)

> [!NOTE]
>
> - **Versioned entities** (Project, WBE, CostElement) inherit from `TemporalBase` - see [ADR-005](decisions/ADR-005-bitemporal-versioning.md)
> - **Non-versioned entities** (UserPreferences, SystemConfig) inherit from `SimpleBase` - see [Non-Versioned Entities](backend/contexts/evcs-core/architecture.md#non-versioned-entities)

---

### 1. Authentication & Authorization

**Responsibility:** User identity verification, token management, role-based access control  
**Owner:** Backend Team  
**Documentation:** [backend/contexts/auth/](backend/contexts/auth/)

---

### 2. User Management

**Responsibility:** User CRUD operations, profile management, admin user creation  
**Owner:** Backend Team  
**Versioning:** Not versioned
**Documentation:** [backend/contexts/user-management/](backend/contexts/user-management/)

---

### 3. Department Management

**Responsibility:** Department CRUD operations for budget tracking  
**Owner:** Backend Team

---

### 4. Project & WBE Management

**Responsibility:** Project hierarchy, Work Breakdown Elements (machines), revenue allocation  
**Owner:** Backend Team  
**Versioning:** Bitemporal with branching (via EVCS Core)

---

### 5. Cost Element & Financial Tracking

**Responsibility:** Departmental budgets, cost registration, forecasts, earned value tracking  
**Owner:** Backend Team  
**Versioning:** Bitemporal with branching (via EVCS Core)

---

### 6. Change Order Processing

**Responsibility:** Branch creation, modification, comparison, merging  
**Owner:** Backend Team

---

### 7. EVM Calculations & Reporting

**Responsibility:** Planned Value, Earned Value, Actual Cost, performance indices, variance analysis  
**Owner:** Backend Team

---

## Context Interaction Rules

1. **EVCS Core** provides the versioning framework used by all versioned entities
2. **Authentication** is used by all contexts for identifying current user
3. **User Management** provides user data for audit trails in all versioned entities
4. **Project/WBE** hierarchy contains **Cost Elements**
5. **Financial Tracking** operates on **Cost Elements**
6. **Change Orders** create branches via EVCS Core affecting **Project/WBE/Cost Elements**
7. **EVM Calculations** read from **Financial Tracking** data with time-travel support

## Adding New Contexts

When adding a new bounded context:

1. Create directory in `contexts/{context-name}/`
2. Add entry to this document
3. Create `architecture.md`, `data-models.md`, `api-contracts.md`, `code-locations.md`
4. Update `00-system-map.md` with context reference
