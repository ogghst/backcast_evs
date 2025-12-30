import { createBrowserRouter } from "react-router-dom";
import AppLayout from "@/layouts/AppLayout";
import Home from "@/pages/Home";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
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
