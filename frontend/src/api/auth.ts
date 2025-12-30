import { apiClient } from "./client";
import type { Token, UserLogin, UserPublic } from "@/types/auth";

/**
 * Login user with email and password
 * Backend expects OAuth2PasswordRequestForm (username + password)
 */
export const loginUser = async (
  credentials: UserLogin
): Promise<Token> => {
  // OAuth2 expects form data with 'username' field (not 'email')
  const formData = new URLSearchParams();
  formData.append("username", credentials.email);
  formData.append("password", credentials.password);

  const response = await apiClient.post<Token>("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
};

/**
 * Get current authenticated user
 */
export const getCurrentUser = async (): Promise<UserPublic> => {
  const response = await apiClient.get<UserPublic>("/auth/me");
  return response.data;
};

/**
 * Register a new user (future implementation)
 */
export const registerUser = async (userData: {
  email: string;
  password: string;
  full_name: string;
  department?: string;
  role?: string;
}): Promise<UserPublic> => {
  const response = await apiClient.post<UserPublic>("/auth/register", userData);
  return response.data;
};
