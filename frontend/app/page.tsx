"use client";

import { useState, useCallback } from "react";
import UploadScreen from "@/components/UploadScreen";
import ScanningScreen from "@/components/ScanningScreen";
import ResultsScreen from "@/components/ResultsScreen";
import { getMockScanResult } from "@/lib/mock-data";
import { AppScreen, ScanResult } from "@/lib/types";

export default function Home() {
  const [screen, setScreen] = useState<AppScreen>("upload");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  const handleImageSelected = useCallback(async (url: string) => {
    setImageUrl(url);
    setScreen("scanning");
    const scanResult = await getMockScanResult(url);
    setResult(scanResult);
    setScreen("results");
  }, []);

  const handleReset = useCallback(() => {
    setScreen("upload");
    setImageUrl(null);
    setResult(null);
  }, []);

  return (
    <main className="min-h-screen w-full">
      <header className="border-b border-rule">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-sm font-semibold tracking-tight text-ink">
              METROLOGY&nbsp;SCAN
            </span>
            <span className="font-mono text-micro text-ink-faint">
              rev. 1.0
            </span>
          </div>
          <div className="flex items-center gap-2 font-mono text-micro text-ink-faint">
            <span
              className={`inline-block h-1.5 w-1.5 ${
                screen === "scanning" ? "animate-blink bg-gauge" : "bg-verified"
              }`}
            />
            {screen === "scanning" ? "PROCESSING" : "READY"}
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-3xl px-6 py-10">
        {screen === "upload" && (
          <UploadScreen onImageSelected={handleImageSelected} />
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
