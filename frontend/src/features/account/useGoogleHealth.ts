import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { customFetch } from "../../api/client";

const STATUS_KEY = ["/api/integrations/google-health/status"];

export interface IntegrationStatus {
  connected: boolean;
  scope_granted: string | null;
  created_at: string | null;
}

export function useIntegrationStatus() {
  return useQuery({
    queryKey: STATUS_KEY,
    queryFn: () =>
      customFetch<IntegrationStatus>({
        url: "/api/integrations/google-health/status",
        method: "GET",
      }),
    retry: false,
  });
}

export function useDisconnectIntegration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      customFetch<void>({
        url: "/api/integrations/google-health/revoke",
        method: "DELETE",
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: STATUS_KEY }),
  });
}

export function useIntegrationWorkouts(enabled: boolean) {
  return useQuery({
    queryKey: ["/api/integrations/google-health/workouts"],
    queryFn: () =>
      customFetch<unknown>({
        url: "/api/integrations/google-health/workouts",
        method: "GET",
      }),
    enabled,
    retry: false,
  });
}

export function connectGoogleHealth() {
  window.location.href = "/api/integrations/google-health/connect";
}
