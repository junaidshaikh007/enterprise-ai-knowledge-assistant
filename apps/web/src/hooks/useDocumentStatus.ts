"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { DocumentStatusResponse } from "@/types/document";

interface UseDocumentStatusOptions {
  intervalMs?: number;
  onSuccess?: (doc: DocumentStatusResponse) => void;
  onError?: (error: string) => void;
}

export function useDocumentStatus(
  documentId: string | null,
  options: UseDocumentStatusOptions = {}
) {
  const { intervalMs = 2000, onSuccess, onError } = options;

  const [statusInfo, setStatusInfo] = useState<DocumentStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState<boolean>(false);

  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!documentId) return;

    try {
      setLoading(true);
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
      const res = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/status`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to fetch document status");
      }

      const data: DocumentStatusResponse = await res.json();
      setStatusInfo(data);
      setError(null);

      if (data.status === "SUCCESS" || data.status === "FAILED") {
        setIsPolling(false);
        if (data.status === "SUCCESS" && onSuccess) {
          onSuccess(data);
        } else if (data.status === "FAILED" && onError) {
          onError(data.error_message || "Document processing failed");
        }
      }

      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "An error occurred while fetching status";
      setError(msg);
      setIsPolling(false);
      if (onError) onError(msg);
    } finally {
      setLoading(false);
    }
  }, [documentId, onSuccess, onError]);

  useEffect(() => {
    if (!documentId) {
      queueMicrotask(() => {
        setStatusInfo(null);
        setIsPolling(false);
      });
      return;
    }

    queueMicrotask(() => {
      setIsPolling(true);
      void fetchStatus();
    });

    timerRef.current = setInterval(() => {
      fetchStatus();
    }, intervalMs);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [documentId, intervalMs, fetchStatus]);

  const stopPolling = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setIsPolling(false);
  }, []);

  return {
    statusInfo,
    loading,
    error,
    isPolling,
    stopPolling,
    refetch: fetchStatus,
  };
}
