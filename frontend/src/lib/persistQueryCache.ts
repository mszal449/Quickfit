import { QueryClient, dehydrate, hydrate } from "@tanstack/react-query";

const CACHE_KEY = "quickfit:query-cache";
const MAX_AGE_MS = 1000 * 60 * 60 * 24;

type PersistedCache = {
  timestamp: number;
  state: ReturnType<typeof dehydrate>;
};

export function restoreQueryCache(client: QueryClient): void {
  const raw = localStorage.getItem(CACHE_KEY);
  if (!raw) return;
  try {
    const persisted = JSON.parse(raw) as PersistedCache;
    if (Date.now() - persisted.timestamp > MAX_AGE_MS) {
      localStorage.removeItem(CACHE_KEY);
      return;
    }
    hydrate(client, persisted.state);
  } catch {
    localStorage.removeItem(CACHE_KEY);
  }
}

export function persistQueryCache(client: QueryClient): void {
  const save = () => {
    try {
      const persisted: PersistedCache = {
        timestamp: Date.now(),
        state: dehydrate(client, {
          shouldDehydrateQuery: (query) => query.state.status === "success",
        }),
      };
      localStorage.setItem(CACHE_KEY, JSON.stringify(persisted));
    } catch {
      return;
    }
  };

  const saveWhenHidden = () => {
    if (document.visibilityState === "hidden") save();
  };

  document.addEventListener("visibilitychange", saveWhenHidden);
  window.addEventListener("pagehide", save);
}
