import { redirect } from "next/navigation";

export default function CatalogIndex() {
  redirect("/merchant/catalog/categories");
}
