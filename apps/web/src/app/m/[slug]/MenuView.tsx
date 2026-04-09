"use client";

import { useState, useRef } from "react";
import type { PublicMenuResponse, PublicProduct } from "@/lib/api";
import { resolveMediaUrl } from "@/lib/api";
import { useCart } from "@/context/CartContext";
import { ProductModal } from "@/components/ProductModal";
import { CartBar } from "@/components/CartBar";
import styles from "./menu.module.css";

type Props = {
  menu: PublicMenuResponse;
};

export function MenuView({ menu }: Props) {
  const { cart, addToCart } = useCart();
  const [openProduct, setOpenProduct] = useState<PublicProduct | null>(null);
  const sectionRefs = useRef<Record<string, HTMLElement | null>>({});

  const scrollToCategory = (id: string) => {
    sectionRefs.current[id]?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const cartTotal = cart.reduce((sum, i) => sum + i.lineTotal, 0);
  const cartCount = cart.reduce((sum, i) => sum + i.quantity, 0);
  const activeCategories = menu.categories.filter((c) =>
    c.products.some((p) => p.is_in_stock)
  );

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.businessName}>{menu.business_name}</h1>
      </header>

      <nav className={styles.categoryNav}>
        <div className={styles.categoryTabs}>
          {activeCategories.map((cat) => (
            <button
              key={cat.id}
              className={styles.categoryTab}
              onClick={() => scrollToCategory(cat.id)}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </nav>

      <main className={styles.main}>
        {activeCategories.map((cat) => (
          <section
            key={cat.id}
            ref={(el) => {
              sectionRefs.current[cat.id] = el;
            }}
            className={styles.categorySection}
          >
            <h2 className={styles.categoryName}>{cat.name}</h2>
            <div className={styles.productList}>
              {cat.products
                .filter((p) => p.is_in_stock)
                .map((product) => (
                  <button
                    key={product.id}
                    className={styles.productCard}
                    onClick={() => setOpenProduct(product)}
                  >
                    <div className={styles.productInfo}>
                      <span className={styles.productName}>{product.name}</span>
                      {product.description && (
                        <span className={styles.productDesc}>{product.description}</span>
                      )}
                      <span className={styles.productPrice}>
                        {product.base_price.toFixed(2)} {menu.currency}
                      </span>
                    </div>
                    {product.image_url && (
                      /* eslint-disable-next-line @next/next/no-img-element */
                      <img
                        src={resolveMediaUrl(product.image_url)}
                        alt={product.name}
                        className={styles.productImage}
                      />
                    )}
                  </button>
                ))}
            </div>
          </section>
        ))}
      </main>

      {openProduct && (
        <ProductModal
          product={openProduct}
          currency={menu.currency}
          onClose={() => setOpenProduct(null)}
          onAdd={(item) => {
            addToCart(item);
            setOpenProduct(null);
          }}
        />
      )}

      {cartCount > 0 && (
        <CartBar
          count={cartCount}
          total={cartTotal}
          currency={menu.currency}
          href={`/m/${menu.slug}/cart`}
        />
      )}
    </div>
  );
}
