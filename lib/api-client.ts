export type ApiErrorBody = {
  error?: {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
  };
};

export class ApiError extends Error {
  status: number;
  code?: string;
  details?: Record<string, unknown>;

  constructor(status: number, body: ApiErrorBody) {
    super(body.error?.message ?? `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.code = body.error?.code;
    this.details = body.error?.details;
  }
}

type ApiOptions = RequestInit & {
  idempotencyKey?: string;
};

const configuredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "";
export const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_DATA !== "false";
const USE_DIRECT_API = process.env.NEXT_PUBLIC_USE_DIRECT_API === "true";
export const API_BASE_URL = USE_DIRECT_API ? configuredApiBaseUrl : "";
const configuredWsBaseUrl = process.env.NEXT_PUBLIC_WS_BASE_URL || "";
export const WS_BASE_URL = configuredWsBaseUrl || API_BASE_URL.replace(/^http/, "ws");

function readCookie(name: string) {
  if (typeof document === "undefined") return "";
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`))
    ?.split("=")[1] ?? "";
}

function isMutatingMethod(method?: string) {
  return ["POST", "PUT", "PATCH", "DELETE"].includes((method ?? "GET").toUpperCase());
}

export async function apiRequest<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (options.idempotencyKey) headers.set("Idempotency-Key", options.idempotencyKey);
  if (!USE_MOCK_DATA && isMutatingMethod(options.method) && !headers.has("X-CSRF-Token")) {
    const csrfToken = readCookie("pred_market_v1_csrf_token");
    if (csrfToken) headers.set("X-CSRF-Token", decodeURIComponent(csrfToken));
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    credentials: "include"
  });

  if (!response.ok) {
    let body: ApiErrorBody = {};
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = { error: { message: response.statusText } };
    }
    throw new ApiError(response.status, body);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
