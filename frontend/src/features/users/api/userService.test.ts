import { describe, it, expect, vi, beforeEach } from 'vitest';
// import { backend } from '@/api'; // Removed unused invalid import
import { UserService } from './userService';
import { CreateUserPayload, UpdateUserPayload } from '@/types/user';

// Mock the API client
// Note: We need to mock the default export or named export depending on api/index.ts
// Based on checked file, api/index.ts exports default apiClient. 
// But let's check how it's used. Using vi.mock easiest on the path.

vi.mock('@/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import apiClient from '@/api';

describe('UserService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getUsers', () => {
    it('should call GET /users with correct params', async () => {
      const mockUsers = [{ id: '1', email: 'test@example.com' }];
      (apiClient.get as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockUsers });

      const filters = { page: 1, per_page: 10, search: 'test' };
      const result = await UserService.getUsers(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/users', {
        params: { limit: 10, skip: 0, search: 'test' } 
      });
      expect(result).toEqual(mockUsers);
    });
  });

  describe('createUser', () => {
    it('should call POST /users with payload', async () => {
      const payload: CreateUserPayload = {
        email: 'new@example.com',
        full_name: 'New User',
        password: 'password',
        role: 'viewer',
        is_active: true
      };
      
      const mockResponse = { id: '2', ...payload };
      (apiClient.post as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse });

      const result = await UserService.createUser(payload);

      expect(apiClient.post).toHaveBeenCalledWith('/users', payload);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('updateUser', () => {
    it('should call PUT /users/:id with payload', async () => {
      const id = '123';
      const payload: UpdateUserPayload = {
        full_name: 'Updated Name'
      };

      const mockResponse = { id, ...payload };
      (apiClient.put as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse });

      const result = await UserService.updateUser(id, payload);

      expect(apiClient.put).toHaveBeenCalledWith(`/users/${id}`, payload);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('deleteUser', () => {
    it('should call DELETE /users/:id', async () => {
      const id = '123';
      (apiClient.delete as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({ data: {} });

      await UserService.deleteUser(id);

      expect(apiClient.delete).toHaveBeenCalledWith(`/users/${id}`);
    });
  });
});
