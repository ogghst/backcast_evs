# Context: Quality & Testing

## 1. Overview
Ensures application stability, maintainability, and code quality through automated tooling and rigorous testing standards.

## 2. Technology Stack
- **Unit/Integration Testing**: Vitest + React Testing Library
- **E2E Testing**: Playwright (Planned)
- **Error Tracking**: Sentry
- **Linting**: ESLint (Flat Config) + Prettier

## 3. Architecture

### 3.1 Testing Strategy
- **Unit Tests**: Focus on pure logic (utils, hooks).
- **Component Tests**: Use React Testing Library to test components *as the user sees them* (clicking buttons, reading text), not implementation details.
- **Mocking**: Use MSW (Mock Service Worker) or simple manual mocks for API calls in tests to avoid hitting the real backend.

### 3.2 Error Monitoring (Sentry)
- **Production**: All exceptions are captured by Sentry.
- **Boundaries**: `ErrorBoundary` components wrap the UI to prevent white-screen crashes.
- **Context**: Errors should include user context (ID) and breadcrumbs (actions leading to error).

### 3.3 Code Quality
- **Pre-commit**: standard `npm run lint` and `npm run type-check` must pass.
- **Strictness**: TypeScript strict mode is non-negotiable.

## 4. Setup
- `vitest.config.ts` handles the test environment (jsdom).
- `eslint.config.js` manages rule sets.
