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
