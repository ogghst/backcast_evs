import axios from "axios";

// Base API URL should come from environment variables
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // For cookie-based auth if needed
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Global error handling can be added here
    return Promise.reject(error);
  },
);
