"use client";

import React, { useState } from "react";
import { ChatSidebar, ChatSession } from "@/components/ChatSidebar";
import { ChatMessage, Message } from "@/components/ChatMessage";
const SEED_SESSIONS: ChatSession[] = [
  {
    id: "1",
    title: "Revenue Q3 Analysis",
    lastMessage: "The Q3 report indicates a 12% increase…",
    timestamp: "2 min ago",
  },
  {
    id: "2",
    title: "HR Policy Questions",
    lastMessage: "According to section 4.2 of the handbook…",
    timestamp: "1 hr ago",
  },
  {
    id: "3",
    title: "Product Roadmap 2026",
    lastMessage: "The roadmap prioritises AI-driven features…",
    timestamp: "Yesterday",
  },
];

const WELCOME_SUGGESTIONS = [
  "Summarise the latest quarterly report",
  "What is our refund policy?",
  "Explain the onboarding checklist",
  "Compare Q2 vs Q3 revenue",
];

/* ─── Page Component ─── */
export default function ChatPage() {
  const [sessions] = useState<ChatSession[]>(SEED_SESSIONS);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  /* ─── Handlers ─── */
  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setInput("");
  };

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
    // Future: load messages from DB
    setMessages([]);
  };

  const handleSend = async (text?: string) => {
    const query = text ?? input.trim();
    if (!query || isLoading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/api/v1/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: query }),
      });

      if (!res.ok) throw new Error("Chat request failed");
      const data = await res.json();

      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer ?? "Sorry, I could not generate a response.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "⚠️ Something went wrong. Please check the backend and try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
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
        <header className="h-14 border-b border-white/5 flex items-center px-4 gap-3 flex-shrink-0 bg-[#0f0f13]/80 backdrop-blur-sm">
          <button
            id="toggle-sidebar-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 rounded-lg hover:bg-white/5 transition-colors text-zinc-400 hover:text-white cursor-pointer"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
          <div className="flex-1 text-center">
            <h1 className="text-sm font-semibold text-zinc-200">
              {activeSessionId
                ? sessions.find((s) => s.id === activeSessionId)?.title
                : "Knowledge Assistant"}
            </h1>
          </div>
          {/* Placeholder for future controls */}
          <div className="w-8" />
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
        <div className="border-t border-white/5 bg-[#0f0f13]/90 backdrop-blur-sm p-4 flex-shrink-0">
          <div className="max-w-3xl mx-auto relative">
            <textarea
              id="chat-input"
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your documents…"
              className="w-full resize-none rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 pr-12 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20 transition-all duration-200"
            />
            <button
              id="send-btn"
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="absolute right-[6px] bottom-[6px] w-8 h-8 flex items-center justify-center rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-30 disabled:hover:bg-violet-600 text-white transition-all duration-200 cursor-pointer"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="-ml-[1px] mt-[1px]">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
          <p className="text-center text-[11px] text-zinc-600 mt-2">
            Responses are grounded in your uploaded knowledge base. Always verify critical information.
          </p>
        </div>
      </main>
    </div>
  );
}
