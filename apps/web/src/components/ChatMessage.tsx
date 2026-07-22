import React from "react";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <div className="flex gap-3">
      {/* Skeleton for message bubble */}
      <div>{message.content}</div>
    </div>
  );
};
