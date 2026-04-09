"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useCart } from "@/context/CartContext";
import { submitOrder } from "@/lib/api";
import styles from "./checkout.module.css";

type Props = {
  slug: string;
  currency: string;
  /** "dine_in" | "pickup" | "both" */
  serviceMode: string;
  businessName: string;
};

export function CheckoutView({ slug, currency, serviceMode, businessName }: Props) {
  const { cart } = useCart();
  const router = useRouter();

  const showDineIn = serviceMode !== "pickup";
  const showPickup = serviceMode !== "dine_in";
  const defaultType = serviceMode === "pickup" ? "pickup" : "dine_in";

  const [orderType, setOrderType] = useState<"dine_in" | "pickup">(
    defaultType as "dine_in" | "pickup"
  );
  const [tableNumber, setTableNumber] = useState("");
  const [customerNote, setCustomerNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const total = cart.reduce((sum, i) => sum + i.lineTotal, 0);

  const canSubmit =
    !submitting &&
    cart.length > 0 &&
    (orderType === "pickup" || tableNumber.trim() !== "");

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setError(null);
    setSubmitting(true);

    try {
      const result = await submitOrder({
        slug,
        order_type: orderType,
        table_number: orderType === "dine_in" ? tableNumber.trim() : null,
        customer_note: customerNote.trim() || null,
        items: cart.map((item) => ({
          product_id: item.productId,
          quantity: item.quantity,
          modifiers: item.modifiers.map((m) => ({ modifier_option_id: m.optionId })),
        })),
      });

      router.push(`/m/${slug}/success?order=${result.order_number}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Sipariş gönderilemedi. Tekrar deneyin."
      );
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <Link href={`/m/${slug}/cart`} className={styles.backBtn}>
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
            {/* Order type — only shown when both modes are available */}
            {showDineIn && showPickup && (
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>Sipariş Tipi</h2>
                <div className={styles.typeRow}>
                  <button
                    className={`${styles.typeBtn} ${orderType === "dine_in" ? styles.typeSelected : ""}`}
                    onClick={() => setOrderType("dine_in")}
                  >
                    Masada
                  </button>
                  <button
                    className={`${styles.typeBtn} ${orderType === "pickup" ? styles.typeSelected : ""}`}
                    onClick={() => setOrderType("pickup")}
                  >
                    Gel Al
                  </button>
                </div>
              </section>
            )}

            {/* Table number — only for dine_in */}
            {orderType === "dine_in" && (
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>
                  Masa Numarası <span className={styles.required}>*</span>
                </h2>
                <input
                  className={styles.input}
                  type="text"
                  placeholder="Örn: 5"
                  value={tableNumber}
                  onChange={(e) => setTableNumber(e.target.value)}
                  maxLength={10}
                  autoComplete="off"
                />
              </section>
            )}

            {/* Optional note */}
            <section className={styles.section}>
              <h2 className={styles.sectionTitle}>Not (İsteğe Bağlı)</h2>
              <textarea
                className={styles.textarea}
                placeholder="Sipariş notu ekleyebilirsiniz..."
                value={customerNote}
                onChange={(e) => setCustomerNote(e.target.value)}
                rows={3}
                maxLength={300}
              />
            </section>

            {/* Order summary */}
            <section className={styles.section}>
              <h2 className={styles.sectionTitle}>Sipariş Özeti</h2>
              <div className={styles.summaryList}>
                {cart.map((item) => (
                  <div key={item.key} className={styles.summaryRow}>
                    <span className={styles.summaryName}>
                      {item.quantity}× {item.productName}
                      {item.modifiers.length > 0 && (
                        <span className={styles.summaryMods}>
                          {" "}
                          ({item.modifiers.map((m) => m.optionName).join(", ")})
                        </span>
                      )}
                    </span>
                    <span className={styles.summaryPrice}>
                      {item.lineTotal.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
              <div className={styles.totalRow}>
                <span>Toplam</span>
                <span className={styles.totalAmount}>
                  {total.toFixed(2)} {currency}
                </span>
              </div>
            </section>

            {error && <p className={styles.error}>{error}</p>}
          </main>

          <div className={styles.footer}>
            <button
              className={`${styles.submitBtn} ${!canSubmit ? styles.submitDisabled : ""}`}
              onClick={handleSubmit}
              disabled={!canSubmit}
            >
              {submitting
                ? "Gönderiliyor..."
                : `Siparişi Onayla · ${total.toFixed(2)} ${currency}`}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
