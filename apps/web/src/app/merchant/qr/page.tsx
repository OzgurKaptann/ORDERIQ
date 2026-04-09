"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { clearToken, AuthError } from "@/lib/auth";
import {
  fetchQRCodes,
  generateQRCode,
  type QRCode,
} from "@/lib/merchant-api";
import styles from "./qr.module.css";

export default function QRPage() {
  const router = useRouter();

  // List state
  const [qrCodes, setQrCodes] = useState<QRCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);

  // Generate form state
  const [codeType, setCodeType] = useState<"generic" | "table">("generic");
  const [tableNumber, setTableNumber] = useState("");
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);

  const handleAuthError = useCallback(() => {
    clearToken();
    router.replace("/login");
  }, [router]);

  const loadQRCodes = useCallback(async () => {
    try {
      const data = await fetchQRCodes();
      // Newest first
      data.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setQrCodes(data);
      setListError(null);
    } catch (err) {
      if (err instanceof AuthError) {
        handleAuthError();
        return;
      }
      setListError("QR kodlar yüklenemedi.");
    } finally {
      setLoading(false);
    }
  }, [handleAuthError]);

  useEffect(() => {
    void loadQRCodes();
  }, [loadQRCodes]);

  const canGenerate =
    !generating && (codeType === "generic" || tableNumber.trim() !== "");

  const handleGenerate = async () => {
    if (!canGenerate) return;
    setGenerating(true);
    setGenerateError(null);
    try {
      await generateQRCode({
        code_type: codeType,
        ...(codeType === "table" && { table_number: tableNumber.trim() }),
      });
      setTableNumber("");
      setLoading(true);
      await loadQRCodes();
    } catch (err) {
      if (err instanceof AuthError) {
        handleAuthError();
        return;
      }
      setGenerateError(
        err instanceof Error ? err.message : "QR kod oluşturulamadı."
      );
    } finally {
      setGenerating(false);
    }
  };

  const handleLogout = () => {
    clearToken();
    router.replace("/login");
  };

  return (
    <div className={styles.page}>
      <header className={styles.topBar}>
        <span className={styles.topBarTitle}>QR Kodlar</span>
        <Link href="/merchant/kitchen" className={styles.navLink}>
          ← Mutfak
        </Link>
        <Link href="/merchant/catalog" className={styles.navLink}>
          Katalog
        </Link>
        <button className={styles.navLink} onClick={handleLogout}>
          Çıkış
        </button>
      </header>

      <main className={styles.main}>
        {/* ── Generate section ───────────────────────── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Yeni QR Kod Oluştur</h2>
          <div className={styles.formPanel}>
            <div className={styles.typeRow}>
              <button
                className={`${styles.typeBtn} ${codeType === "generic" ? styles.typeSelected : ""}`}
                onClick={() => setCodeType("generic")}
              >
                Genel Mağaza QR
              </button>
              <button
                className={`${styles.typeBtn} ${codeType === "table" ? styles.typeSelected : ""}`}
                onClick={() => setCodeType("table")}
              >
                Masa QR
              </button>
            </div>

            {codeType === "table" && (
              <div className={styles.field}>
                <label className={styles.label}>
                  Masa Numarası <span className={styles.required}>*</span>
                </label>
                <input
                  className={styles.input}
                  type="text"
                  placeholder="Örn: 5"
                  value={tableNumber}
                  onChange={(e) => setTableNumber(e.target.value)}
                  maxLength={10}
                  autoComplete="off"
                />
              </div>
            )}

            {generateError && (
              <p className={styles.errorBanner}>{generateError}</p>
            )}

            <div>
              <button
                className={styles.generateBtn}
                onClick={handleGenerate}
                disabled={!canGenerate}
              >
                {generating ? "Oluşturuluyor..." : "Oluştur"}
              </button>
            </div>
          </div>
        </section>

        {/* ── Existing QR codes ──────────────────────── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>
            Mevcut QR Kodlar
            {!loading && qrCodes.length > 0 && (
              <span className={styles.count}>{qrCodes.length}</span>
            )}
          </h2>

          {listError && <p className={styles.errorBanner}>{listError}</p>}

          {loading ? (
            <p className={styles.message}>Yükleniyor...</p>
          ) : qrCodes.length === 0 ? (
            <p className={styles.message}>Henüz QR kod oluşturulmamış.</p>
          ) : (
            <div className={styles.qrList}>
              {qrCodes.map((qr) => (
                <div key={qr.id} className={styles.qrCard}>
                  <img
                    src={qr.image_url}
                    alt={
                      qr.code_type === "table"
                        ? `Masa ${qr.table_number} QR`
                        : "Genel QR"
                    }
                    className={styles.qrImage}
                  />
                  <div className={styles.qrInfo}>
                    <div className={styles.qrMeta}>
                      <span
                        className={`${styles.badge} ${
                          qr.code_type === "table"
                            ? styles.badgeTable
                            : styles.badgeGeneric
                        }`}
                      >
                        {qr.code_type === "table" ? "Masa" : "Genel"}
                      </span>
                      {qr.table_number && (
                        <span className={styles.tableName}>
                          Masa {qr.table_number}
                        </span>
                      )}
                    </div>
                    <p className={styles.targetUrl} title={qr.target_url}>
                      {qr.target_url}
                    </p>
                    <p className={styles.createdAt}>
                      {new Date(qr.created_at).toLocaleString("tr-TR")}
                    </p>
                    <a
                      href={qr.image_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      download
                      className={styles.downloadLink}
                    >
                      Aç / İndir
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
