import { create } from "zustand";
import { theme } from "antd";
import api from "@/api";

interface UserPreferencesState {
  themeMode: "light" | "dark";
  setThemeMode: (mode: "light" | "dark") => void;
  toggleTheme: () => void;
  fetchPreferences: () => Promise<void>;
}

export const useUserPreferencesStore = create<UserPreferencesState>((set, get) => ({
  themeMode: "light",
  setThemeMode: async (mode) => {
    set({ themeMode: mode });
    try {
      await api.put("/users/me/preferences", { theme: mode });
    } catch (error) {
      console.error("Failed to save preference", error);
    }
  },
  toggleTheme: async () => {
    const newMode = get().themeMode === "light" ? "dark" : "light";
    set({ themeMode: newMode });
    try {
      await api.put("/users/me/preferences", { theme: newMode });
    } catch (error) {
      console.error("Failed to save preference", error);
    }
  },
  fetchPreferences: async () => {
    try {
      const response = await api.get("/users/me/preferences");
      if (response.data && response.data.theme) {
        set({ themeMode: response.data.theme });
      }
    } catch (error) {
      console.error("Failed to fetch preferences", error);
    }
  },
}));
