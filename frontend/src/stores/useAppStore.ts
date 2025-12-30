import { create } from "zustand";

interface AppState {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  // Theme could also be managed here or via a dedicated store,
  // currently we are just demonstrating the pattern.
}

export const useAppStore = create<AppState>((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () =>
    set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
