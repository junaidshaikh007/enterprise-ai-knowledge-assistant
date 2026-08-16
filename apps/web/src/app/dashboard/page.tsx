"use client";

import React, { useState } from "react";
import { DocumentUpload } from "@/components/DocumentUpload";
import { DocumentList } from "@/components/DocumentList";

export default function DashboardPage() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadComplete = () => {
    // Trigger a refresh of the DocumentList when upload begins or status updates
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="flex flex-col flex-1 p-8 bg-zinc-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Knowledge Base</h2>
          <p className="text-sm text-gray-500 mb-6">
            Upload documents (PDF, TXT, DOCX) to expand the AI&apos;s knowledge base.
            These documents will be parsed and embedded for RAG retrieval in real-time.
          </p>
          <DocumentUpload onUploadComplete={handleUploadComplete} />
        </div>
        
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-700">Recent Documents</h2>
            <button
              onClick={handleUploadComplete}
              className="p-1.5 text-zinc-500 hover:text-blue-600 rounded-md hover:bg-zinc-150 transition-colors"
              title="Refresh document list"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
            </button>
          </div>
          <DocumentList refreshTrigger={refreshTrigger} />
        </div>
      </div>
    </div>
  );
}
