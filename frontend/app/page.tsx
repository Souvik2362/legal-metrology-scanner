"use client";

import { useState, useCallback } from "react";
import UploadScreen from "@/components/UploadScreen";
import ScanningScreen from "@/components/ScanningScreen";
import ResultsScreen from "@/components/ResultsScreen";
import { scanProductLabel, getMockScanResult } from "@/lib/mock-data";
import { AppScreen, ScanResult } from "@/lib/types";

export default function Home() {
  const [screen, setScreen] = useState<AppScreen>("upload");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [demoMode, setDemoMode] = useState<boolean>(false);

  const handleImageSelected = useCallback(async (url: string) => {
  setImageUrl(url);
  setErrorMessage(null);

  // Start the API request immediately.
  const scanPromise = scanProductLabel(url, demoMode);

  // Then show the scanning screen.
  setScreen("scanning");

  try {
    const scanResult = await scanPromise;
    setResult(scanResult);
    setScreen("results");
  } catch (err: any) {
    setErrorMessage(err.message || "Failed to complete product compliance scan.");
    setScreen("upload");
  }
}, [demoMode]);

  const handleReset = useCallback(() => {
    setScreen("upload");
    setImageUrl(null);
    setResult(null);
    setErrorMessage(null);
  }, []);

  const handleUseDemo = useCallback((sample: "cookme" | "sunridge" = "cookme") => {
    setErrorMessage(null);
    setDemoMode(true);
    setScreen("scanning");
    setTimeout(() => {
      const sampleResult = getMockScanResult("product_01.JPG", sample);
      setResult(sampleResult);
      setImageUrl("product_01.JPG");
      setScreen("results");
    }, 600);
  }, []);

  return (
    <main className="min-h-screen w-full">
      <header className="border-b border-rule bg-white/50 backdrop-blur-sm">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-sm font-semibold tracking-tight text-ink">
              METROLOGY&nbsp;SCAN
            </span>
            <span className="font-mono text-micro text-ink-faint">
              SIH26034
            </span>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setDemoMode((prev) => !prev)}
              className={`font-mono text-micro px-2.5 py-1 border transition-colors ${
                demoMode
                  ? "border-pending bg-pending-bg text-pending font-semibold"
                  : "border-rule text-ink-faint hover:text-ink hover:border-ink"
              }`}
              title="Toggle between live FastAPI backend and offline demo presentation mode"
            >
              {demoMode ? "MODE: OFFLINE DEMO" : "MODE: LIVE API"}
            </button>

            <div className="flex items-center gap-2 font-mono text-micro text-ink-faint">
              <span
                className={`inline-block h-1.5 w-1.5 ${
                  screen === "scanning"
                    ? "animate-blink bg-gauge"
                    : errorMessage
                    ? "bg-flagged"
                    : "bg-verified"
                }`}
              />
              {screen === "scanning"
                ? "PROCESSING"
                : errorMessage
                ? "ERROR"
                : "READY"}
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-3xl px-6 py-10">
        {errorMessage && (
          <div className="mb-6 border-l-2 border-flagged bg-flagged-bg/60 p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-mono text-micro text-flagged font-semibold">
                  SCAN FAILED
                </p>
                <p className="mt-1 text-sm text-ink-soft">{errorMessage}</p>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                className="font-mono text-micro text-ink-faint hover:text-ink"
              >
                DISMISS
              </button>
            </div>
            <div className="mt-3 flex gap-3">
              <button
                onClick={() => handleUseDemo("cookme")}
                className="border border-flagged bg-white px-3 py-1 font-mono text-micro text-flagged hover:bg-flagged-bg"
              >
                TRY WITH COOKME DEMO DATA
              </button>
            </div>
          </div>
        )}

        {screen === "upload" && (
          <UploadScreen
            onImageSelected={handleImageSelected}
            onLoadDemo={handleUseDemo}
          />
        )}
        {screen === "scanning" && imageUrl && (
          <ScanningScreen imageUrl={imageUrl} />
        )}
        {screen === "results" && result && (
          <ResultsScreen result={result} onReset={handleReset} />
        )}
      </div>
    </main>
  );
}
