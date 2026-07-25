"use client";

import React, { useState } from "react";
import { SourceReference } from "./ChatMessage";
import { SourceCitation } from "./SourceCitation";

interface SourceReferencesPanelProps {
  sources: SourceReference[];
}

export const SourceReferencesPanel: React.FC<SourceReferencesPanelProps> = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 text-sm">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-300 transition-colors focus:outline-none"
        aria-expanded={isOpen}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`transition-transform duration-200 ${isOpen ? "rotate-90" : ""}`}
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span className="font-medium text-xs">
          {sources.length} {sources.length === 1 ? "Source" : "Sources"}
        </span>
      </button>

      {isOpen && (
        <div className="mt-2 flex flex-col gap-1.5 pl-4 border-l-2 border-violet-500/30">
          {sources.map((source) => (
            <SourceCitation key={source.id} source={source} />
          ))}
        </div>
      )}
    </div>
  );
};
