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
        className={`flex w-full items-center gap-4 py-3 text-left ${
          expandable ? "cursor-pointer" : "cursor-default"
        }`}
        aria-expanded={expandable ? open : undefined}
      >
        <span className={`inline-block h-1.5 w-1.5 shrink-0 ${meta.dotClass}`} />
        <span className="w-40 shrink-0 text-sm text-ink">{check.label}</span>
        <span className="flex-1 truncate font-mono text-sm text-ink-soft">
          {check.reading ?? "—"}
        </span>
        <span
          className={`shrink-0 px-2 py-0.5 font-mono text-micro ${meta.textClass} ${meta.bgClass}`}
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
          <p className="text-sm text-ink-soft">{check.reason}</p>

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
          <div className="mb-1 flex items-center gap-2 font-mono text-micro text-ink-faint">
            <span>{result.scanId}</span>
            <span>·</span>
            <span>{new Date(result.scannedAt).toLocaleString()}</span>
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

      <section className="mb-10 border border-rule bg-white/40 p-5">
        <h2 className="mb-4 text-sm font-medium text-ink">
          Printed declarations
        </h2>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-3 font-mono text-sm tabular sm:grid-cols-3">
          <div>
            <dt className="text-micro text-ink-faint">NET QUANTITY</dt>
            <dd className="text-ink">{result.product.netQuantity}</dd>
          </div>
          <div>
            <dt className="text-micro text-ink-faint">MRP</dt>
            <dd className="text-ink">{result.product.mrp}</dd>
          </div>
          <div>
            <dt className="text-micro text-ink-faint">BATCH NO.</dt>
            <dd className="text-ink">{result.product.batchNumber}</dd>
          </div>
          <div>
            <dt className="text-micro text-ink-faint">MFG DATE</dt>
            <dd className="text-ink">{result.product.mfgDate}</dd>
          </div>
          <div className="col-span-2 sm:col-span-3">
            <dt className="text-micro text-ink-faint">PACKER ADDRESS</dt>
            <dd className="text-ink">{result.product.packerAddress}</dd>
          </div>
        </dl>
      </section>

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
