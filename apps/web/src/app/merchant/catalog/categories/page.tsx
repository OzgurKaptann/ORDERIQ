"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  fetchCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  type Category,
  type CategoryCreate,
} from "@/lib/merchant-api";
import { AuthError } from "@/lib/auth";
import styles from "../catalog.module.css";

type FormState = {
  name: string;
  sort_order: string;
};

const EMPTY_FORM: FormState = { name: "", sort_order: "0" };

export default function CategoriesPage() {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const handleAuthError = useCallback(() => {
    router.replace("/login");
  }, [router]);

  const load = useCallback(async () => {
    try {
      const data = await fetchCategories();
      data.sort((a, b) => a.sort_order - b.sort_order);
      setCategories(data);
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
      setError("Kategoriler yüklenemedi.");
    } finally {
      setLoading(false);
    }
  }, [handleAuthError]);

  useEffect(() => {
    void load();
  }, [load]);

  function openCreate() {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
    setError(null);
  }

  function openEdit(cat: Category) {
    setEditingId(cat.id);
    setForm({
      name: cat.name,
      sort_order: String(cat.sort_order),
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

  async function handleSave() {
    if (!form.name.trim()) {
      setError("Kategori adı zorunlu.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const payload: CategoryCreate = {
        name: form.name.trim(),
        sort_order: parseInt(form.sort_order, 10) || 0,
      };
      if (editingId) {
        const updated = await updateCategory(editingId, payload);
        setCategories((prev) =>
          prev.map((c) => (c.id === editingId ? updated : c))
        );
      } else {
        const created = await createCategory(payload);
        setCategories((prev) =>
          [...prev, created].sort((a, b) => a.sort_order - b.sort_order)
        );
      }
      cancelForm();
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
      setError(err instanceof Error ? err.message : "Kayıt başarısız.");
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleActive(cat: Category) {
    try {
      const updated = await updateCategory(cat.id, { is_active: !cat.is_active });
      setCategories((prev) => prev.map((c) => (c.id === cat.id ? updated : c)));
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
    }
  }

  async function handleDelete(cat: Category) {
    if (!confirm(`"${cat.name}" silinsin mi? (pasif yapılır)`)) return;
    try {
      await deleteCategory(cat.id);
      setCategories((prev) =>
        prev.map((c) => (c.id === cat.id ? { ...c, is_active: false } : c))
      );
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
    }
  }

  if (loading) return <p className={styles.message}>Yükleniyor...</p>;

  return (
    <>
      <div className={styles.sectionHead}>
        <h2 className={styles.sectionTitle}>Kategoriler</h2>
        <button className={styles.addBtn} onClick={openCreate}>
          + Yeni Kategori
        </button>
      </div>

      {showForm && (
        <div className={styles.formPanel}>
          <p className={styles.formTitle}>
            {editingId ? "Kategoriyi Düzenle" : "Yeni Kategori"}
          </p>

          <div className={styles.formRow}>
            <div className={styles.field}>
              <label className={styles.label}>Ad *</label>
              <input
                className={styles.input}
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Kategori adı"
              />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Sıra</label>
              <input
                className={styles.input}
                type="number"
                value={form.sort_order}
                onChange={(e) =>
                  setForm((f) => ({ ...f, sort_order: e.target.value }))
                }
                min={0}
              />
            </div>
          </div>

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
        {categories.length === 0 && (
          <p className={styles.message}>Henüz kategori yok.</p>
        )}
        {categories.map((cat) => (
          <div
            key={cat.id}
            className={`${styles.row} ${!cat.is_active ? styles.rowInactive : ""}`}
          >
            <span className={styles.rowName}>{cat.name}</span>
            <span className={styles.rowMeta}>Sıra: {cat.sort_order}</span>
            <span
              className={`${styles.badge} ${cat.is_active ? styles.badgeActive : styles.badgeInactive}`}
            >
              {cat.is_active ? "Aktif" : "Pasif"}
            </span>
            <div className={styles.rowActions}>
              <button className={styles.editBtn} onClick={() => openEdit(cat)}>
                Düzenle
              </button>
              <button
                className={styles.toggleBtn}
                onClick={() => handleToggleActive(cat)}
              >
                {cat.is_active ? "Pasif Yap" : "Aktif Yap"}
              </button>
              {cat.is_active && (
                <button
                  className={styles.deleteBtn}
                  onClick={() => handleDelete(cat)}
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
