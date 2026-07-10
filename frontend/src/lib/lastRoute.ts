const LAST_ROUTE_KEY = "quickfit:last-route";

export function saveLastRoute(path: string): void {
  localStorage.setItem(LAST_ROUTE_KEY, path);
}

export function readLastRoute(): string | null {
  return localStorage.getItem(LAST_ROUTE_KEY);
}
