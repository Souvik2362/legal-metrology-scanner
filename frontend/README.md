# Metrology Scan — frontend

A Next.js (App Router + TypeScript + Tailwind) frontend for a Legal
Metrology label compliance scanner. Runs entirely on mock data — no
backend required to try it.

## Setup

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## What's inside

- `app/page.tsx` — the state machine driving Upload → Scanning →
  Results, all client-side, so the photo passes straight from screen
  to screen with no backend yet.
- `components/UploadScreen.tsx` — drag-and-drop or browse, live
  preview, numbered steps (01 Upload, 02 Analyze).
- `components/ScanningScreen.tsx` — cycles through status lines with
  a progress sweep.
- `components/ResultsScreen.tsx` — product readout plus compliance
  checks with three states (Detected / Needs verification / Not
  found — not a binary pass/fail); flagged items expand to show why.
- `lib/types.ts` / `lib/mock-data.ts` — the mock backend response,
  shaped so swapping in a real API is a one-line change.

## Connecting a real backend

`lib/mock-data.ts` exports `getMockScanResult(imageUrl)`. Replace its
body with a `fetch` to your API (see the comment at the top of the
file for an example against a FastAPI endpoint that accepts an image
upload and returns JSON shaped like `ScanResult` in `lib/types.ts`).
No other component needs to change as long as the response shape
matches.

## Design direction

"Legal Metrology" literally means weights and measures, so the UI
leans into a precision-instrument register rather than a generic
SaaS look: a ruled ledger background, hairline borders, tick-mark
dividers, and IBM Plex Mono for data readouts (MRP, quantities,
batch numbers) paired with IBM Plex Sans for interface text. Deep
ledger-blue for actions; green / amber / rust mark the three check
states. No rounded cards, no single compliant/non-compliant banner —
just a status summary plus the individual checks.

## Notes

This was built without network access, so it hasn't been run through
`npm install` / `npm run build` here — every file was reviewed by
hand for correctness. Run it locally and flag anything that breaks.
