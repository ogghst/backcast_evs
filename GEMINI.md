# Entity Version Control System (EVCS) Architecture 

## 1. Project Scope
This project implements a robust, Git-style version control system for relational database entities. Unlike simple audit logs, this system provides full branching capabilities, time-travel functionality, and immutable state history for complex data structures.

**Key Capabilities:**
* **Branching:** Support for parallel development of entity states (e.g., `main`, `draft`, `feature/legal-review`).
* **Time Travel:** Ability to reconstruct the state of an entity (and its related children) at any specific timestamp in the past.
* **Immutability:** Updates create new version nodes; historical data is never overwritten (APPEND-ONLY).
* **Strong Typing:** Fully typed codebase verified at compile-time.

## 2. Project Structure

The project is organized into several key directories:

*   **`backend/`**: Contains the FastAPI application, database models, and versioning logic.
    *   `app/api/`: Endpoint definitions and dependencies.
    *   `app/core/`: Configuration, security, and versioning core logic.
    *   `app/models/`: SQLAlchemy ORM models and Pydantic schemas.
    *   `app/repositories/`: Data access layer implementing the versioning logic.
    *   `app/services/`: Business logic orchestrating multiple repositories.
*   **`docs/`**: Project documentation, including architectural deep dives and sprint plans.
    *   `docs/dev/`: Technical documentation for developers.
    *   `docs/project_documentation/`: Project management and tracking records.
*   **`scripts/`**: Utility scripts for database management and development tasks.

## 3. Documentation

For detailed technical information and development guides, please refer to the following documents in the `docs/` folder:

*   **[Backend Architecture Documentation](file:///home/nicola/dev/backcast_evs/docs/dev/backend_architecture.md)**: Deep dive into the EVCS implementation, patterns, and database schema.
*   **[Development Onboarding](file:///home/nicola/dev/backcast_evs/docs/dev/onboarding.md)**: Setup instructions and coding standards.
*   **[Product Requirements Document (PRD)](file:///home/nicola/dev/backcast_evs/docs/prd.md)**: Business requirements and functional specifications.
*   **[Agile Implementation Plan](file:///home/nicola/dev/backcast_evs/docs/project_documentation/agile_implementation_plan.md)**: High-level roadmap and strategy.
*   **[Project Track Record](file:///home/nicola/dev/backcast_evs/docs/project_documentation/project_track_record.md)**: Historical record of completed tasks and metrics.

## 4. Work Process (Strict Rules)

> [!IMPORTANT]
> To ensure project health and visibility, the following rules are **MANDATORY**:
> 1.  **PDCA Alignment**: Every major change must follow the Plan-Do-Check-Act cycle.
> 2.  **Documentation Updates**: Both the **[Agile Implementation Plan](file:///home/nicola/dev/backcast_evs/docs/project_documentation/agile_implementation_plan.md)** and the **[Project Track Record](file:///home/nicola/dev/backcast_evs/docs/project_documentation/project_track_record.md)** MUST be updated at the end of every PDCA cycle.

---
> [!NOTE]
> This project follows strict type safety (MyPy strict mode) and automated quality checks (Ruff).