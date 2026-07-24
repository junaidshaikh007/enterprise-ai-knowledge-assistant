import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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
      }}
    >
      {content}
    </ReactMarkdown>
  );
};
