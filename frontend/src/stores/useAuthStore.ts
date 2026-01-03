import { create } from "zustand";
import { persist } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    immer((set) => ({
      token: null,
      isAuthenticated: false,
      login: (token: string) => {
        set((state) => {
          state.token = token;
          state.isAuthenticated = true;
        });
      },
      logout: () => {
        set((state) => {
          state.token = null;
          state.isAuthenticated = false;
        });
      },
    })),
    {
      name: "auth-storage", // localStorage key
      partialize: (state) => ({ token: state.token }), // Only persist token
      onRehydrateStorage: () => (state) => {
        // After rehydration, update isAuthenticated based on token presence
        if (state?.token) {
          state.isAuthenticated = true;
        }
      },
    }
  )
);
