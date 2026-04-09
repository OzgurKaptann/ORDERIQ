"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import styles from "./catalog.module.css";

const TABS = [
  { href: "/merchant/catalog/categories", label: "Kategoriler" },
  { href: "/merchant/catalog/products", label: "Ürünler" },
  { href: "/merchant/catalog/modifiers", label: "Modifier Grupları" },
];

export default function CatalogLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className={styles.shell}>
      <nav className={styles.topNav}>
        <Link href="/merchant/kitchen" className={styles.backLink}>
          ← Mutfak
        </Link>
        <span className={styles.navTitle}>Katalog</span>
        <div className={styles.tabs}>
          {TABS.map((t) => (
            <Link
              key={t.href}
              href={t.href}
              className={`${styles.tab} ${pathname === t.href ? styles.tabActive : ""}`}
            >
              {t.label}
            </Link>
          ))}
        </div>
      </nav>
      <div className={styles.body}>{children}</div>
    </div>
  );
}
