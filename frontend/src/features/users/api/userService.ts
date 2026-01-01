import apiClient from '@/api';
import { 
  User, 
  UserFilters, 
  CreateUserPayload, 
  UpdateUserPayload 
} from '@/types/user';

export const UserService = {
  getUsers: async (filters: UserFilters = {}): Promise<User[]> => {
    // Map filters to backend params
    const params = {
      skip: filters.page && filters.per_page ? (filters.page - 1) * filters.per_page : 0,
      limit: filters.per_page || 100,
      search: filters.search
    };

    const response = await apiClient.get<User[]>('/users', { params });
    return response.data;
  },

  createUser: async (data: CreateUserPayload): Promise<User> => {
    const response = await apiClient.post<User>('/users', data);
    return response.data;
  },

  updateUser: async (id: string, data: UpdateUserPayload): Promise<User> => {
    const response = await apiClient.put<User>(`/users/${id}`, data);
    return response.data;
  },

  deleteUser: async (id: string): Promise<void> => {
    await apiClient.delete(`/users/${id}`);
  }
};
