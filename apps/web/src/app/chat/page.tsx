"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ChatSidebar, ChatSession } from "@/components/ChatSidebar";
import { ChatMessage, Message } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { useChatStream } from "@/hooks/useChatStream";
import { getOrFetchAuthToken } from "@/lib/auth";

type ChatSessionApi = {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string | null;
};

type ChatMessageApi = {
  id: string;
  role: string;
  content: string;
  created_at: string;
};

const WELCOME_SUGGESTIONS = [
  "Summarise the latest quarterly report",
  "What is our refund policy?",
  "Explain the onboarding checklist",
  "Compare Q2 vs Q3 revenue",
];

/* ─── Page Component ─── */
export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { streamChat, isStreaming: isLoading } = useChatStream();

  /* ─── Handlers ─── */
  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setInput("");
  };

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const token = await getOrFetchAuthToken();
        if (!token) return;
        const res = await fetch("http://localhost:8000/api/v1/sessions/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json() as ChatSessionApi[];
          setSessions(
            data.map((s) => ({
              id: s.id,
              title: s.title || "New Chat",
              lastMessage: "...",
              timestamp: new Date(s.updated_at || s.created_at).toLocaleString(),
            }))
          );
        }
      } catch (e) {
        console.error("Failed to load sessions", e);
      }
    };
    fetchSessions();
  }, []);

  const handleSelectSession = async (id: string) => {
    setActiveSessionId(id);
    setMessages([]);
    try {
      const token = await getOrFetchAuthToken();
      if (!token) return;
      const res = await fetch(`http://localhost:8000/api/v1/sessions/${id}/messages`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json() as ChatMessageApi[];
        setMessages(
          data.map((m) => ({
            id: m.id,
            role: m.role === "user" ? "user" : "assistant",
            content: m.content,
            timestamp: new Date(m.created_at),
          }))
        );
      }
    } catch (e) {
      console.error("Failed to load messages", e);
    }
  };

  const handleSend = async (text?: string) => {
    const query = text ?? input.trim();
    if (!query || isLoading) return;

    const token = await getOrFetchAuthToken();

    let targetSessionId = activeSessionId;
    if (!targetSessionId) {
      try {
        const res = await fetch("http://localhost:8000/api/v1/sessions/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ title: query.substring(0, 30) + (query.length > 30 ? "..." : "") })
        });
        if (res.ok) {
          const newSession = await res.json();
          targetSessionId = newSession.id;
          setActiveSessionId(newSession.id);
          setSessions((prev) => [
            {
              id: newSession.id,
              title: newSession.title,
              lastMessage: query,
              timestamp: new Date().toLocaleString(),
            },
            ...prev
          ]);
        }
      } catch (e) {
        console.error("Failed to create session", e);
      }
    } else {
        setSessions((prev) => prev.map(s => s.id === targetSessionId ? { ...s, lastMessage: query } : s));
    }

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };
    const assistantMessageId = crypto.randomUUID();
    const assistantMsg: Message = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput("");

    try {
      await streamChat({
        message: query,
        session_id: targetSessionId || undefined,
        accessToken: token,
        onToken: (streamedToken) => {
          setMessages((prev) => prev.map((message) => (
            message.id === assistantMessageId
              ? { ...message, content: message.content + streamedToken }
              : message
          )));
        },
        onSources: (sources) => {
          setMessages((prev) => prev.map((message) => (
            message.id === assistantMessageId
              ? {
                  ...message,
                  sources: sources.map((source, index) => ({
                    id: `source-${index}`,
                    documentName: source.file_name,
                    confidenceScore: source.score,
                  })),
                }
              : message
          )));
        },
      });
    } catch {
      const errMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "⚠️ Something went wrong. Please check the backend and try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => prev.map((message) => (
        message.id === assistantMessageId
          ? { ...message, content: errMsg.content }
          : message
      )));
    }
  };

  /* ─── Render ─── */
  return (
    <div className="flex h-screen bg-[#0f0f13] text-white overflow-hidden">
      {/* ─── Sidebar ─── */}
      <ChatSidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        sidebarOpen={sidebarOpen}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
      />

      {/* ─── Main Chat Area ─── */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-14 border-b border-white/5 flex items-center px-4 gap-3 flex-shrink-0 bg-[#0f0f13]/80 backdrop-blur-sm justify-between">
          <div className="flex items-center gap-3">
            <button
              id="toggle-sidebar-btn"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 rounded-lg hover:bg-white/5 transition-colors text-zinc-400 hover:text-white cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
            <h1 className="text-sm font-semibold text-zinc-200">
              {activeSessionId
                ? sessions.find((s) => s.id === activeSessionId)?.title
                : "Knowledge Assistant"}
            </h1>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <Link
              href="/dashboard"
              className="px-3 py-1.5 rounded-md bg-violet-600/30 hover:bg-violet-600/50 text-violet-200 border border-violet-500/30 transition-all font-medium flex items-center gap-1.5"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Upload Documents
            </Link>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            /* ─── Welcome / Empty State ─── */
            <div className="flex flex-col items-center justify-center h-full px-6">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center mb-6 shadow-lg shadow-violet-500/20">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                  <path
                    d="M16 4C9.373 4 4 9.373 4 16s5.373 12 12 12 12-5.373 12-12S22.627 4 16 4Zm0 6a2 2 0 1 1 0 4 2 2 0 0 1 0-4Zm3 10h-6v-1c0-.55.45-1 1-1h1v-3h-1c-.55 0-1-.45-1-1s.45-1 1-1h2c.55 0 1 .45 1 1v4h1c.55 0 1 .45 1 1v1Z"
                    fill="white"
                    fillOpacity="0.9"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Enterprise Knowledge Assistant
              </h2>
              <p className="text-zinc-400 text-sm text-center max-w-md mb-8">
                Ask questions about your organisation&apos;s documents. Answers are grounded
                in your uploaded knowledge base with source citations.
              </p>

              {/* Suggestion Chips */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                {WELCOME_SUGGESTIONS.map((suggestion, i) => (
                  <button
                    key={i}
                    id={`suggestion-${i}`}
                    onClick={() => handleSend(suggestion)}
                    className="text-left px-4 py-3 rounded-xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.06] hover:border-violet-500/30 text-sm text-zinc-300 hover:text-white transition-all duration-200 cursor-pointer"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* ─── Message Thread ─── */
            <div className="max-w-3xl mx-auto w-full px-4 py-6 space-y-6">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center flex-shrink-0 text-xs font-bold">
                    AI
                  </div>
                  <div className="bg-white/[0.06] border border-white/5 px-4 py-3 rounded-2xl rounded-bl-md">
                    <div className="flex gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-violet-400 animate-bounce [animation-delay:0ms]" />
                      <span className="w-2 h-2 rounded-full bg-violet-400 animate-bounce [animation-delay:150ms]" />
                      <span className="w-2 h-2 rounded-full bg-violet-400 animate-bounce [animation-delay:300ms]" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ─── Input Area ─── */}
        <ChatInput
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          onSend={handleSend}
        />
      </main>
    </div>
  );
}
