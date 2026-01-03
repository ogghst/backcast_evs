import { http, HttpResponse } from "msw";

// Helper to simulate network delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const handlers = [
  // Auth Handlers
  http.post("*/api/v1/login/access-token", async () => {
    await delay(300);
    return HttpResponse.json({
      access_token: "mock-jwt-token",
      token_type: "bearer",
    });
  }),

  http.get("*/api/v1/users/me", async () => {
    await delay(200);
    return HttpResponse.json({
      id: "mock-user-id",
      email: "user@example.com",
      full_name: "Mock User",
      is_active: true,
      roles: ["user"],
    });
  }),

  // User List Handler
  http.get("*/api/v1/users", async () => {
    await delay(500);
    return HttpResponse.json({
      items: [
        {
          id: "user-1",
          user_id: "user-root-1",
          email: "alice@example.com",
          full_name: "Alice Johnson",
          is_active: true,
          role: "admin",
          department: "Engineering",
        },
        {
          id: "user-2",
          user_id: "user-root-2",
          email: "bob@example.com",
          full_name: "Bob Smith",
          is_active: true,
          role: "user",
          department: "Marketing",
        },
        {
          id: "user-3",
          user_id: "user-root-3",
          email: "charlie@example.com",
          full_name: "Charlie Davis",
          is_active: false,
          role: "user",
          department: "Sales",
        },
      ],
      total: 3,
      page: 1,
      size: 10,
    });
  }),

  // User History Handler
  http.get("*/api/v1/users/:userId/history", async () => {
    return HttpResponse.json([
      {
        id: "ver-2",
        user_id: "user-root-1",
        email: "alice@example.com",
        full_name: "Alice Johnson (Updated)",
        valid_time: ["2024-01-02T10:00:00Z", null],
        transaction_time: ["2024-01-02T10:00:00Z", null],
        is_active: true,
        role: "admin",
        department: "Engineering",
      },
      {
        id: "ver-1",
        user_id: "user-root-1",
        email: "alice@example.com",
        full_name: "Alice Johnson",
        valid_time: ["2024-01-01T10:00:00Z", "2024-01-02T10:00:00Z"],
        transaction_time: ["2024-01-01T10:00:00Z", "2024-01-02T10:00:00Z"],
        is_active: true,
        role: "admin",
        department: "Engineering",
      },
    ]);
  }),
];
