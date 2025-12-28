---
trigger: always_on
---

# Onboarding Guide

Welcome to the Backcast EVS project! This guide will help you get your development environment set up and familiarize you with our workflow.

## 1. Prerequisites

Ensure you have the following installed:
*   Python 3.12 or higher
*   PostgreSQL 15 or higher
*   [uv](https://github.com/astral-sh/uv) (Our package manager)

## 2. Backend Environment Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/nicola/backcast_evs.git
    cd backcast_evs/backend
    ```

2.  **Install Dependencies**:
    ```bash
    uv sync
    ```

3.  **Configure Environment Variables**:
    ```bash
    cp .env.example .env
    # Update DATABASE_URL and SECRET_KEY in .env
    ```

4.  **Create Test Database**:
    Ensure you have a `backcast_evs_test` database for automated tests.

## 3. Backend Mandatory Quality Checks

We use **pre-commit** hooks to ensure code quality **before** it hits our repository. This is a mandatory step for all developers.

1.  **Install Pre-commit Hooks**:
    ```bash
    cd backend
    uv run pre-commit install
    ```
    Now, every time you `git commit`, `ruff` and `mypy` will run automatically.

## 4. Daily Workflow

1.  **Branching**: Create a feature branch from `develop`.
2.  **Coding**: Follow our [Coding Standards](coding_standards.md).
3.  **Testing**: Write tests following our [Testing Guidelines](testing_guidelines.md).
4.  **Committing**: Ensure pre-commit hooks pass.
5.  **Pull Request**: Submit PR to `develop` for review.

## 5. Backend Useful Commands

*   `uv run uvicorn app.main:app --reload`: Start dev server.
*   `uv run pytest`: Run tests.
*   `uv run ruff check .`: Run linter.
*   `uv run mypy app --strict`: Run type checker.
