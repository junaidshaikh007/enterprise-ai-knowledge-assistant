import React from "react";

export interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  sidebarOpen: boolean;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
}

export function ChatSidebar({
  sessions,
  activeSessionId,
  sidebarOpen,
  onSelectSession,
  onNewChat,
}: ChatSidebarProps) {
  return (
    <aside
      className={`${
        sidebarOpen ? "w-72" : "w-0"
      } transition-all duration-300 ease-in-out flex-shrink-0 overflow-hidden border-r border-white/5 bg-[#13131a] flex flex-col`}
    >
      {/* Sidebar Header */}
      <div className="p-4 border-b border-white/5 flex-shrink-0">
        <button
          id="new-chat-btn"
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-sm font-medium transition-all duration-200 shadow-lg shadow-violet-500/20 hover:shadow-violet-500/30 cursor-pointer"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3v10M3 8h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500 px-2 mb-2">
          Recent
        </p>
        {sessions.map((s) => (
          <button
            key={s.id}
            id={`session-${s.id}`}
            onClick={() => onSelectSession(s.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg transition-all duration-150 group cursor-pointer ${
              activeSessionId === s.id
                ? "bg-white/10 text-white"
                : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
            }`}
          >
            <p className="text-sm font-medium truncate">{s.title}</p>
            <p className="text-xs text-zinc-500 truncate mt-0.5 group-hover:text-zinc-400 transition-colors">
              {s.lastMessage}
            </p>
          </button>
        ))}
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-white/5 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center text-xs font-bold">
            U
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">User</p>
            <p className="text-xs text-zinc-500 truncate">Enterprise Plan</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
