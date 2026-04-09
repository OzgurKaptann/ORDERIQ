"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  fetchCategories,
  fetchProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  fetchModifierGroups,
  type Category,
  type Product,
  type ModifierGroup,
  type ProductCreate,
} from "@/lib/merchant-api";
import { AuthError } from "@/lib/auth";
import styles from "../catalog.module.css";

type FormState = {
  category_id: string;
  name: string;
  description: string;
  base_price: string;
  tags: string;
  modifier_group_ids: string[];
};

const EMPTY_FORM: FormState = {
  category_id: "",
  name: "",
  description: "",
  base_price: "",
  tags: "",
  modifier_group_ids: [],
};

export default function ProductsPage() {
  const router = useRouter();

  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [modifierGroups, setModifierGroups] = useState<ModifierGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filterCatId, setFilterCatId] = useState<string>("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const handleAuthError = useCallback(() => {
    router.replace("/login");
  }, [router]);

  useEffect(() => {
    async function init() {
      try {
        const [cats, mods] = await Promise.all([
          fetchCategories(),
          fetchModifierGroups(),
        ]);
        cats.sort((a, b) => a.sort_order - b.sort_order);
        setCategories(cats);
        setModifierGroups(mods.filter((m) => m.is_active));
      } catch (err) {
        if (err instanceof AuthError) return handleAuthError();
        setError("Veriler yüklenemedi.");
      }
    }
    void init();
  }, [handleAuthError]);

  const loadProducts = useCallback(async () => {
    try {
      const data = await fetchProducts(filterCatId || undefined);
      setProducts(data);
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
      setError("Ürünler yüklenemedi.");
    } finally {
      setLoading(false);
    }
  }, [filterCatId, handleAuthError]);

  useEffect(() => {
    setLoading(true);
    void loadProducts();
  }, [loadProducts]);

  function openCreate() {
    setEditingId(null);
    setForm({
      ...EMPTY_FORM,
      category_id: filterCatId || categories[0]?.id || "",
    });
    setShowForm(true);
    setError(null);
  }

  function openEdit(p: Product) {
    setEditingId(p.id);
    setForm({
      category_id: p.category_id,
      name: p.name,
      description: p.description ?? "",
      base_price: String(p.base_price),
      tags: p.tags.join(", "),
      modifier_group_ids: [...p.modifier_group_ids],
    });
    setShowForm(true);
    setError(null);
  }

  function cancelForm() {
    setShowForm(false);
    setEditingId(null);
    setForm(EMPTY_FORM);
    setError(null);
  }

  function toggleModGroup(id: string) {
    setForm((f) => ({
      ...f,
      modifier_group_ids: f.modifier_group_ids.includes(id)
        ? f.modifier_group_ids.filter((x) => x !== id)
        : [...f.modifier_group_ids, id],
    }));
  }

  async function handleSave() {
    if (!form.name.trim()) { setError("Ürün adı zorunlu."); return; }
    if (!form.category_id) { setError("Kategori seçin."); return; }
    const price = parseFloat(form.base_price);
    if (isNaN(price) || price < 0) { setError("Geçerli bir fiyat girin."); return; }

    setSaving(true);
    setError(null);
    try {
      const payload: ProductCreate = {
        category_id: form.category_id,
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        base_price: price,
        tags: form.tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
        modifier_group_ids: form.modifier_group_ids,
      };
      if (editingId) {
        const updated = await updateProduct(editingId, payload);
        setProducts((prev) => prev.map((p) => (p.id === editingId ? updated : p)));
      } else {
        const created = await createProduct(payload);
        setProducts((prev) => [created, ...prev]);
      }
      cancelForm();
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
      setError(err instanceof Error ? err.message : "Kayıt başarısız.");
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleActive(p: Product) {
    try {
      const updated = await updateProduct(p.id, { is_active: !p.is_active });
      setProducts((prev) => prev.map((x) => (x.id === p.id ? updated : x)));
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
    }
  }

  async function handleDelete(p: Product) {
    if (!confirm(`"${p.name}" silinsin mi?`)) return;
    try {
      await deleteProduct(p.id);
      setProducts((prev) =>
        prev.map((x) => (x.id === p.id ? { ...x, is_active: false } : x))
      );
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
    }
  }

  const catName = (id: string) =>
    categories.find((c) => c.id === id)?.name ?? "—";

  if (loading) return <p className={styles.message}>Yükleniyor...</p>;

  return (
    <>
      <div className={styles.sectionHead}>
        <h2 className={styles.sectionTitle}>Ürünler</h2>
        <div className={styles.filterBar}>
          <label className={styles.filterLabel}>Kategori:</label>
          <select
            className={styles.select}
            value={filterCatId}
            onChange={(e) => setFilterCatId(e.target.value)}
            style={{ minWidth: 140 }}
          >
            <option value="">Tümü</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <button className={styles.addBtn} onClick={openCreate}>
          + Yeni Ürün
        </button>
      </div>

      {showForm && (
        <div className={styles.formPanel}>
          <p className={styles.formTitle}>
            {editingId ? "Ürünü Düzenle" : "Yeni Ürün"}
          </p>

          <div className={styles.formRow}>
            <div className={styles.field}>
              <label className={styles.label}>Ad *</label>
              <input
                className={styles.input}
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Ürün adı"
              />
            </div>
            <div className={styles.field} style={{ maxWidth: 180 }}>
              <label className={styles.label}>Fiyat *</label>
              <input
                className={styles.input}
                type="number"
                value={form.base_price}
                onChange={(e) =>
                  setForm((f) => ({ ...f, base_price: e.target.value }))
                }
                min={0}
                step={0.01}
                placeholder="0.00"
              />
            </div>
          </div>

          <div className={styles.formRow}>
            <div className={styles.field}>
              <label className={styles.label}>Kategori *</label>
              <select
                className={styles.select}
                value={form.category_id}
                onChange={(e) =>
                  setForm((f) => ({ ...f, category_id: e.target.value }))
                }
              >
                <option value="">Seçin</option>
                {categories.filter((c) => c.is_active).map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Etiketler (virgülle)</label>
              <input
                className={styles.input}
                value={form.tags}
                onChange={(e) => setForm((f) => ({ ...f, tags: e.target.value }))}
                placeholder="vegan, glutensiz, ..."
              />
            </div>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Açıklama</label>
            <textarea
              className={styles.textarea}
              value={form.description}
              onChange={(e) =>
                setForm((f) => ({ ...f, description: e.target.value }))
              }
              placeholder="(opsiyonel)"
            />
          </div>

          {modifierGroups.length > 0 && (
            <div className={styles.field}>
              <label className={styles.label}>Modifier Grupları</label>
              <div className={styles.checkGroup}>
                {modifierGroups.map((mg) => (
                  <label key={mg.id} className={styles.checkLabel}>
                    <input
                      type="checkbox"
                      checked={form.modifier_group_ids.includes(mg.id)}
                      onChange={() => toggleModGroup(mg.id)}
                    />
                    {mg.name}
                  </label>
                ))}
              </div>
            </div>
          )}

          {error && <p className={styles.errorBanner}>{error}</p>}

          <div className={styles.formActions}>
            <button className={styles.saveBtn} onClick={handleSave} disabled={saving}>
              {saving ? "Kaydediliyor..." : "Kaydet"}
            </button>
            <button className={styles.cancelBtn} onClick={cancelForm}>
              İptal
            </button>
          </div>
        </div>
      )}

      {!showForm && error && <p className={styles.errorBanner}>{error}</p>}

      <div className={styles.list}>
        {products.length === 0 && (
          <p className={styles.message}>
            {filterCatId ? "Bu kategoride ürün yok." : "Henüz ürün yok."}
          </p>
        )}
        {products.map((p) => (
          <div
            key={p.id}
            className={`${styles.row} ${!p.is_active ? styles.rowInactive : ""}`}
          >
            <div style={{ flex: 1, minWidth: 120 }}>
              <div className={styles.rowName}>{p.name}</div>
              <div className={styles.rowMeta}>{catName(p.category_id)}</div>
            </div>
            <span className={styles.rowMeta}>{p.base_price.toFixed(2)} ₺</span>
            <span
              className={`${styles.badge} ${p.is_active ? styles.badgeActive : styles.badgeInactive}`}
            >
              {p.is_active ? "Aktif" : "Pasif"}
            </span>
            <div className={styles.rowActions}>
              <button className={styles.editBtn} onClick={() => openEdit(p)}>
                Düzenle
              </button>
              <button
                className={styles.toggleBtn}
                onClick={() => handleToggleActive(p)}
              >
                {p.is_active ? "Pasif Yap" : "Aktif Yap"}
              </button>
              {p.is_active && (
                <button
                  className={styles.deleteBtn}
                  onClick={() => handleDelete(p)}
                >
                  Sil
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
