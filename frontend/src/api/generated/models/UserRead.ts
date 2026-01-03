/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Schema for reading user data (excludes password).
 */
export type UserRead = {
    email: string;
    full_name: string;
    department?: (string | null);
    role?: string;
    id: string;
    user_id: string;
    is_active: boolean;
    created_at?: (string | null);
    password_changed_at?: (string | null);
    preferences?: (Record<string, any> | null);
};

