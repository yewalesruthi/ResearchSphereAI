"use client";

import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { ChatMessage as ChatMessageType, SourceReference } from "@/types";

interface ChatMessageProps {
  message: ChatMessageType;
}

function formatCitation(source: SourceReference): string {
  const page = source.page != null ? ` — Page ${source.page}` : "";
  return `📄 ${source.document}${page}`;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-3",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}
      >
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.sources.map((source, i) => (
              <Badge
                key={`${source.chunk_id}-${i}`}
                variant="outline"
                className="cursor-default bg-background/80 font-normal"
              >
                {formatCitation(source)}
              </Badge>
            ))}
          </div>
        )}
        {message.intent && !isUser && (
          <span className="mt-2 inline-block rounded bg-background/50 px-2 py-0.5 text-xs opacity-70">
            {message.intent}
          </span>
        )}
      </div>
    </div>
  );
}
