"use client";

import { AppLayout } from "@/components/layout/AppLayout";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { useChat } from "@/hooks/useChat";
import { useWorkspaceStore } from "@/store/workspaceStore";

export default function ChatPage() {
  const currentWorkspace = useWorkspaceStore((s) => s.currentWorkspace);
  const { messages, isStreaming, sendMessage } = useChat(currentWorkspace?.id);

  if (!currentWorkspace) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center p-8">
          <p className="text-muted-foreground">Select or create a workspace first.</p>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex h-screen flex-col">
        <div className="border-b p-4">
          <h1 className="text-xl font-bold">Research Chat</h1>
          <p className="text-sm text-muted-foreground">Ask questions about your uploaded documents</p>
        </div>
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 space-y-4 overflow-y-auto p-6">
            {messages.length === 0 && (
              <div className="flex h-full items-center justify-center text-muted-foreground">
                <p>Start a conversation about your research documents</p>
              </div>
            )}
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} />
            ))}
          </div>
          <ChatInput onSend={sendMessage} disabled={isStreaming} />
        </div>
      </div>
    </AppLayout>
  );
}
