import { useMeGet } from "../api/generated/auth/auth";

export function useCurrentUser() {
  return useMeGet({
    query: {
      staleTime: Infinity,
      retry: false,
    },
  });
}
