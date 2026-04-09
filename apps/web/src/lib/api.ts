// ---------------------------------------------------------------------------
// Types — mirror PublicMenuResponse from the backend
// ---------------------------------------------------------------------------

export type PublicModifierOption = {
  id: string;
  name: string;
  extra_price: number;
  sort_order: number;
};

export type PublicModifierGroup = {
  id: string;
  name: string;
  selection_type: string; // "single" | "multiple"
  is_required: boolean;
  min_select: number;
  max_select: number;
  options: PublicModifierOption[];
};

export type PublicProduct = {
  id: string;
  name: string;
  description: string | null;
  image_url: string | null;
  base_price: number;
  is_in_stock: boolean;
  prep_time_minutes: number | null;
  modifier_groups: PublicModifierGroup[];
};

export type PublicCategory = {
  id: string;
  name: string;
  sort_order: number;
  products: PublicProduct[];
};

export type PublicMenuResponse = {
  tenant_id: string;
  business_name: string;
  slug: string;
  currency: string;
  service_mode: string;
  accepts_orders: boolean;
  categories: PublicCategory[];
};

// ---------------------------------------------------------------------------
// Cart types
// ---------------------------------------------------------------------------

export type CartModifier = {
  optionId: string;
  optionName: string;
  extraPrice: number;
};

export type CartItem = {
  /** Stable key: productId + sorted modifier optionIds */
  key: string;
  productId: string;
  productName: string;
  basePrice: number;
  modifiers: CartModifier[];
  quantity: number;
  lineTotal: number;
};

// ---------------------------------------------------------------------------
// Fetch helpers
// ---------------------------------------------------------------------------

/**
 * Server-side: uses API_URL (docker internal network).
 * Client-side: uses NEXT_PUBLIC_API_URL (browser-accessible).
 */
function getApiBaseUrl(): string {
  if (typeof window === "undefined") {
    return (
      process.env.API_URL ??
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000"
    );
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export async function fetchMenu(slug: string): Promise<PublicMenuResponse> {
  const res = await fetch(`${getApiBaseUrl()}/public/menu/${slug}`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) {
    throw new Error(`Menu fetch failed: ${res.status}`);
  }
  return res.json() as Promise<PublicMenuResponse>;
}

export function resolveMediaUrl(url: string): string {
  if (url.startsWith("http")) return url;
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return `${base}${url}`;
}

// ---------------------------------------------------------------------------
// Order submission — public, no auth
// ---------------------------------------------------------------------------

export type SubmitOrderPayload = {
  slug: string;
  order_type: "dine_in" | "pickup";
  table_number: string | null;
  customer_note: string | null;
  items: Array<{
    product_id: string;
    quantity: number;
    modifiers: Array<{ modifier_option_id: string }>;
  }>;
};

export type SubmitOrderResponse = {
  id: string;
  order_number: number;
  status: string;
  order_type: string;
  table_number: string | null;
  customer_note: string | null;
  total_amount: number;
  currency: string;
  placed_at: string;
};

export async function submitOrder(
  payload: SubmitOrderPayload
): Promise<SubmitOrderResponse> {
  const res = await fetch(`${getApiBaseUrl()}/public/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const data: { detail?: string } = await res.json().catch(() => ({}));
    throw new Error(data.detail ?? `Sipariş gönderilemedi (${res.status})`);
  }
  return res.json() as Promise<SubmitOrderResponse>;
}
