import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { UserList } from "./UserList";
import { useUserStore } from "@/stores/useUserStore";
import { User } from "@/types/user";

// Mock the stores
vi.mock("@/stores/useUserStore", () => ({
  useUserStore: vi.fn(),
}));

// Mock DataTable since it's tested separately
vi.mock("@/components/DataTable", () => ({
  DataTable: ({
    dataSource,
    columns,
  }: {
    dataSource: Record<string, unknown>[];
    columns: Record<string, unknown>[];
  }) => (
    <div data-testid="data-table">
      {dataSource.map((item: Record<string, unknown>) => (
        <div key={item.id as string}>{item.full_name as string}</div>
      ))}
      <div data-testid="columns">
        {columns
          .map((c: Record<string, unknown>) => c.title as string)
          .join(",")}
      </div>
    </div>
  ),
}));

// Mock UserModal to avoid complex rendering
vi.mock("./UserModal", () => ({
  UserModal: ({
    open,
    onCancel,
    onOk,
  }: {
    open: boolean;
    onCancel: () => void;
    onOk: (v: unknown) => void;
  }) =>
    open ? (
      <div role="dialog">
        Mock Modal
        <button onClick={onCancel}>Cancel</button>
        <button onClick={() => onOk({ email: "new@test.com" })}>Submit</button>
      </div>
    ) : null,
}));

describe("UserList", () => {
  const mockUsers: User[] = [
    {
      id: "1",
      email: "test1@example.com",
      full_name: "User One",
      role: "admin",
      is_active: true,
      is_superuser: false,
      created_at: "2025-01-01",
    },
    {
      id: "2",
      email: "test2@example.com",
      full_name: "User Two",
      role: "viewer",
      is_active: false,
      is_superuser: false,
      created_at: "2025-01-01",
    },
  ];

  const mockFetchUsers = vi.fn();
  const mockDeleteUser = vi.fn();
  const mockCreateUser = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useUserStore as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      (selector: (state: unknown) => unknown) => {
        const state = {
          users: mockUsers,
          loading: false,
          fetchUsers: mockFetchUsers,
          deleteUser: mockDeleteUser,
          createUser: mockCreateUser,
        };
        return selector ? selector(state) : state;
      }
    );
  });

  it("renders user list and fetches data on mount", () => {
    render(<UserList />);

    expect(mockFetchUsers).toHaveBeenCalled();
    expect(screen.getByText("User One")).toBeInTheDocument();
    expect(screen.getByText("User Two")).toBeInTheDocument();
  });

  it("opens create modal when Add button is clicked", () => {
    render(<UserList />);

    const addButton = screen.getByText(/Add User/i); // Adjust text based on actual implementation
    fireEvent.click(addButton);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Mock Modal")).toBeInTheDocument();
  });
});
