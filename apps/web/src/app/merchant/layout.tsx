"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/auth";

export default function MerchantLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
    } else {
      setAuthorized(true);
    }
  }, [router]);

  // Render nothing until auth is confirmed — prevents flash of protected content
  if (!authorized) return null;

  return <>{children}</>;
}
