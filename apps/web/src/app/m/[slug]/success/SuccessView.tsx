"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useCart } from "@/context/CartContext";
import styles from "./success.module.css";

type Props = {
  slug: string;
  orderNumber: string | null;
};

export function SuccessView({ slug, orderNumber }: Props) {
  const { clearCart } = useCart();

  // Clear cart once on mount — after successful order
  useEffect(() => {
    clearCart();
  }, [clearCart]);

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.icon}>✓</div>
        <h1 className={styles.title}>Siparişiniz Alındı!</h1>

        {orderNumber && (
          <p className={styles.orderNumber}>
            Sipariş No: <strong>#{orderNumber}</strong>
          </p>
        )}

        <p className={styles.subtitle}>
          Siparişiniz hazırlanmaya başlandı.
        </p>

        <Link href={`/m/${slug}`} className={styles.backBtn}>
          Menüye Dön
        </Link>
      </div>
    </div>
  );
}
