"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import type { CartItem } from "@/lib/api";

type CartContextValue = {
  cart: CartItem[];
  addToCart: (item: CartItem) => void;
  updateQuantity: (key: string, quantity: number) => void;
  removeItem: (key: string) => void;
  clearCart: () => void;
};

const CartContext = createContext<CartContextValue | null>(null);

function storageKey(slug: string) {
  return `orderiq_cart_${slug}`;
}

function loadCart(slug: string): CartItem[] {
  try {
    const raw = localStorage.getItem(storageKey(slug));
    return raw ? (JSON.parse(raw) as CartItem[]) : [];
  } catch {
    return [];
  }
}

export function CartProvider({ slug, children }: { slug: string; children: ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [hydrated, setHydrated] = useState(false);

  // Load from localStorage after mount — avoids SSR hydration mismatch
  useEffect(() => {
    setCart(loadCart(slug));
    setHydrated(true);
  }, [slug]);

  // Persist to localStorage after every change (skip the initial server render)
  useEffect(() => {
    if (!hydrated) return;
    try {
      localStorage.setItem(storageKey(slug), JSON.stringify(cart));
    } catch {
      // localStorage unavailable — ignore silently
    }
  }, [cart, slug, hydrated]);

  const addToCart = useCallback((item: CartItem) => {
    setCart((prev) => {
      const idx = prev.findIndex((i) => i.key === item.key);
      if (idx >= 0) {
        return prev.map((i, n) =>
          n === idx
            ? {
                ...i,
                quantity: i.quantity + item.quantity,
                lineTotal: i.lineTotal + item.lineTotal,
              }
            : i
        );
      }
      return [...prev, item];
    });
  }, []);

  const updateQuantity = useCallback((key: string, quantity: number) => {
    if (quantity < 1) return;
    setCart((prev) =>
      prev.map((i) => {
        if (i.key !== key) return i;
        const unitPrice =
          i.basePrice + i.modifiers.reduce((s, m) => s + m.extraPrice, 0);
        return { ...i, quantity, lineTotal: unitPrice * quantity };
      })
    );
  }, []);

  const removeItem = useCallback((key: string) => {
    setCart((prev) => prev.filter((i) => i.key !== key));
  }, []);

  const clearCart = useCallback(() => {
    setCart([]);
    try {
      localStorage.removeItem(storageKey(slug));
    } catch {
      // ignore
    }
  }, [slug]);

  return (
    <CartContext.Provider value={{ cart, addToCart, updateQuantity, removeItem, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
