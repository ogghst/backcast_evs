import { describe, it, expect, beforeEach, vi } from "vitest";
import { act } from "@testing-library/react";
import { useAuthStore } from "./useAuthStore";

describe("useAuthStore", () => {
  beforeEach(() => {
    // Clear localStorage and reset store
    localStorage.clear();
    useAuthStore.setState({ token: null, isAuthenticated: false });
  });

  it("should have initial state", () => {
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it("should set token and isAuthenticated on login", () => {
    const token = "test-token";
    act(() => {
      useAuthStore.getState().login(token);
    });

    const state = useAuthStore.getState();
    expect(state.token).toBe(token);
    expect(state.isAuthenticated).toBe(true);
  });

  it("should clear token and isAuthenticated on logout", () => {
    useAuthStore.setState({ token: "test-token", isAuthenticated: true });

    act(() => {
      useAuthStore.getState().logout();
    });

    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it("should persist token to localStorage", () => {
    const token = "persist-token";
    act(() => {
      useAuthStore.getState().login(token);
    });

    const stored = JSON.parse(localStorage.getItem("auth-storage") || "{}");
    expect(stored.state.token).toBe(token);
  });
});
