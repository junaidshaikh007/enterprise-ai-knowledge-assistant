export type StreamSource = {
  file_name: string;
  score: number;
  text: string;
};

export type ChatStreamEvent =
  | { type: "sources"; sources: StreamSource[] }
  | { type: "token"; token: string }
  | { type: "done" };

type SSEPayload = {
  sources?: StreamSource[];
  token?: string;
  done?: boolean;
};

/** Convert one complete SSE message into the chat event used by the UI. */
export function parseChatStreamEvent(message: string): ChatStreamEvent | null {
  const lines = message.split("\n");
  const event = lines.find((line) => line.startsWith("event: "))?.slice(7);
  const data = lines.find((line) => line.startsWith("data: "))?.slice(6);

  if (!event || !data) return null;

  const payload = JSON.parse(data) as SSEPayload;

  if (event === "sources" && Array.isArray(payload.sources)) {
    return { type: "sources", sources: payload.sources };
  }
  if (event === "token" && typeof payload.token === "string") {
    return { type: "token", token: payload.token };
  }
  if (event === "done" && payload.done === true) {
    return { type: "done" };
  }

  return null;
}

/** Read a fetch response incrementally and emit each complete SSE chat event. */
export async function readChatStream(
  response: Response,
  onEvent: (event: ChatStreamEvent) => void,
): Promise<void> {
  if (!response.body) {
    throw new Error("The chat response did not include a readable stream.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      let separatorIndex = buffer.indexOf("\n\n");

      while (separatorIndex !== -1) {
        const message = buffer.slice(0, separatorIndex);
        buffer = buffer.slice(separatorIndex + 2);

        const event = parseChatStreamEvent(message);
        if (event) onEvent(event);

        separatorIndex = buffer.indexOf("\n\n");
      }
    }
  } finally {
    reader.releaseLock();
  }
}
