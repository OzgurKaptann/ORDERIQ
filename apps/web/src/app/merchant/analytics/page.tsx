"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { clearToken, AuthError } from "@/lib/auth";
import {
  fetchAnalyticsSummary,
  fetchTopProducts,
  fetchHourlyOrders,
  type AnalyticsSummary,
  type TopProduct,
  type HourlyOrder,
} from "@/lib/merchant-api";
import styles from "./analytics.module.css";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmt(value: number): string {
  return value.toFixed(2);
}

function padHours(raw: HourlyOrder[]): HourlyOrder[] {
  const map = new Map(raw.map((h) => [h.hour, h.order_count]));
  return Array.from({ length: 24 }, (_, i) => ({
    hour: i,
    order_count: map.get(i) ?? 0,
  }));
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function AnalyticsPage() {
  const router = useRouter();

  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [hourlyOrders, setHourlyOrders] = useState<HourlyOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleAuthError = useCallback(() => {
    clearToken();
    router.replace("/login");
  }, [router]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, topData, hourlyData] = await Promise.all([
        fetchAnalyticsSummary(),
        fetchTopProducts(),
        fetchHourlyOrders(),
      ]);
      setSummary(summaryData);
      setTopProducts(topData);
      setHourlyOrders(padHours(hourlyData));
    } catch (err) {
      if (err instanceof AuthError) {
        handleAuthError();
        return;
      }
      setError(
        err instanceof Error ? err.message : "Veriler yüklenemedi."
      );
    } finally {
      setLoading(false);
    }
  }, [handleAuthError]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleLogout = () => {
    clearToken();
    router.replace("/login");
  };

  const maxHourlyCount = Math.max(
    1,
    ...hourlyOrders.map((h) => h.order_count)
  );

  return (
    <div className={styles.page}>
      <header className={styles.topBar}>
        <span className={styles.topBarTitle}>Analitik</span>
        <Link href="/merchant/kitchen" className={styles.navLink}>
          ← Mutfak
        </Link>
        <Link href="/merchant/catalog" className={styles.navLink}>
          Katalog
        </Link>
        <Link href="/merchant/qr" className={styles.navLink}>
          QR
        </Link>
        <button className={styles.navLink} onClick={handleLogout}>
          Çıkış
        </button>
      </header>

      <main className={styles.main}>
        {loading && (
          <p className={styles.message}>Yükleniyor...</p>
        )}

        {!loading && error && (
          <p className={styles.errorBanner}>{error}</p>
        )}

        {!loading && !error && summary && (
          <>
            {/* ── Summary cards ─────────────────────────── */}
            <section className={styles.section}>
              <h2 className={styles.sectionTitle}>Bugün</h2>
              <div className={styles.cardGrid}>
                <div className={styles.summaryCard}>
                  <span className={styles.cardLabel}>Sipariş Sayısı</span>
                  <span className={styles.cardValue}>
                    {summary.today_order_count}
                  </span>
                </div>
                <div className={styles.summaryCard}>
                  <span className={styles.cardLabel}>Ciro</span>
                  <span className={styles.cardValue}>
                    {fmt(summary.today_revenue)}
                  </span>
                </div>
                <div className={styles.summaryCard}>
                  <span className={styles.cardLabel}>Ort. Sepet</span>
                  <span className={styles.cardValue}>
                    {fmt(summary.average_basket_value)}
                  </span>
                </div>
              </div>
            </section>

            {/* ── Top products ───────────────────────────── */}
            <section className={styles.section}>
              <h2 className={styles.sectionTitle}>En Çok Satan Ürünler</h2>
              {topProducts.length === 0 ? (
                <p className={styles.empty}>Henüz veri yok.</p>
              ) : (
                <div className={styles.tableWrap}>
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th className={styles.th}>#</th>
                        <th className={styles.th}>Ürün</th>
                        <th className={`${styles.th} ${styles.thRight}`}>
                          Adet
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {topProducts.map((p, idx) => (
                        <tr key={p.product_name} className={styles.tr}>
                          <td className={`${styles.td} ${styles.tdRank}`}>
                            {idx + 1}
                          </td>
                          <td className={styles.td}>{p.product_name}</td>
                          <td className={`${styles.td} ${styles.tdRight}`}>
                            {p.total_quantity}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            {/* ── Hourly orders bar chart ────────────────── */}
            <section className={styles.section}>
              <h2 className={styles.sectionTitle}>Saatlik Sipariş Dağılımı</h2>
              {hourlyOrders.every((h) => h.order_count === 0) ? (
                <p className={styles.empty}>Bugün henüz sipariş yok.</p>
              ) : (
                <div className={styles.barChart}>
                  {hourlyOrders.map((h) => (
                    <div key={h.hour} className={styles.barRow}>
                      <span className={styles.barHour}>
                        {String(h.hour).padStart(2, "0")}:00
                      </span>
                      <div className={styles.barTrack}>
                        <div
                          className={styles.barFill}
                          style={{
                            width: `${((h.order_count / maxHourlyCount) * 100).toFixed(1)}%`,
                          }}
                        />
                      </div>
                      <span className={styles.barCount}>
                        {h.order_count > 0 ? h.order_count : ""}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
