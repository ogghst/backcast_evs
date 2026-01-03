import { describe, it, expect, vi, beforeEach } from "vitest";
import { useUserStore } from "./useUserStore";
import { UserService } from "@/features/users/api/userService";
import { User, UserRole } from "@/types/user";

vi.mock("@/features/users/api/userService", () => ({
  UserService: {
    getUsers: vi.fn(),
    createUser: vi.fn(),
    updateUser: vi.fn(),
    deleteUser: vi.fn(),
  },
}));

describe("useUserStore", () => {
  beforeEach(() => {
    useUserStore.setState({ users: [], loading: false, error: null });
    vi.clearAllMocks();
  });

  const mockUser: User = {
    id: "1",
    email: "test@example.com",
    full_name: "Test User",
    role: "admin" as UserRole,
    is_active: true,
    is_superuser: false,
    created_at: "2025-01-01",
  };

  it("should fetch users successfully", async () => {
    vi.mocked(UserService.getUsers).mockResolvedValue([mockUser]);

    await useUserStore.getState().fetchUsers();

    expect(useUserStore.getState().users).toEqual([mockUser]);
    expect(useUserStore.getState().loading).toBe(false);
    expect(useUserStore.getState().error).toBe(null);
  });

  it("should handle fetch error", async () => {
    const errorMsg = "Network Error";
    vi.mocked(UserService.getUsers).mockRejectedValue(new Error(errorMsg));

    await useUserStore.getState().fetchUsers();

    expect(useUserStore.getState().users).toEqual([]);
    expect(useUserStore.getState().loading).toBe(false);
    expect(useUserStore.getState().error).toBe(errorMsg);
  });

  it("should add user successfully", async () => {
    vi.mocked(UserService.createUser).mockResolvedValue(mockUser);

    // Setup initial state
    useUserStore.setState({ users: [] });

    await useUserStore.getState().createUser({
      email: "test@example.com",
      full_name: "Test",
      password: "pwd",
      role: "admin",
    });

    expect(useUserStore.getState().users).toContainEqual(mockUser);
  });
});
