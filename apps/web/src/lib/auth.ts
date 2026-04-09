const TOKEN_KEY = "orderiq_token";

// ---------------------------------------------------------------------------
// Token storage
// ---------------------------------------------------------------------------

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// ---------------------------------------------------------------------------
// Authenticated fetch
// ---------------------------------------------------------------------------

export class AuthError extends Error {
  constructor() {
    super("Unauthorized");
    this.name = "AuthError";
  }
}

function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export async function authFetch(
  path: string,
  options?: RequestInit
): Promise<Response> {
  const token = getToken();
  const res = await fetch(`${apiBase()}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (res.status === 401) {
    clearToken();
    throw new AuthError();
  }
  return res;
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export type LoginPayload = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export async function loginRequest(
  payload: LoginPayload
): Promise<TokenResponse> {
  const res = await fetch(`${apiBase()}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const data: { detail?: string } = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? "Giriş başarısız");
  }
  return res.json() as Promise<TokenResponse>;
}

// ---------------------------------------------------------------------------
// Merchant types — mirror OrderResponse from the backend
// ---------------------------------------------------------------------------

export type OrderItemModifier = {
  id: string;
  modifier_option_id: string;
  modifier_name_snapshot: string;
  extra_price: number;
};

export type OrderItem = {
  id: string;
  product_id: string;
  product_name_snapshot: string;
  unit_price: number;
  quantity: number;
  line_total: number;
  modifiers: OrderItemModifier[];
};

export type Order = {
  id: string;
  tenant_id: string;
  branch_id: string;
  order_number: number;
  /** "dine_in" | "pickup" */
  order_type: string;
  /** "pending" | "preparing" | "ready" | "delivered" | "cancelled" */
  status: string;
  table_number: string | null;
  customer_note: string | null;
  subtotal: number;
  total_amount: number;
  currency: string;
  placed_at: string;
  completed_at: string | null;
  cancelled_at: string | null;
  items: OrderItem[];
};

// ---------------------------------------------------------------------------
// Merchant API functions
// ---------------------------------------------------------------------------

export async function fetchOrders(statusFilter: string): Promise<Order[]> {
  const res = await authFetch(`/orders?status=${encodeURIComponent(statusFilter)}`);
  if (!res.ok) throw new Error(`Orders fetch failed: ${res.status}`);
  return res.json() as Promise<Order[]>;
}

export async function updateOrderStatus(
  orderId: string,
  newStatus: string
): Promise<Order> {
  const res = await authFetch(`/orders/${orderId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status: newStatus }),
  });
  if (!res.ok) throw new Error(`Status update failed: ${res.status}`);
  return res.json() as Promise<Order>;
}
