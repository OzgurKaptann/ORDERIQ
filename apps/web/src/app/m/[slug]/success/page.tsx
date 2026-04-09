import type { Metadata } from "next";
import { SuccessView } from "./SuccessView";

export const metadata: Metadata = { title: "Sipariş Alındı" };

type Props = {
  params: { slug: string };
  searchParams: { order?: string };
};

export default function SuccessPage({ params, searchParams }: Props) {
  return (
    <SuccessView
      slug={params.slug}
      orderNumber={searchParams.order ?? null}
    />
  );
}
