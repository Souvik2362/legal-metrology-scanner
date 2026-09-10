"use client";

import { useEffect, useState } from "react";

interface ScanningScreenProps {
  imageUrl: string;
}

const STATUS_LINES = [
  "Reading packaging geometry",
  "Extracting printed declarations",
  "Cross-checking against LM(PC) Rules 2011",
];

export default function ScanningScreen({ imageUrl }: ScanningScreenProps) {
  const [activeLine, setActiveLine] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveLine((prev) => Math.min(prev + 1, STATUS_LINES.length - 1));
    }, 850);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <div className="mb-8 border-b border-rule pb-6">
        <h1 className="text-xl font-medium text-ink">Analyzing label</h1>
        <p className="mt-1 text-sm text-ink-soft">
          Reconciling printed declarations against Legal Metrology
          requirements.
        </p>
      </div>

      <div className="grid grid-cols-[minmax(0,220px)_1fr] gap-8">
        <div className="border border-rule bg-white/40 p-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={imageUrl}
            alt="Label being scanned"
            className="w-full object-contain opacity-80"
          />
        </div>

        <div>
          <div className="relative mb-8 h-px w-full overflow-hidden bg-paper-line">
            <div className="absolute inset-y-0 left-0 w-1/4 animate-sweep bg-gauge" />
          </div>

          <ul className="space-y-4 font-mono text-sm">
            {STATUS_LINES.map((line, i) => {
              const state =
                i < activeLine ? "done" : i === activeLine ? "active" : "pending";
              return (
                <li key={line} className="flex items-center gap-3">
                  <span
                    className={`inline-block h-1.5 w-1.5 shrink-0 ${
                      state === "done"
                        ? "bg-verified"
                        : state === "active"
                        ? "animate-blink bg-gauge"
                        : "bg-paper-line"
                    }`}
                  />
                  <span
                    className={
                      state === "pending" ? "text-ink-faint" : "text-ink"
                    }
                  >
                    {line}
                  </span>
                  {state === "done" && (
                    <span className="text-micro text-verified">OK</span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
}
