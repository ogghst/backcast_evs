import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      isAuthenticated: false,
      login: (token: string) => {
        set({ token, isAuthenticated: true });
      },
      logout: () => {
        set({ token: null, isAuthenticated: false });
      },
    }),
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
