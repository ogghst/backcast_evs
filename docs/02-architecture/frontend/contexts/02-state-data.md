# Context: State Management & Data

## 1. Overview

This context governs how data flows through the application, distinguishing clearly between **Server State** (data owned by the backend) and **Client State** (UI state owned by the user session).

## 2. Technology Stack

- **Server State**: TanStack Query (React Query) v5
- **Client State**: Zustand v5 with Immer middleware
- **HTTP Client**: Axios

## 3. Architecture

### 3.1 Server State (TanStack Query)

We prefer **Servers State** over generic global stores.

- **Pattern**: Custom hooks for every API resource (e.g., `useProjects`, `useUpdateProject`).
- **Caching**: Stale-while-revalidate strategy.
- **Optimistic Updates**: UI updates immediately before the server response confirms success (critical for "snappy" feel).
- **DevTools**: Enabled in development to debug cache states.

### 3.2 Client State (Zustand)

Used **only** for global UI state that persists across routes but isn't database data.

- **Examples**: Sidebar toggle state, User authentication token, Theme preference.
- **Why Zustand?**: Minimal boilerplate compared to Redux; better performance than Context API for frequent updates.

**Immer Middleware:**
All Zustand stores use the `immer` middleware for immutable state updates:

```typescript
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

export const useStore = create<State>()(
  immer((set) => ({
    items: [],
    addItem: (item) =>
      set((state) => {
        state.items.push(item); // Direct mutation (immer handles immutability)
      }),
  }))
);
```

**Benefits:**

- Cleaner, more readable code (no spread operators)
- Prevents accidental mutations
- Easier to work with nested objects/arrays
- Type-safe draft mutations

### 3.3 API Layer

- **Client**: Single Axios instance (`src/api/client.ts`) handles:
  - Base URL configuration.
  - Auth token injection (Interceptors).
  - Global error handling (401 redirects).
- **Standardization**: All API calls must return typed responses matching Backend Pydantic schemas.

## 4. Implementation Guidelines

- **Do not** store API data in Zustand. Use `useQuery`.
- **Do not** use `useEffect` for data fetching.
- **Do** type all API responses.
- **Do** use immer middleware for all Zustand stores.
- **Do** use draft mutations (direct assignments) within immer `set` callbacks.
