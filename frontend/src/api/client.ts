type RequestConfig = {
  url: string;
  method: string;
  params?: Record<string, unknown>;
  data?: unknown;
  headers?: HeadersInit;
  signal?: AbortSignal;
};

export const customFetch = async <T>(
  config: RequestConfig,
  options?: RequestInit,
): Promise<T> => {
  const { url, method, params, data, signal, headers } = config;

  const query = params
    ? `?${new URLSearchParams(params as Record<string, string>).toString()}`
    : "";

  const res = await fetch(`${url}${query}`, {
    ...options,
    method,
    signal,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...headers },
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
};
