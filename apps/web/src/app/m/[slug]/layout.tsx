import { CartProvider } from "@/context/CartContext";
import type { ReactNode } from "react";

export default function MenuLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: { slug: string };
}) {
  return <CartProvider slug={params.slug}>{children}</CartProvider>;
}
