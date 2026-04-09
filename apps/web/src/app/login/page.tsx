import type { Metadata } from "next";
import { LoginView } from "./LoginView";

export const metadata: Metadata = { title: "Giriş — OrderIQ" };

export default function LoginPage() {
  return <LoginView />;
}
