"use client";

import { useCallback, useRef, useState } from "react";

interface UploadScreenProps {
  onImageSelected: (url: string) => void;
}

export default function UploadScreen({ onImageSelected }: UploadScreenProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const loadFile = useCallback((file: File | undefined) => {
    if (!file || !file.type.startsWith("image/")) return;
    const url = URL.createObjectURL(file);
    setPreview(url);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      loadFile(e.dataTransfer.files?.[0]);
    },
    [loadFile]
  );

  return (
    <div>
      <div className="mb-8 flex items-start justify-between border-b border-rule pb-6">
        <div>
          <h1 className="text-xl font-medium text-ink">Scan a product label</h1>
          <p className="mt-1 max-w-md text-sm text-ink-soft">
            Upload a clear photo of the packaging face carrying the MRP, net
            quantity, and manufacturer declarations. One label per scan.
          </p>
        </div>
      </div>

      <ol className="mb-6 flex gap-6 font-mono text-micro text-ink-faint">
        <li className={preview ? "text-ink-faint" : "text-gauge"}>
          01 UPLOAD
        </li>
        <li>02 ANALYZE</li>
      </ol>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative flex min-h-[320px] cursor-pointer flex-col items-center justify-center border ${
          isDragging ? "border-gauge bg-white/60" : "border-rule bg-white/40"
        } transition-colors`}
      >
        <div className="pointer-events-none absolute left-0 top-0 h-3 w-3 border-l border-t border-ink-faint" />
        <div className="pointer-events-none absolute right-0 top-0 h-3 w-3 border-r border-t border-ink-faint" />
        <div className="pointer-events-none absolute bottom-0 left-0 h-3 w-3 border-b border-l border-ink-faint" />
        <div className="pointer-events-none absolute bottom-0 right-0 h-3 w-3 border-b border-r border-ink-faint" />

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => loadFile(e.target.files?.[0])}
        />

        {preview ? (
          <div className="flex w-full max-w-sm flex-col items-center gap-4 px-6 py-6">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={preview}
              alt="Selected label preview"
              className="max-h-56 w-auto border border-rule object-contain"
            />
            <p className="font-mono text-micro text-ink-faint">
              PREVIEW LOADED — TAP TO REPLACE
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 px-6 text-center">
            <div className="flex h-12 w-12 items-center justify-center border border-ink-faint">
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M10 3v10M10 3l-4 4M10 3l4 4"
                  stroke="#4A5459"
                  strokeWidth="1.4"
                  strokeLinecap="square"
                />
                <path
                  d="M3 15v1.5A1.5 1.5 0 0 0 4.5 18h11a1.5 1.5 0 0 0 1.5-1.5V15"
                  stroke="#4A5459"
                  strokeWidth="1.4"
                />
              </svg>
            </div>
            <p className="text-sm text-ink">
              Drag a photo here, or click to browse
            </p>
            <p className="font-mono text-micro text-ink-faint">
              JPG / PNG — LEGIBLE, EVENLY LIT
            </p>
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <p className="font-mono text-micro text-ink-faint">
          NO IMAGE LEAVES THIS DEVICE UNTIL YOU CONTINUE
        </p>
        <button
          disabled={!preview}
          onClick={() => preview && onImageSelected(preview)}
          className="border border-ink bg-gauge px-5 py-2.5 text-sm font-medium text-paper transition-opacity disabled:cursor-not-allowed disabled:border-rule disabled:bg-rule disabled:text-ink-faint disabled:opacity-100"
        >
          Run compliance scan
        </button>
      </div>
    </div>
  );
}
