import { authFetch } from "./auth";

// ---------------------------------------------------------------------------
// Category types
// ---------------------------------------------------------------------------

export type Category = {
  id: string;
  tenant_id: string;
  branch_id: string;
  name: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
};

export type CategoryCreate = {
  name: string;
  sort_order?: number;
};

export type CategoryUpdate = Partial<CategoryCreate & { is_active: boolean }>;

// ---------------------------------------------------------------------------
// Product types
// ---------------------------------------------------------------------------

export type Product = {
  id: string;
  tenant_id: string;
  branch_id: string;
  category_id: string;
  name: string;
  description: string | null;
  image_url: string | null;
  base_price: number;
  is_active: boolean;
  is_in_stock: boolean;
  prep_time_minutes: number | null;
  tags: string[];
  modifier_group_ids: string[];
  created_at: string;
};

export type ProductCreate = {
  category_id: string;
  name: string;
  description?: string;
  base_price: number;
  tags?: string[];
  modifier_group_ids?: string[];
};

export type ProductUpdate = Partial<
  ProductCreate & { is_active: boolean }
>;

// ---------------------------------------------------------------------------
// Modifier types
// ---------------------------------------------------------------------------

export type ModifierOption = {
  id: string;
  name: string;
  extra_price: number;
  is_active: boolean;
  sort_order: number;
};

export type ModifierGroup = {
  id: string;
  tenant_id: string;
  branch_id: string;
  name: string;
  selection_type: string;
  is_required: boolean;
  min_select: number;
  max_select: number;
  is_active: boolean;
  options: ModifierOption[];
};

export type ModifierGroupCreate = {
  name: string;
  selection_type: string;
  is_required?: boolean;
  min_select?: number;
  max_select?: number;
  options?: { name: string; extra_price?: number; sort_order?: number }[];
};

export type ModifierGroupUpdate = Partial<ModifierGroupCreate & { is_active: boolean }>;

// ---------------------------------------------------------------------------
// Category API
// ---------------------------------------------------------------------------

export async function fetchCategories(): Promise<Category[]> {
  const res = await authFetch("/categories");
  if (!res.ok) throw new Error(`Failed to fetch categories: ${res.status}`);
  return res.json() as Promise<Category[]>;
}

export async function createCategory(data: CategoryCreate): Promise<Category> {
  const res = await authFetch("/categories", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create category: ${res.status}`);
  return res.json() as Promise<Category>;
}

export async function updateCategory(
  id: string,
  data: CategoryUpdate
): Promise<Category> {
  const res = await authFetch(`/categories/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update category: ${res.status}`);
  return res.json() as Promise<Category>;
}

export async function deleteCategory(id: string): Promise<void> {
  const res = await authFetch(`/categories/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204)
    throw new Error(`Failed to delete category: ${res.status}`);
}

// ---------------------------------------------------------------------------
// Product API
// ---------------------------------------------------------------------------

export async function fetchProducts(categoryId?: string): Promise<Product[]> {
  const qs = categoryId
    ? `?category_id=${encodeURIComponent(categoryId)}`
    : "";
  const res = await authFetch(`/products${qs}`);
  if (!res.ok) throw new Error(`Failed to fetch products: ${res.status}`);
  return res.json() as Promise<Product[]>;
}

export async function createProduct(data: ProductCreate): Promise<Product> {
  const res = await authFetch("/products", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create product: ${res.status}`);
  return res.json() as Promise<Product>;
}

export async function updateProduct(
  id: string,
  data: ProductUpdate
): Promise<Product> {
  const res = await authFetch(`/products/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update product: ${res.status}`);
  return res.json() as Promise<Product>;
}

export async function deleteProduct(id: string): Promise<void> {
  const res = await authFetch(`/products/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204)
    throw new Error(`Failed to delete product: ${res.status}`);
}

// ---------------------------------------------------------------------------
// Modifier Group API
// ---------------------------------------------------------------------------

export async function fetchModifierGroups(): Promise<ModifierGroup[]> {
  const res = await authFetch("/modifier-groups");
  if (!res.ok) throw new Error(`Failed to fetch modifier groups: ${res.status}`);
  return res.json() as Promise<ModifierGroup[]>;
}

export async function createModifierGroup(
  data: ModifierGroupCreate
): Promise<ModifierGroup> {
  const res = await authFetch("/modifier-groups", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create modifier group: ${res.status}`);
  return res.json() as Promise<ModifierGroup>;
}

export async function updateModifierGroup(
  id: string,
  data: ModifierGroupUpdate
): Promise<ModifierGroup> {
  const res = await authFetch(`/modifier-groups/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update modifier group: ${res.status}`);
  return res.json() as Promise<ModifierGroup>;
}

export async function deleteModifierGroup(id: string): Promise<void> {
  const res = await authFetch(`/modifier-groups/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204)
    throw new Error(`Failed to delete modifier group: ${res.status}`);
}

// ---------------------------------------------------------------------------
// QR Code types
// ---------------------------------------------------------------------------

export type QRCode = {
  id: string;
  code_type: "generic" | "table";
  table_number: string | null;
  target_url: string;
  image_url: string;
  created_at: string;
};

export type QRGeneratePayload = {
  code_type: "generic" | "table";
  table_number?: string;
};

// ---------------------------------------------------------------------------
// QR Code API
// ---------------------------------------------------------------------------

export async function fetchQRCodes(): Promise<QRCode[]> {
  const res = await authFetch("/qr");
  if (!res.ok) throw new Error(`QR fetch failed: ${res.status}`);
  return res.json() as Promise<QRCode[]>;
}

export async function generateQRCode(data: QRGeneratePayload): Promise<QRCode> {
  const res = await authFetch("/qr/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`QR generate failed: ${res.status}`);
  return res.json() as Promise<QRCode>;
}

// ---------------------------------------------------------------------------
// Analytics types
// ---------------------------------------------------------------------------

export type AnalyticsSummary = {
  today_order_count: number;
  today_revenue: number;
  average_basket_value: number;
  // backend does not return currency; omitted intentionally
};

export type TopProduct = {
  product_name: string;
  total_quantity: number; // backend field name; was incorrectly typed as order_count
};

export type HourlyOrder = {
  hour: number;        // 0-23
  order_count: number;
};

// ---------------------------------------------------------------------------
// Analytics API
// ---------------------------------------------------------------------------

export async function fetchAnalyticsSummary(): Promise<AnalyticsSummary> {
  const res = await authFetch("/analytics/summary");
  if (!res.ok) throw new Error(`Analytics summary failed: ${res.status}`);
  return res.json() as Promise<AnalyticsSummary>;
}

export async function fetchTopProducts(): Promise<TopProduct[]> {
  const res = await authFetch("/analytics/top-products");
  if (!res.ok) throw new Error(`Top products failed: ${res.status}`);
  // Backend wraps the list: { products: [...] }
  const data = await res.json() as { products?: TopProduct[] };
  return Array.isArray(data.products) ? data.products : [];
}

export async function fetchHourlyOrders(): Promise<HourlyOrder[]> {
  const res = await authFetch("/analytics/hourly-orders");
  if (!res.ok) throw new Error(`Hourly orders failed: ${res.status}`);
  // Backend wraps the list: { distribution: [...] }
  const data = await res.json() as { distribution?: HourlyOrder[] };
  return Array.isArray(data.distribution) ? data.distribution : [];
}
