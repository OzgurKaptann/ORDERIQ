"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  fetchOrders,
  updateOrderStatus,
  clearToken,
  AuthError,
  type Order,
} from "@/lib/auth";
import styles from "./kitchen.module.css";

// ---------------------------------------------------------------------------
// Static config
// ---------------------------------------------------------------------------

const FILTERS = [
  { value: "pending", label: "Bekleyen" },
  { value: "preparing", label: "Hazırlanıyor" },
  { value: "ready", label: "Hazır" },
] as const;

type FilterValue = (typeof FILTERS)[number]["value"];

const STATUS_ACTIONS: Record<
  string,
  Array<{ label: string; next: string; danger?: boolean }>
> = {
  pending: [
    { label: "Hazırlanıyor", next: "preparing" },
    { label: "İptal", next: "cancelled", danger: true },
  ],
  preparing: [
    { label: "Hazir", next: "ready" },
    { label: "İptal", next: "cancelled", danger: true },
  ],
  ready: [{ label: "Teslim Edildi", next: "delivered" }],
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatElapsed(placedAt: string, now: number): string {
  const diffMs = now - new Date(placedAt).getTime();
  const totalSec = Math.max(0, Math.floor(diffMs / 1000));
  const min = Math.floor(totalSec / 60);
  const sec = totalSec % 60;
  if (min === 0) return `${sec}s`;
  return `${min}dk ${sec}s`;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("tr-TR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function elapsedClass(placedAt: string): string {
  const diffMin = (Date.now() - new Date(placedAt).getTime()) / 60000;
  if (diffMin >= 15) return styles.elapsedAlert;
  if (diffMin >= 8) return styles.elapsedWarn;
  return "";
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function KitchenPage() {
  const router = useRouter();
  const [filter, setFilter] = useState<FilterValue>("pending");
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [now, setNow] = useState(() => Date.now());
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const handleAuthError = useCallback(() => {
    clearToken();
    router.replace("/login");
  }, [router]);

  const load = useCallback(async () => {
    try {
      const data = await fetchOrders(filter);
      // Sort oldest first — most urgent orders appear first
      data.sort(
        (a, b) =>
          new Date(a.placed_at).getTime() - new Date(b.placed_at).getTime()
      );
      setOrders(data);
    } catch (err) {
      if (err instanceof AuthError) {
        handleAuthError();
      }
      // Network errors: silently keep existing orders
    } finally {
      setLoading(false);
    }
  }, [filter, handleAuthError]);

  // Reset + poll on filter change
  useEffect(() => {
    setLoading(true);
    setOrders([]);
    void load();
    const pollId = setInterval(() => void load(), 5000);
    return () => clearInterval(pollId);
  }, [load]);

  // 1-second tick for elapsed time display
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  const handleStatusUpdate = async (orderId: string, newStatus: string) => {
    setUpdatingId(orderId);
    try {
      await updateOrderStatus(orderId, newStatus);
      // Remove from current list — it's no longer in this status bucket
      setOrders((prev) => prev.filter((o) => o.id !== orderId));
    } catch (err) {
      if (err instanceof AuthError) handleAuthError();
    } finally {
      setUpdatingId(null);
    }
  };

  const handleLogout = () => {
    clearToken();
    router.replace("/login");
  };

  return (
    <div className={styles.page}>
      {/* Top bar */}
      <header className={styles.topBar}>
        <span className={styles.topBarTitle}>Mutfak Ekranı</span>

        <div className={styles.filterTabs}>
          {FILTERS.map((f) => (
            <button
              key={f.value}
              className={`${styles.filterTab} ${filter === f.value ? styles.filterActive : ""}`}
              onClick={() => setFilter(f.value)}
            >
              {f.label}
            </button>
          ))}
        </div>

        <Link href="/merchant/catalog" className={styles.logoutBtn}>
          Katalog
        </Link>

        <button className={styles.logoutBtn} onClick={handleLogout}>
          Çıkış
        </button>
      </header>

      {/* Main content */}
      <main className={styles.main}>
        {loading && orders.length === 0 ? (
          <p className={styles.message}>Yükleniyor...</p>
        ) : orders.length === 0 ? (
          <p className={styles.message}>Bu durumda bekleyen sipariş yok.</p>
        ) : (
          <div className={styles.grid}>
            {orders.map((order) => (
              <div
                key={order.id}
                className={`${styles.card} ${styles[`s_${order.status}`] ?? ""}`}
              >
                {/* Card header */}
                <div className={styles.cardHeader}>
                  <span className={styles.orderNum}>#{order.order_number}</span>
                  <span
                    className={`${styles.elapsed} ${elapsedClass(order.placed_at)}`}
                  >
                    {formatElapsed(order.placed_at, now)}
                  </span>
                </div>

                {/* Meta */}
                <div className={styles.meta}>
                  <span
                    className={`${styles.typeBadge} ${order.order_type === "dine_in" ? styles.typeDineIn : styles.typePickup}`}
                  >
                    {order.order_type === "dine_in" ? "Masada" : "Gel Al"}
                  </span>
                  {order.table_number && (
                    <span className={styles.tableNum}>
                      Masa {order.table_number}
                    </span>
                  )}
                  <span className={styles.placedTime}>
                    {formatTime(order.placed_at)}
                  </span>
                </div>

                {/* Items */}
                <ul className={styles.itemList}>
                  {order.items.map((item) => (
                    <li key={item.id} className={styles.item}>
                      <span className={styles.itemQty}>{item.quantity}×</span>
                      <span className={styles.itemBody}>
                        <span className={styles.itemName}>
                          {item.product_name_snapshot}
                        </span>
                        {item.modifiers.length > 0 && (
                          <span className={styles.itemMods}>
                            {item.modifiers
                              .map((m) => m.modifier_name_snapshot)
                              .join(", ")}
                          </span>
                        )}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* Customer note */}
                {order.customer_note && (
                  <p className={styles.note}>{order.customer_note}</p>
                )}

                {/* Footer: total + actions */}
                <div className={styles.cardFooter}>
                  <span className={styles.total}>
                    {order.total_amount.toFixed(2)} {order.currency}
                  </span>
                  <div className={styles.actions}>
                    {(STATUS_ACTIONS[order.status] ?? []).map((action) => (
                      <button
                        key={action.next}
                        className={`${styles.actionBtn} ${action.danger ? styles.actionDanger : styles.actionPrimary}`}
                        onClick={() =>
                          handleStatusUpdate(order.id, action.next)
                        }
                        disabled={updatingId === order.id}
                      >
                        {updatingId === order.id ? "..." : action.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
