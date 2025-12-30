import { createBrowserRouter } from "react-router-dom";
import AppLayout from "@/layouts/AppLayout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Home from "@/pages/Home";
import Login from "@/pages/Login";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: "/",
        element: <Home />,
      },
      {
        path: "/projects",
        element: <div>Projects Placeholder</div>,
      },
      {
        path: "/users",
        element: <div>Users Placeholder</div>,
      },
    ],
  },
]);
