import { notFound } from "next/navigation";
import { fetchMenu } from "@/lib/api";
import { CheckoutView } from "./CheckoutView";

type Props = { params: { slug: string } };

export async function generateMetadata({ params }: Props) {
  try {
    const menu = await fetchMenu(params.slug);
    return { title: `Sipariş Ver — ${menu.business_name}` };
  } catch {
    return { title: "Sipariş Ver" };
  }
}

export default async function CheckoutPage({ params }: Props) {
  try {
    const menu = await fetchMenu(params.slug);
    return (
      <CheckoutView
        slug={params.slug}
        currency={menu.currency}
        serviceMode={menu.service_mode}
        businessName={menu.business_name}
      />
    );
  } catch {
    notFound();
  }
}
