import { UsersService } from "@/api/generated";
import {
  User,
  UserFilters,
  CreateUserPayload,
  UpdateUserPayload,
} from "@/types/user";

export const UserService = {
  getUsers: async (filters: UserFilters = {}): Promise<User[]> => {
    // Map filters to backend params
    const skip =
      filters.page && filters.per_page
        ? (filters.page - 1) * filters.per_page
        : 0;
    const limit = filters.per_page || 100;

    // Note: Search param is not yet implemented in backend
    const users = await UsersService.getUsers(skip, limit);
    return users as unknown as User[];
  },

  createUser: async (data: CreateUserPayload): Promise<User> => {
    const user = await UsersService.createUser(data);
    return user as unknown as User;
  },

  updateUser: async (id: string, data: UpdateUserPayload): Promise<User> => {
    const user = await UsersService.updateUser(id, data);
    return user as unknown as User;
  },

  deleteUser: async (id: string): Promise<void> => {
    await UsersService.deleteUser(id);
  },
};
