import { create } from 'zustand';
import { User, CreateUserPayload, UpdateUserPayload, UserFilters } from '@/types/user';
import { UserService } from '@/features/users/api/userService';

interface UserState {
  users: User[];
  loading: boolean;
  error: string | null;
  
  fetchUsers: (filters?: UserFilters) => Promise<void>;
  createUser: (data: CreateUserPayload) => Promise<void>;
  updateUser: (id: string, data: UpdateUserPayload) => Promise<void>;
  deleteUser: (id: string) => Promise<void>;
}

export const useUserStore = create<UserState>((set) => ({
  users: [],
  loading: false,
  error: null,

  fetchUsers: async (filters) => {
    set({ loading: true, error: null });
    try {
      const users = await UserService.getUsers(filters);
      set({ users, loading: false });
    } catch (err) {
      set({ 
        error: err instanceof Error ? err.message : 'Unknown error', 
        loading: false,
        users: [] 
      });
    }
  },
  
  createUser: async (data) => {
    set({ loading: true, error: null });
    try {
        const newUser = await UserService.createUser(data);
        set((state) => ({ 
            users: [...state.users, newUser],
            loading: false 
        }));
    } catch (err) {
         set({ error: err instanceof Error ? err.message : 'Failed to create user', loading: false });
    }
  },

  updateUser: async (id, data) => {
      set({ loading: true, error: null });
       try {
        const updatedUser = await UserService.updateUser(id, data);
        set((state) => ({
            users: state.users.map(u => u.id === id ? updatedUser : u),
            loading: false
        }));
    } catch (err) {
         set({ error: err instanceof Error ? err.message : 'Failed to update user', loading: false });
    }
  },

  deleteUser: async (id) => {
       set({ loading: true, error: null });
       try {
        await UserService.deleteUser(id);
        set((state) => ({
            users: state.users.filter(u => u.id !== id),
            loading: false
        }));
    } catch (err) {
         set({ error: err instanceof Error ? err.message : 'Failed to delete user', loading: false });
    }
  }
}));
