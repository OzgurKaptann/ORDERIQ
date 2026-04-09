"use client";

import Link from "next/link";
import styles from "./CartBar.module.css";

type Props = {
  count: number;
  total: number;
  currency: string;
  href: string;
};

export function CartBar({ count, total, currency, href }: Props) {
  return (
    <div className={styles.bar}>
      <Link href={href} className={styles.inner}>
        <span className={styles.count}>{count} ürün</span>
        <span className={styles.label}>Sepetim</span>
        <span className={styles.total}>
          {total.toFixed(2)} {currency}
        </span>
      </Link>
    </div>
  );
}
