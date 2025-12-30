import React from "react";
import "./i18n/config"; // Initialize i18n
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ConfigProvider, theme as antTheme } from "antd";
import { RouterProvider } from "react-router-dom";
import { router } from "@/routes";
import { theme } from "@/config/theme";
import "antd/dist/reset.css";
import { useUserPreferencesStore } from "@/stores/useUserPreferencesStore";

const queryClient = new QueryClient();

const App = () => {
  const { themeMode } = useUserPreferencesStore();
  
  return (
    <ConfigProvider
      theme={{
        ...theme,
        algorithm: themeMode === "dark" ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm,
      }}
    >
      <RouterProvider router={router} />
    </ConfigProvider>
  );
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
