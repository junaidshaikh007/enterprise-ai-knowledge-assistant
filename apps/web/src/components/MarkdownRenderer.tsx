import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className="prose prose-sm max-w-none prose-invert break-words"
      components={{
        h1: ({ node, ...props }) => <h1 className="text-xl font-bold mt-4 mb-2" {...props} />,
        h2: ({ node, ...props }) => <h2 className="text-lg font-bold mt-4 mb-2" {...props} />,
        h3: ({ node, ...props }) => <h3 className="text-base font-bold mt-3 mb-2" {...props} />,
        p: ({ node, ...props }) => <p className="mb-2 leading-relaxed" {...props} />,
        ul: ({ node, ...props }) => <ul className="list-disc list-outside ml-4 mb-2" {...props} />,
        ol: ({ node, ...props }) => <ol className="list-decimal list-outside ml-4 mb-2" {...props} />,
        li: ({ node, ...props }) => <li className="mb-1" {...props} />,
        a: ({ node, ...props }) => <a className="text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer" {...props} />,
        code({ node, className, children, ...props }) {
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
                style={vscDarkPlus as any}
                language={match[1]}
                PreTag="div"
                customStyle={{ margin: 0, borderRadius: 0 }}
                {...props}
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
  );
};
