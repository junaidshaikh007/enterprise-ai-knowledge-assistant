import React from "react";
import { SourceReference } from "./ChatMessage";

interface SourceCitationProps {
  source: SourceReference;
}

export const SourceCitation: React.FC<SourceCitationProps> = ({ source }) => {
  // Format score as percentage
  const scorePercent = Math.round(source.confidenceScore * 100);

  return (
    <div className="flex items-center justify-between gap-3 p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-xs text-zinc-300">
      <div className="flex items-center gap-2 overflow-hidden">
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
          className="flex-shrink-0 text-violet-400"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
        <span className="truncate font-medium">{source.documentName}</span>
      </div>
      <div className="flex items-center gap-1 flex-shrink-0">
        <span className="px-1.5 py-0.5 rounded-full font-semibold bg-violet-500/20 text-violet-300">
          {scorePercent}%
        </span>
      </div>
    </div>
  );
};
