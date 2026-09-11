"use client";

import { useState } from "react";
import { CheckStatus, ScanResult } from "@/lib/types";

interface ResultsScreenProps {
  result: ScanResult;
  onReset: () => void;
}

const STATUS_META: Record<
  CheckStatus,
  { label: string; textClass: string; bgClass: string; dotClass: string }
> = {
  detected: {
    label: "DETECTED",
    textClass: "text-verified",
    bgClass: "bg-verified-bg",
    dotClass: "bg-verified",
  },
  potential_issue: {
    label: "POTENTIAL ISSUE",
    textClass: "text-flagged",
    bgClass: "bg-flagged-bg",
    dotClass: "bg-flagged",
  },
  manual_verification: {
    label: "MANUAL VERIFICATION",
    textClass: "text-pending",
    bgClass: "bg-pending-bg",
    dotClass: "bg-pending",
  },
};

function CheckRow({ check }: { check: ScanResult["checks"][number] }) {
  const [open, setOpen] = useState(false);
  const meta = STATUS_META[check.status];
  const expandable = true;

  return (
    <div className="border-b border-rule last:border-b-0">
      <button
        onClick={() => expandable && setOpen((o) => !o)}
        className={`flex w-full items-center gap-2 py-3 text-left sm:gap-4 ${
          expandable ? "cursor-pointer" : "cursor-default"
        }`}
        aria-expanded={expandable ? open : undefined}
      >
        <span className={`inline-block h-1.5 w-1.5 shrink-0 ${meta.dotClass}`} />
        <div className="w-32 shrink-0 sm:w-40">
          <span className="block text-sm text-ink">{check.label}</span>
          <span className="mt-0.5 block font-mono text-micro text-ink-faint">
            {check.ruleRef}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <span className="block truncate font-mono text-sm text-ink-soft">
            {check.reading ?? "—"}
          </span>

          {check.status !== "detected" && (
            <span className="mt-1 block font-mono text-micro text-ink-faint">
              REVIEW REQUIRED
            </span>
          )}
        </div>
        <span
          className={`shrink-0 px-1.5 py-0.5 font-mono text-micro sm:px-2 ${meta.textClass} ${meta.bgClass}`}
        >
          {meta.label}
        </span>
        <span
          className={`shrink-0 font-mono text-ink-faint transition-transform ${
            open ? "rotate-90" : ""
          }`}
        >
          ›
        </span>
      </button>

      {expandable && open && (
        <div className="mb-4 ml-[22px] border-l border-rule pl-4 pb-1">
          <p className="text-sm leading-6 text-ink-soft">
            {check.reason ??
              (check.status === "detected"
                ? "Declaration detected on the scanned label. Review the applicable rule reference and verify correctness, placement, and legibility where required."
                : check.status === "manual_verification"
                ? "Declaration requires manual verification against the package and applicable rule requirements."
                : "Potential non-compliance detected. Review the declaration and applicable rule requirements.")}
          </p>

          <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 font-mono text-micro text-ink-faint">
            <span>READING · {check.reading ?? "—"}</span>
            <span>REF · {check.ruleRef}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ResultsScreen({ result, onReset }: ResultsScreenProps) {
  const counts = result.checks.reduce(
    (acc, c) => {
      acc[c.status] += 1;
      return acc;
    },
    { detected: 0, potential_issue: 0, manual_verification: 0 } as Record<
      CheckStatus,
      number
    >
  );

  return (
    <div>
      <div className="mb-6 flex items-start justify-between border-b border-rule pb-6">
        <div>
          <div className="mb-1 flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-micro text-ink-faint">
            <span>SCAN · {result.scanId}</span>
            <span>·</span>
            <span>
              ASSESSED · {new Date(result.scannedAt).toLocaleString()}
            </span>
          </div>
          <h1 className="text-xl font-medium text-ink">
            {result.product.brand} — {result.product.name}
          </h1>
        </div>
        <button
          onClick={onReset}
          className="shrink-0 border border-rule px-4 py-2 font-mono text-micro text-ink-soft hover:border-ink"
        >
          NEW SCAN
        </button>
      </div>

      <div className="mb-5 flex items-center justify-between border-b border-rule pb-3">
        <span className="font-mono text-micro text-ink-faint">
          ASSESSMENT STATUS
        </span>

        <span className="font-mono text-micro text-verified">
          ✓ COMPLETE · {result.checks.length} CHECKS
        </span>
      </div>

      <section className="mb-6 grid gap-6 border border-rule bg-white/40 p-5 sm:grid-cols-[220px_1fr]">
        <div className="border border-rule bg-paper p-2">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={result.imageUrl}
            alt="Scanned product label"
            className="h-full max-h-64 w-full object-contain"
          />
        </div>

        <div className="flex flex-col justify-center">
          <p className="font-mono text-micro text-ink-faint">
            SCANNED LABEL
          </p>

          <h2 className="mt-2 text-base font-medium text-ink">
            Visual reference
          </h2>

          <p className="mt-2 max-w-md text-sm leading-6 text-ink-soft">
            Results below are based on statutory declarations detected from the
            scanned product face across 9 Legal Metrology rules.
          </p>

          <div className="mt-3 flex flex-wrap gap-2 font-mono text-micro">
            <span className="border border-rule bg-white px-2 py-0.5 text-ink">
              QTY: {result.product.netQuantity}
            </span>
            <span className="border border-rule bg-white px-2 py-0.5 text-ink">
              MRP: {result.product.mrp}
            </span>
            <span className="border border-rule bg-white px-2 py-0.5 text-ink">
              BATCH: {result.product.batchNumber}
            </span>
            <span className="border border-rule bg-white px-2 py-0.5 text-ink">
              MFD: {result.product.mfgDate}
            </span>
            {result.product.unitSalePrice && (
              <span className="border border-rule bg-white px-2 py-0.5 text-gauge">
                USP: {result.product.unitSalePrice}
              </span>
            )}
            {result.product.countryOfOrigin && (
              <span className="border border-rule bg-white px-2 py-0.5 text-verified">
                ORIGIN: {result.product.countryOfOrigin}
              </span>
            )}
          </div>
        </div>
      </section>

      <div className="mb-4 border-l-2 border-gauge bg-white/40 px-4 py-3">
        <p className="font-mono text-micro text-gauge">
          ASSESSMENT SUMMARY
        </p>

       <p className="mt-1 text-sm leading-6 text-ink-soft">
          {counts.potential_issue > 0
            ? `${counts.potential_issue} potential issue${
                counts.potential_issue > 1 ? "s" : ""
              } detected. Review flagged declarations before making a compliance decision.`
            : counts.manual_verification > 0
            ? `${counts.manual_verification} item${
                counts.manual_verification > 1 ? "s" : ""
              } require manual verification.`
            : "All scanned declarations were detected without a potential issue."}
        </p>
      </div>

      <div className="mb-6 grid grid-cols-3 border-y border-rule">
        <div className="border-r border-rule px-4 py-4">
          <p className="font-mono text-micro text-ink-faint">DETECTED</p>
          <p className="mt-1 text-2xl text-verified">
            {counts.detected}
          </p>
        </div>

        <div className="border-r border-rule px-4 py-4">
          <p className="font-mono text-micro text-ink-faint">
            POTENTIAL ISSUE
          </p>
          <p className="mt-1 text-2xl text-flagged">
            {counts.potential_issue}
          </p>
        </div>

        <div className="px-4 py-4">
          <p className="font-mono text-micro text-ink-faint">
            TO VERIFY
          </p>
          <p className="mt-1 text-2xl text-pending">
            {counts.manual_verification}
          </p>
        </div>
      </div>
      

      <section>
        <h2 className="mb-2 text-sm font-medium text-ink">
          Compliance checks
        </h2>
        <div className="tick-row mb-1" />
        <div className="border border-rule bg-white/40 px-4">
          {result.checks.map((check) => (
            <CheckRow key={check.id} check={check} />
          ))}
        </div>
        <div className="mt-4 border-l-2 border-pending bg-pending-bg/30 px-4 py-3">
          <p className="font-mono text-micro text-pending">
            PRELIMINARY COMPLIANCE ASSESSMENT
          </p>

          <p className="mt-1 text-xs leading-5 text-ink-soft">
            This scan is a decision-support tool, not a legal certification.
            DETECTED means the declaration was found on the scanned face.
            POTENTIAL ISSUE and MANUAL VERIFICATION items require human review
            and may require checking other areas of the package.
          </p>
        </div>
        <div className="mt-8 flex justify-end border-t border-rule pt-5">
          <button
            onClick={onReset}
            className="border border-ink bg-gauge px-5 py-2.5 text-sm font-medium text-paper hover:opacity-90"
          >
            SCAN ANOTHER PRODUCT
          </button>
        </div>
      </section>
    </div>
  );
}
