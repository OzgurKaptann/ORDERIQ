"use client";

import { useState } from "react";
import type { PublicProduct, PublicModifierGroup, CartItem } from "@/lib/api";
import styles from "./ProductModal.module.css";

type Props = {
  product: PublicProduct;
  currency: string;
  onClose: () => void;
  onAdd: (item: CartItem) => void;
};

export function ProductModal({ product, currency, onClose, onAdd }: Props) {
  const [selections, setSelections] = useState<Map<string, string[]>>(() => {
    const m = new Map<string, string[]>();
    product.modifier_groups.forEach((g) => m.set(g.id, []));
    return m;
  });
  const [quantity, setQuantity] = useState(1);

  const toggleOption = (group: PublicModifierGroup, optionId: string) => {
    setSelections((prev) => {
      const next = new Map(prev);
      const current = next.get(group.id) ?? [];

      if (group.selection_type === "single") {
        // Required groups: cannot deselect the currently selected option
        if (group.is_required && current[0] === optionId) return prev;
        next.set(group.id, current[0] === optionId ? [] : [optionId]);
      } else {
        if (current.includes(optionId)) {
          next.set(group.id, current.filter((id) => id !== optionId));
        } else if (current.length < group.max_select) {
          next.set(group.id, [...current, optionId]);
        }
      }
      return next;
    });
  };

  const modifierTotal = product.modifier_groups.reduce((sum, group) => {
    const selected = selections.get(group.id) ?? [];
    return (
      sum +
      group.options
        .filter((o) => selected.includes(o.id))
        .reduce((s, o) => s + o.extra_price, 0)
    );
  }, 0);

  const unitPrice = product.base_price + modifierTotal;
  const totalPrice = unitPrice * quantity;

  const canAdd = product.modifier_groups.every((group) => {
    if (!group.is_required) return true;
    const selected = selections.get(group.id) ?? [];
    return selected.length >= group.min_select;
  });

  const handleAdd = () => {
    if (!canAdd) return;

    const selectedModifiers = product.modifier_groups.flatMap((group) => {
      const selected = selections.get(group.id) ?? [];
      return group.options
        .filter((o) => selected.includes(o.id))
        .map((o) => ({ optionId: o.id, optionName: o.name, extraPrice: o.extra_price }));
    });

    const key = [product.id, ...selectedModifiers.map((m) => m.optionId).sort()].join("|");

    onAdd({
      key,
      productId: product.id,
      productName: product.name,
      basePrice: product.base_price,
      modifiers: selectedModifiers,
      quantity,
      lineTotal: totalPrice,
    });
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.sheet} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.modalHeader}>
          <h2 className={styles.productName}>{product.name}</h2>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Kapat">
            ✕
          </button>
        </div>

        {/* Scrollable body */}
        <div className={styles.body}>
          {product.description && (
            <p className={styles.productDesc}>{product.description}</p>
          )}

          {product.modifier_groups.map((group) => {
            const selected = selections.get(group.id) ?? [];
            return (
              <div key={group.id} className={styles.groupSection}>
                <div className={styles.groupHeader}>
                  <span className={styles.groupName}>{group.name}</span>
                  {group.is_required && (
                    <span className={styles.badge}>Zorunlu</span>
                  )}
                  {group.selection_type === "multiple" && (
                    <span className={styles.hint}>En fazla {group.max_select}</span>
                  )}
                </div>
                <div className={styles.optionList}>
                  {group.options.map((option) => {
                    const isSelected = selected.includes(option.id);
                    const isDisabled =
                      !isSelected &&
                      group.selection_type === "multiple" &&
                      selected.length >= group.max_select;
                    return (
                      <button
                        key={option.id}
                        className={`${styles.optionBtn} ${isSelected ? styles.selected : ""} ${isDisabled ? styles.dimmed : ""}`}
                        onClick={() => !isDisabled && toggleOption(group, option.id)}
                      >
                        <span>{option.name}</span>
                        {option.extra_price > 0 && (
                          <span className={styles.extraPrice}>
                            +{option.extra_price.toFixed(2)}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <div className={styles.quantityRow}>
            <button
              className={styles.qtyBtn}
              onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              aria-label="Azalt"
            >
              −
            </button>
            <span className={styles.qtyValue}>{quantity}</span>
            <button
              className={styles.qtyBtn}
              onClick={() => setQuantity((q) => q + 1)}
              aria-label="Artır"
            >
              +
            </button>
          </div>
          <button
            className={`${styles.addBtn} ${!canAdd ? styles.addBtnDisabled : ""}`}
            onClick={handleAdd}
            disabled={!canAdd}
          >
            Sepete Ekle · {totalPrice.toFixed(2)} {currency}
          </button>
        </div>
      </div>
    </div>
  );
}
