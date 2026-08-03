"use client";

import { useCallback, useState } from "react";

import { readChatStream, StreamSource } from "@/lib/sse";

const CHAT_API_URL = "http://localhost:8000/api/v1/chat/";

type StreamChatOptions = {
  message: string;
  session_id?: string;
  accessToken: string | null;
  onToken: (token: string) => void;
  onSources: (sources: StreamSource[]) => void;
};

/** Stream a chat response while exposing request state to the calling component. */
export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const streamChat = useCallback(async ({
    message,
    session_id,
    accessToken,
    onToken,
    onSources,
  }: StreamChatOptions) => {
    setIsStreaming(true);
    setError(null);

    try {
      const headers: HeadersInit = { "Content-Type": "application/json" };
      if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

      const response = await fetch(CHAT_API_URL, {
        method: "POST",
        headers,
        body: JSON.stringify({ message, session_id }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed (${response.status}).`);
      }

      await readChatStream(response, (event) => {
        if (event.type === "sources") onSources(event.sources);
        if (event.type === "token") onToken(event.token);
      });
    } catch (streamError) {
      const message = streamError instanceof Error ? streamError.message : "Chat streaming failed.";
      setError(message);
      throw streamError;
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return { streamChat, isStreaming, error };
}
