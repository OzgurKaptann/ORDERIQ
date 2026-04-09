"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  fetchModifierGroups,
  createModifierGroup,
  updateModifierGroup,
  deleteModifierGroup,
  type ModifierGroup,
  type ModifierGroupCreate,
} from "@/lib/merchant-api";
import { AuthError } from "@/lib/auth";
import styles from "../catalog.module.css";

type OptionDraft = { name: string; extra_price: string };

type FormState = {
  name: string;
  selection_type: string;
  is_required: boolean;
  min_select: string;
  max_select: string;
  options: OptionDraft[];
};

const EMPTY_FORM: FormState = {
  name: "",
  selection_type: "single",
  is_required: false,
  min_select: "0",
  max_select: "1",
  options: [{ name: "", extra_price: "0" }],
};

export default function ModifiersPage() {
  const router = useRouter();

  const [groups, setGroups] = useState<ModifierGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const handleAuthError = useCallback(() => {
    router.replace("/login");
  }, [router]);

  const load = useCallback(async () => {
    try {
      const data = await fetchModifierGroups();
      setGroups(data);
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
      setError("Modifier grupları yüklenemedi.");
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

  function openEdit(g: ModifierGroup) {
    setEditingId(g.id);
    setForm({
      name: g.name,
      selection_type: g.selection_type,
      is_required: g.is_required,
      min_select: String(g.min_select),
      max_select: String(g.max_select),
      options:
        g.options.length > 0
          ? g.options.map((o) => ({
              name: o.name,
              extra_price: String(o.extra_price),
            }))
          : [{ name: "", extra_price: "0" }],
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

  function addOption() {
    setForm((f) => ({
      ...f,
      options: [...f.options, { name: "", extra_price: "0" }],
    }));
  }

  function removeOption(idx: number) {
    setForm((f) => ({
      ...f,
      options: f.options.filter((_, i) => i !== idx),
    }));
  }

  function setOption(idx: number, field: keyof OptionDraft, value: string) {
    setForm((f) => {
      const opts = [...f.options];
      opts[idx] = { ...opts[idx], [field]: value };
      return { ...f, options: opts };
    });
  }

  async function handleSave() {
    if (!form.name.trim()) { setError("Grup adı zorunlu."); return; }
    const validOptions = form.options.filter((o) => o.name.trim());
    if (validOptions.length === 0) {
      setError("En az bir seçenek ekleyin.");
      return;
    }

    const minSel = parseInt(form.min_select, 10) || 0;
    const maxSel = parseInt(form.max_select, 10) || 1;
    if (minSel > maxSel) {
      setError("Min seçim, max seçimden büyük olamaz.");
      return;
    }

    setSaving(true);
    setError(null);
    try {
      const payload: ModifierGroupCreate = {
        name: form.name.trim(),
        selection_type: form.selection_type,
        is_required: form.is_required,
        min_select: minSel,
        max_select: maxSel,
        options: validOptions.map((o, i) => ({
          name: o.name.trim(),
          extra_price: parseFloat(o.extra_price) || 0,
          sort_order: i,
        })),
      };
      if (editingId) {
        const updated = await updateModifierGroup(editingId, payload);
        setGroups((prev) => prev.map((g) => (g.id === editingId ? updated : g)));
      } else {
        const created = await createModifierGroup(payload);
        setGroups((prev) => [created, ...prev]);
      }
      cancelForm();
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
      setError(err instanceof Error ? err.message : "Kayıt başarısız.");
    } finally {
      setSaving(false);
    }
  }

  async function handleToggleActive(g: ModifierGroup) {
    try {
      const updated = await updateModifierGroup(g.id, { is_active: !g.is_active });
      setGroups((prev) => prev.map((x) => (x.id === g.id ? updated : x)));
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
    }
  }

  async function handleDelete(g: ModifierGroup) {
    if (!confirm(`"${g.name}" silinsin mi?`)) return;
    try {
      await deleteModifierGroup(g.id);
      setGroups((prev) =>
        prev.map((x) => (x.id === g.id ? { ...x, is_active: false } : x))
      );
    } catch (err) {
      if (err instanceof AuthError) return handleAuthError();
    }
  }

  if (loading) return <p className={styles.message}>Yükleniyor...</p>;

  return (
    <>
      <div className={styles.sectionHead}>
        <h2 className={styles.sectionTitle}>Modifier Grupları</h2>
        <button className={styles.addBtn} onClick={openCreate}>
          + Yeni Grup
        </button>
      </div>

      {showForm && (
        <div className={styles.formPanel}>
          <p className={styles.formTitle}>
            {editingId ? "Grubu Düzenle" : "Yeni Modifier Grubu"}
          </p>

          <div className={styles.formRow}>
            <div className={styles.field}>
              <label className={styles.label}>Ad *</label>
              <input
                className={styles.input}
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Ekstra peynir, Boyut, ..."
              />
            </div>
            <div className={styles.field} style={{ maxWidth: 180 }}>
              <label className={styles.label}>Seçim tipi</label>
              <select
                className={styles.select}
                value={form.selection_type}
                onChange={(e) =>
                  setForm((f) => ({ ...f, selection_type: e.target.value }))
                }
              >
                <option value="single">Tekli</option>
                <option value="multiple">Çoklu</option>
              </select>
            </div>
          </div>

          <div className={styles.formRow}>
            <div className={styles.field} style={{ maxWidth: 160 }}>
              <label className={styles.label}>Min seçim</label>
              <input
                className={styles.input}
                type="number"
                value={form.min_select}
                onChange={(e) =>
                  setForm((f) => ({ ...f, min_select: e.target.value }))
                }
                min={0}
              />
            </div>
            <div className={styles.field} style={{ maxWidth: 160 }}>
              <label className={styles.label}>Max seçim</label>
              <input
                className={styles.input}
                type="number"
                value={form.max_select}
                onChange={(e) =>
                  setForm((f) => ({ ...f, max_select: e.target.value }))
                }
                min={1}
              />
            </div>
            <div className={styles.field} style={{ maxWidth: 160, justifyContent: "flex-end" }}>
              <label className={styles.checkLabel} style={{ marginTop: 22 }}>
                <input
                  type="checkbox"
                  checked={form.is_required}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, is_required: e.target.checked }))
                  }
                />
                Zorunlu
              </label>
            </div>
          </div>

          {/* Options */}
          <div className={styles.field}>
            <label className={styles.label}>Seçenekler *</label>
            <div className={styles.optionList}>
              {form.options.map((opt, idx) => (
                <div key={idx} className={styles.optionRow}>
                  <input
                    className={styles.optionInput}
                    value={opt.name}
                    onChange={(e) => setOption(idx, "name", e.target.value)}
                    placeholder={`Seçenek ${idx + 1}`}
                  />
                  <input
                    className={styles.optionInput}
                    type="number"
                    value={opt.extra_price}
                    onChange={(e) => setOption(idx, "extra_price", e.target.value)}
                    placeholder="Ekstra fiyat"
                    min={0}
                    step={0.01}
                    style={{ maxWidth: 120 }}
                  />
                  {form.options.length > 1 && (
                    <button
                      className={styles.removeOptionBtn}
                      onClick={() => removeOption(idx)}
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
              <button className={styles.addOptionBtn} onClick={addOption}>
                + Seçenek Ekle
              </button>
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
        {groups.length === 0 && (
          <p className={styles.message}>Henüz modifier grubu yok.</p>
        )}
        {groups.map((g) => (
          <div
            key={g.id}
            className={`${styles.row} ${!g.is_active ? styles.rowInactive : ""}`}
          >
            <div style={{ flex: 1, minWidth: 120 }}>
              <div className={styles.rowName}>{g.name}</div>
              <div className={styles.rowMeta}>
                {g.selection_type === "single" ? "Tekli" : "Çoklu"}
                {g.is_required ? " · Zorunlu" : ""}
                {" · "}
                {g.options.filter((o) => o.is_active).length} seçenek
              </div>
            </div>
            <span
              className={`${styles.badge} ${g.is_active ? styles.badgeActive : styles.badgeInactive}`}
            >
              {g.is_active ? "Aktif" : "Pasif"}
            </span>
            <div className={styles.rowActions}>
              <button className={styles.editBtn} onClick={() => openEdit(g)}>
                Düzenle
              </button>
              <button
                className={styles.toggleBtn}
                onClick={() => handleToggleActive(g)}
              >
                {g.is_active ? "Pasif Yap" : "Aktif Yap"}
              </button>
              {g.is_active && (
                <button
                  className={styles.deleteBtn}
                  onClick={() => handleDelete(g)}
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
