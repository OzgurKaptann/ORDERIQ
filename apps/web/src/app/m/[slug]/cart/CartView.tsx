"use client";

import Link from "next/link";
import { useCart } from "@/context/CartContext";
import styles from "./cart.module.css";

type Props = {
  slug: string;
  currency: string;
  businessName: string;
};

export function CartView({ slug, currency, businessName }: Props) {
  const { cart, updateQuantity, removeItem } = useCart();

  const total = cart.reduce((sum, i) => sum + i.lineTotal, 0);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <Link href={`/m/${slug}`} className={styles.backBtn}>
          ← Geri
        </Link>
        <span className={styles.headerTitle}>{businessName}</span>
      </header>

      {cart.length === 0 ? (
        <div className={styles.empty}>
          <p className={styles.emptyText}>Sepetiniz boş.</p>
          <Link href={`/m/${slug}`} className={styles.emptyLink}>
            Menüye Dön
          </Link>
        </div>
      ) : (
        <>
          <main className={styles.main}>
            <div className={styles.itemList}>
              {cart.map((item) => (
                <div key={item.key} className={styles.cartItem}>
                  <div className={styles.itemTop}>
                    <span className={styles.itemName}>{item.productName}</span>
                    <button
                      className={styles.removeBtn}
                      onClick={() => removeItem(item.key)}
                      aria-label="Kaldır"
                    >
                      ✕
                    </button>
                  </div>

                  {item.modifiers.length > 0 && (
                    <p className={styles.modifiers}>
                      {item.modifiers.map((m) => m.optionName).join(", ")}
                    </p>
                  )}

                  <div className={styles.itemBottom}>
                    <div className={styles.qtyRow}>
                      <button
                        className={styles.qtyBtn}
                        onClick={() => updateQuantity(item.key, item.quantity - 1)}
                        aria-label="Azalt"
                      >
                        −
                      </button>
                      <span className={styles.qtyVal}>{item.quantity}</span>
                      <button
                        className={styles.qtyBtn}
                        onClick={() => updateQuantity(item.key, item.quantity + 1)}
                        aria-label="Artır"
                      >
                        +
                      </button>
                    </div>
                    <span className={styles.itemPrice}>
                      {item.lineTotal.toFixed(2)} {currency}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className={styles.summary}>
              <span className={styles.summaryLabel}>Toplam</span>
              <span className={styles.summaryTotal}>
                {total.toFixed(2)} {currency}
              </span>
            </div>
          </main>

          <div className={styles.footer}>
            <Link href={`/m/${slug}/checkout`} className={styles.checkoutBtn}>
              Ödemeye Geç
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
