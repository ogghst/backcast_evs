import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { UserList } from "./UserList";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ConfigProvider } from "antd";

// We DO NOT mock useUserStore here, so it hits the real API layer
// MSW handlers in setupTests.ts will intercept the requests

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

// Mock Ant Design App component
vi.mock("antd", async () => {
  const actual = await vi.importActual("antd");
  return {
    ...actual,
    App: {
      useApp: () => ({
        message: { success: vi.fn(), error: vi.fn() },
        modal: { confirm: vi.fn() },
      }),
    },
  };
});

const createTestClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

const renderWithProviders = (ui: React.ReactNode) => {
  const queryClient = createTestClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <ConfigProvider>{ui}</ConfigProvider>
    </QueryClientProvider>
  );
};

describe("UserList Integration", () => {
  it("renders user list and fetches data from MSW", async () => {
    // This looks for data defined in src/mocks/handlers.ts
    // Alice Johnson, Bob Smith, Charlie Davis
    renderWithProviders(<UserList />);

    // Initial loading state might be visible, wait for data
    await waitFor(() => {
      expect(screen.getByText("Alice Johnson")).toBeInTheDocument();
    });

    expect(screen.getByText("Bob Smith")).toBeInTheDocument();
    expect(screen.getByText("Charlie Davis")).toBeInTheDocument();

    // Verify role mapping from mock data
    expect(screen.getByText("Engineering")).toBeInTheDocument();
  });

  it("opens create modal when Add button is clicked", async () => {
    renderWithProviders(<UserList />);

    // Wait for list to load first to ensure interactive
    await waitFor(() => screen.getByText("Alice Johnson"));

    const addButton = screen.getByText(/Add User/i);
    fireEvent.click(addButton);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Mock Modal")).toBeInTheDocument();
  });
});
