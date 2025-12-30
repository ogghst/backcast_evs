// Authentication-related TypeScript types matching backend schemas

export interface UserPublic {
  id: string;
  email: string;
  full_name: string;
  department: string | null;
  role: string;
  is_active: boolean;
  created_at: string | null;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface LoginFormData {
  username: string; // OAuth2 uses 'username' field
  password: string;
}
