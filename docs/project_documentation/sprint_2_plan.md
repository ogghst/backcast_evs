# Sprint 2 Implementation Plan: Core Infrastructure & User Management

**Sprint Duration:** 2 weeks
**Sprint Goal:** Complete foundation and implement user management
**Total Story Points:** 23

---

## Sprint 2 Stories

### Story 2.1: User Management (CRUD) [5 pts]

**As a** system administrator
**I need** to manage users (create, read, update, delete)
**So that** I can control who has access to the system and their details

#### Acceptance Criteria
- [ ] Complete CRUD endpoints for Users (`/users`)
- [ ] List users with pagination
- [ ] Get specific user details
- [ ] Update user profile (name, email, role)
- [ ] Deactivate/Soft delete user
- [ ] Admin-only restrictions for creating/deleting users
- [ ] Users can update their own profile (self-service)

#### Tasks
1.  **Enhance User Repository**
    - Add `get_all(skip, limit)`
    - Add `update(user_id, data)`
    - Add `delete(user_id)` (soft delete implementation `is_active=False`)

2.  **Enhance User Service**
    - Implement `update_user` with password handling (if changed)
    - Implement `delete_user`
    - Implement `get_users` with filtering

3.  **Implement API Endpoints**
    - `GET /users` (Admin only)
    - `GET /users/{id}` (Admin or Self)
    - `PUT /users/{id}` (Admin or Self)
    - `DELETE /users/{id}` (Admin only)

4.  **Write Tests**
    - Test pagination
    - Test permission enforcement (Admin vs Normal User)
    - Test validation logic

#### Definition of Done
- [ ] All CRUD endpoints working
- [ ] Permission checks passing
- [ ] Tests covering 90% of logic

---

### Story 2.2: Department Management [5 pts]

**As a** system administrator
**I need** to create and manage departments
**So that** I can organize users and cost elements into functional groups

#### Acceptance Criteria
- [ ] Department model created (id, name, code, description)
- [ ] CRUD endpoints for Departments (`/departments`)
- [ ] Unique constraint on Department code
- [ ] Relationship to Users (optional for now, but good to plan)

#### Tasks
1.  **Create Department Model**
    - `app/models/domain/department.py`
    - Fields: `id` (UUID), `name` (str), `code` (str, unique), `description` (str), `created_at`, `updated_at`

2.  **Create Schemas**
    - `DepartmentCreate`, `DepartmentUpdate`, `DepartmentResponse`

3.  **Create Repository**
    - `app/repositories/department.py`
    - Basic CRUD operations

4.  **Create Service**
    - `app/services/department.py`
    - Business logic (e.g., check for duplicates)

5.  **Create API Routes**
    - `app/api/routes/departments.py`
    - Protected endpoints (Admin only?)

#### Definition of Done
- [ ] Department entity fully functional
- [ ] Can create, list, and update departments
- [ ] Integrity constraints enforced

---

### Story 2.3: Pydantic Schemas & Validation [5 pts]

**As a** developer
**I need** robust data validation
**So that** invalid data never reaches the database and API clients get clear errors

#### Acceptance Criteria
- [ ] All API inputs validated using Pydantic V2
- [ ] Custom validators for specific fields (e.g., email format, codes)
- [ ] Consistent error response format
- [ ] Example values in schemas for documentation

#### Tasks
1.  **Refine Existing Schemas**
    - Review User schemas for edge cases
    - Add field descriptions and examples

2.  **Standardize Error Responses**
    - Create a standard `ErrorResponse` schema
    - Use `HTTPException` with detail models

3.  **Implement Common Validators**
    - `app/core/validators.py`? (or keep in schemas if simple)
    - Regex for codes, phone numbers, etc.

#### Definition of Done
- [ ] Invalid requests return 422 with clear details
- [ ] Documentation shows example payloads
- [ ] No internal server errors on bad input

---

### Story 2.4: Comprehensive Integration Testing [5 pts]

**As a** developer
**I need** a solid test suite
**So that** I can refactor with confidence (TDD)

#### Acceptance Criteria
- [ ] Integration tests for all new endpoints
- [ ] Database state clean/reset between tests
- [ ] Test coverage report > 80%
- [ ] Happy paths and edge cases covered

#### Tasks
1.  **Expand `conftest.py`**
    - Add fixtures for `admin_user`, `normal_user`, `department`
    - Improve async database cleanup efficiency

2.  **Write Tests for Stories 2.1 & 2.2**
    - `tests/api/test_users.py`
    - `tests/api/test_departments.py`

3.  **Run Coverage Analysis**
    - `pytest --cov=app`
    - Identify missing branches

#### Definition of Done
- [ ] CI pipeline passes with high coverage
- [ ] All reported bugs from manual testing added as test cases

---

### Story 2.5: API Documentation (OpenAPI) [3 pts]

**As a** frontend developer
**I need** clear API documentation
**So that** I can integrate with the backend without guessing

#### Acceptance Criteria
- [ ] Swagger UI (`/docs`) fully detailed
- [ ] ReDoc (`/redoc`) working
- [ ] All endpoints have summaries and descriptions
- [ ] Auth security schemes defined in OpenAPI spec

#### Tasks
1.  **Configure FastAPI Metadata**
    - `app/main.py`: Title, Description, Version, Tags Metadata
    - Define tags (Users, Departments, Auth)

2.  **Annotate Endpoints**
    - Add `summary`, `description`, `response_model`
    - Document status codes (200, 201, 400, 401, 403, 404)

3.  **Verify UI**
    - Check `/docs` to ensure it looks professional and complete

#### Definition of Done
- [ ] API is self-documenting
- [ ] "Try it out" feature works in Swagger UI

---

## Sprint 2 Timeline

### Week 1
**Days 1-3:** Story 2.2 (Department Management) - Low dependency, good warm-up
**Days 4-5:** Story 2.1 (User Management) - Build on Auth foundation

### Week 2
**Days 6-7:** Story 2.3 & 2.5 (Validation & Docs) - Refine what was built
**Days 8-9:** Story 2.4 (Comprehensive Testing) - Ensure robustness
**Day 10:** Sprint Review & Retrospective

---

## Sprint 2 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Scope Creep (RBAC details)** | Medium | Stick to simple Admin/User roles for now. Defer complex permission tables to later sprints if needed. |
| **Testing Bottlenecks** | Medium | Write tests *alongside* code (TDD), don't leave them for the end. |

---

## Sprint 2 Success Metrics

- [ ] All 5 stories completed (23 points)
- [ ] Test coverage maintained > 80% (ideally > 90%)
- [ ] Zero critical bugs in foundation code
- [ ] API fully documented

---

**Document Version:** 1.0
**Created:** 2025-12-28
