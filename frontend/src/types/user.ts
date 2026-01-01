// User Management Types

// Status for filtering
export type UserStatus = 'active' | 'inactive';

// Role definitions
export type UserRole = 'admin' | 'project_manager' | 'department_manager' | 'viewer';

// Base User Interface (matching backend UserPublic)
export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  role: UserRole;
  department_id?: string | null; // For Department Managers
  created_at: string;
  updated_at?: string;
}

// User Creation Payload
export interface CreateUserPayload {
  email: string;
  full_name: string;
  password: string;
  role: UserRole;
  department_id?: string | null;
  is_active?: boolean;
  is_superuser?: boolean;
}

// User Update Payload
export interface UpdateUserPayload {
  email?: string;
  full_name?: string;
  password?: string;
  role?: UserRole;
  department_id?: string | null;
  is_active?: boolean;
  is_superuser?: boolean;
}

// Filter params for Users API
export interface UserFilters {
  status?: UserStatus;
  role?: UserRole;
  search?: string; // Search by name or email
  page?: number;
  per_page?: number;
}
