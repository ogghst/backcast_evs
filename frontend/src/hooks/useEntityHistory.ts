import { useQuery } from "@tanstack/react-query";

interface UseEntityHistoryOptions<T> {
  /** Resource name (e.g., "users", "projects", "departments") */
  resource: string;
  /** Root entity ID to fetch history for */
  entityId: string | null | undefined;
  /** Function to fetch history for the given entity ID */
  fetchFn: (id: string) => Promise<T[]>;
  /** Whether the query should run (default: true when entityId exists) */
  enabled?: boolean;
}

/**
 * Generic hook for fetching version history of any versioned entity.
 *
 * @example
 * ```typescript
 * // For users
 * const { data: history, isLoading } = useEntityHistory({
 *   resource: "users",
 *   entityId: user?.user_id,
 *   fetchFn: UserService.getUserHistory,
 *   enabled: drawerOpen,
 * });
 *
 * // For projects
 * const { data: history, isLoading } = useEntityHistory({
 *   resource: "projects",
 *   entityId: project?.project_id,
 *   fetchFn: ProjectService.getProjectHistory,
 *   enabled: drawerOpen,
 * });
 * ```
 */
export const useEntityHistory = <T>({
  resource,
  entityId,
  fetchFn,
  enabled = true,
}: UseEntityHistoryOptions<T>) => {
  return useQuery({
    queryKey: [resource, entityId, "history"],
    queryFn: async () => {
      if (!entityId) return [];
      return await fetchFn(entityId);
    },
    enabled: enabled && !!entityId,
    staleTime: 30000, // Consider data fresh for 30 seconds
  });
};
