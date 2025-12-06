const DEFAULT_API_BASE = 'http://localhost:8000/api';
const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE).replace(/\/$/, '');

type QueryParams = Record<string, string | number | boolean | undefined>;

type RequestOptions = {
  query?: QueryParams;
  init?: RequestInit;
};

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || response.statusText);
  }

  if (response.status === 204) {
    return {} as T;
  }

  const text = await response.text();
  if (!text) {
    return {} as T;
  }

  return JSON.parse(text) as T;
}

function buildUrl(path: string, query?: QueryParams) {
  const normalisedPath = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(`${BASE_URL}${normalisedPath}`);

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined) return;
      url.searchParams.append(key, String(value));
    });
  }

  return url.toString();
}

export const apiClient = {
  async get<T>(path: string, options?: RequestOptions) {
    const url = buildUrl(path, options?.query);
    const response = await fetch(url, { method: 'GET', ...(options?.init ?? {}) });
    return handleResponse<T>(response);
  },
};
