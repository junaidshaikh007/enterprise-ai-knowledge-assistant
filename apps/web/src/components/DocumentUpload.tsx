"use client";
import React, { useState, useRef } from "react";
import { useDocumentStatus } from "@/hooks/useDocumentStatus";

interface DocumentUploadProps {
  onUploadComplete?: () => void;
}

export function DocumentUpload({ onUploadComplete }: DocumentUploadProps = {}) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "processing" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [activeDocId, setActiveDocId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Hook for polling the active document status during background ingestion
  useDocumentStatus(activeDocId, {
    onSuccess: (doc) => {
      setStatus("success");
      setMessage(`"${doc.filename}" processed successfully! Created ${doc.num_chunks} chunks.`);
      setActiveDocId(null);
      if (onUploadComplete) onUploadComplete();
    },
    onError: (err) => {
      setStatus("error");
      setMessage(`Processing failed: ${err}`);
      setActiveDocId(null);
      if (onUploadComplete) onUploadComplete();
    },
  });

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus("uploading");
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("token"); // Assuming token is stored here
      const res = await fetch("http://localhost:8000/api/v1/documents/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Upload failed");
      }

      const data = await res.json();
      setStatus("processing");
      setMessage("Upload successful. Analyzing and indexing document...");
      setActiveDocId(data.document_id);
      if (onUploadComplete) onUploadComplete(); // Refresh list to show pending
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "An error occurred during upload.");
    }
  };

  return (
    <div className="w-full max-w-md p-6 bg-white rounded-lg shadow-md border border-gray-100">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Upload Document</h2>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          status === "uploading" || status === "processing"
            ? "border-blue-300 bg-blue-50/30 cursor-not-allowed"
            : isDragging
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-blue-400 cursor-pointer"
        }`}
        onDragOver={status === "uploading" || status === "processing" ? undefined : handleDragOver}
        onDragLeave={status === "uploading" || status === "processing" ? undefined : handleDragLeave}
        onDrop={status === "uploading" || status === "processing" ? undefined : handleDrop}
        onClick={() => {
          if (status !== "uploading" && status !== "processing") {
            fileInputRef.current?.click();
          }
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept=".pdf,.txt,.docx"
          disabled={status === "uploading" || status === "processing"}
        />
        
        {status === "uploading" || status === "processing" ? (
          <div className="flex flex-col items-center justify-center space-y-3 py-2">
            <svg className="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <div className="text-sm font-semibold text-blue-700">
              {status === "uploading" ? "Uploading file..." : "Ingesting & indexing..."}
            </div>
            <div className="text-xs text-blue-500 max-w-[200px] mx-auto truncate font-medium">
              {file?.name}
            </div>
          </div>
        ) : file ? (
          <div className="flex flex-col items-center justify-center py-2">
            <svg className="h-8 w-8 text-blue-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <div className="text-sm font-medium text-blue-600 truncate max-w-xs">{file.name}</div>
            <div className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB</div>
          </div>
        ) : (
          <div className="py-2">
            <svg className="h-8 w-8 text-gray-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
            </svg>
            <p className="text-sm font-medium text-gray-600 mb-1">Drag and drop your file here</p>
            <p className="text-xs text-gray-400">Supported formats: PDF, TXT, DOCX</p>
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between">
        <button
          onClick={() => {
            setFile(null);
            setStatus("idle");
            setMessage("");
          }}
          disabled={!file || status === "uploading" || status === "processing"}
          className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 transition-colors"
        >
          Clear
        </button>
        <button
          onClick={handleUpload}
          disabled={!file || status === "uploading" || status === "processing"}
          className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {status === "uploading" ? "Uploading..." : status === "processing" ? "Processing..." : "Upload"}
        </button>
      </div>

      {message && (
        <div className={`mt-4 p-3 text-sm rounded-md flex items-start gap-2 border ${
          status === "success"
            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
            : status === "error"
            ? "bg-rose-50 text-rose-700 border-rose-200"
            : "bg-blue-50 text-blue-700 border-blue-200"
        }`}>
          {(status === "uploading" || status === "processing") && (
            <svg className="animate-spin h-4 w-4 text-blue-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          )}
          {status === "success" && (
            <svg className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          )}
          {status === "error" && (
            <svg className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          )}
          <span className="leading-tight">{message}</span>
        </div>
      )}
    </div>
  );
}
