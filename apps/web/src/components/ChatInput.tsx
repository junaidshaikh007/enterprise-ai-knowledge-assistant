import React from "react";

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  onSend: (text?: string) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  input,
  setInput,
  isLoading,
  onSend,
}) => {
  return (
    <div className="border-t border-white/5 bg-[#0f0f13]/90 backdrop-blur-sm p-4 flex-shrink-0">
      <div className="max-w-3xl mx-auto relative">
        {/* Input container skeleton */}
      </div>
    </div>
  );
};
