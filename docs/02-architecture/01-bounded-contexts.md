# Bounded Contexts

**Last Updated:** 2025-12-29

This document defines the bounded contexts used to partition the Backcast EVS system. Each context represents a cohesive functional area with clear boundaries.

## Active Contexts

### 1. Authentication & Authorization
**Responsibility:** User identity verification, token management, role-based access control  
**Owner:** Backend Team  
**Status:** ✅ Implemented  
**Code Locations:**
- `app/core/security.py` - Password hashing, JWT creation/decoding
- `app/api/routes/auth.py` - Login, register, token endpoints
- `app/api/dependencies/auth.py` - Current user dependency
- `app/services/auth.py` - Authentication business logic

**Documentation:** [contexts/auth/](contexts/auth/)

---

### 2. User Management
**Responsibility:** User CRUD operations, profile management, admin user creation  
**Owner:** Backend Team  
**Status:** ✅ Implemented  
**Code Locations:**
- `app/models/domain/user.py` - User head + UserVersion tables
- `app/models/schemas/user.py` - Pydantic request/response schemas
- `app/api/routes/users.py` - User CRUD endpoints
- `app/services/user.py` - User business logic
- `app/repositories/user.py` - User data access
- `app/commands/user.py` - Create/Update/Delete commands

**Versioning:** Non-branching (simple version history)  
**Documentation:** [contexts/user-management/](contexts/user-management/)

---

### 3. Department Management
**Responsibility:** Department CRUD operations for budget tracking  
**Owner:** Backend Team  
**Status:** 📋 Planned (Story 2.2)  
**Code Locations:** TBD

---

### 4. Project & WBE Management
**Responsibility:** Project hierarchy, Work Breakdown Elements (machines), revenue allocation  
**Owner:** Backend Team  
**Status:** 📋 Backlog  
**Versioning:** Branch-enabled (supports change orders)

---

### 5. Cost Element & Financial Tracking
**Responsibility:** Departmental budgets, cost registration, forecasts, earned value tracking  
**Owner:** Backend Team  
**Status:** 📋 Backlog  
**Versioning:** Branch-enabled

---

### 6. Change Order Processing
**Responsibility:** Branch creation, modification, comparison, merging  
**Owner:** Backend Team  
**Status:** 📋 Backlog

---

### 7. EVM Calculations & Reporting
**Responsibility:** Planned Value, Earned Value, Actual Cost, performance indices, variance analysis  
**Owner:** Backend Team  
**Status:** 📋 Backlog

---

## Context Interaction Rules

1. **Authentication** is used by all contexts for identifying current user
2. **User Management** provides user data for audit trails in all versioned entities
3. **Project/WBE** hierarchy contains **Cost Elements**
4. **Financial Tracking** operates on **Cost Elements**
5. **Change Orders** create branches affecting **Project/WBE/Cost Elements**
6. **EVM Calculations** read from **Financial Tracking** data

## Adding New Contexts

When adding a new bounded context:

1. Create directory in `contexts/{context-name}/`
2. Add entry to this document
3. Create `architecture.md`, `data-models.md`, `api-contracts.md`, `code-locations.md`
4. Update `00-system-map.md` with context reference
