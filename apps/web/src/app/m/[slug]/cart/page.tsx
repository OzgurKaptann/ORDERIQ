import { notFound } from "next/navigation";
import { fetchMenu } from "@/lib/api";
import { CartView } from "./CartView";

type Props = { params: { slug: string } };

export async function generateMetadata({ params }: Props) {
  try {
    const menu = await fetchMenu(params.slug);
    return { title: `Sepet — ${menu.business_name}` };
  } catch {
    return { title: "Sepet" };
  }
}

export default async function CartPage({ params }: Props) {
  try {
    const menu = await fetchMenu(params.slug);
    return (
      <CartView
        slug={params.slug}
        currency={menu.currency}
        businessName={menu.business_name}
      />
    );
  } catch {
    notFound();
  }
}
