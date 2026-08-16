import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="prose prose-sm max-w-none prose-invert break-words">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        code({ node, className, children, ...props }) {
          void node;
          const match = /language-(\w+)/.exec(className || '');
          // check if it's an inline code block by looking at className (usually inline code has no language-xxx class)
          // Also, react-markdown v9 might handle inline differently, but typically if there's no match it's inline.
          const isInline = !match;
          if (isInline) {
            return (
              <code className="bg-white/10 px-1 py-0.5 rounded text-sm font-mono" {...props}>
                {children}
              </code>
            );
          }
          return (
            <div className="rounded-md overflow-hidden my-3 border border-white/10">
              <div className="bg-zinc-800 text-zinc-400 text-xs px-3 py-1 flex items-center justify-between border-b border-white/5">
                <span>{match[1]}</span>
              </div>
              <SyntaxHighlighter
                language={match[1]}
                PreTag="div"
                customStyle={{ margin: 0, borderRadius: 0 }}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            </div>
          );
        },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
