import { notFound } from "next/navigation";
import { fetchMenu } from "@/lib/api";
import { MenuView } from "./MenuView";

type Props = {
  params: { slug: string };
};

export async function generateMetadata({ params }: Props) {
  try {
    const menu = await fetchMenu(params.slug);
    return { title: menu.business_name };
  } catch {
    return { title: "Menü" };
  }
}

export default async function MenuPage({ params }: Props) {
  try {
    const menu = await fetchMenu(params.slug);
    return <MenuView menu={menu} />;
  } catch {
    notFound();
  }
}
