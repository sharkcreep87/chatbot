import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Sidebar } from '@/components/Sidebar';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { Button } from '@/components/ui/Button';
import { chatAPI } from '@/services/api';
import toast from 'react-hot-toast';
import { Loader2, Bot } from 'lucide-react';

export function Chat() {
  const queryClient = useQueryClient();
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  // Fetch conversations
  const { data: conversations = [] } = useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      const response = await chatAPI.getConversations();
      return response.data;
    },
  });

  // Fetch messages for current conversation
  const { data: messages = [], isLoading: messagesLoading } = useQuery({
    queryKey: ['messages', currentConversationId],
    queryFn: async () => {
      if (!currentConversationId) return [];
      const response = await chatAPI.getMessages(currentConversationId);
      return response.data;
    },
    enabled: !!currentConversationId,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (message) =>
      chatAPI.sendMessage({
        message,
        conversation_id: currentConversationId,
        ai_provider: 'openai',
        model: 'gpt-4-turbo-preview',
      }),
    onSuccess: (data) => {
      setCurrentConversationId(data.data.conversation_id);
      queryClient.invalidateQueries(['messages', data.data.conversation_id]);
      queryClient.invalidateQueries(['conversations']);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to send message');
    },
  });

  // Delete conversation mutation
  const deleteConversationMutation = useMutation({
    mutationFn: (id) => chatAPI.deleteConversation(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['conversations']);
      if (currentConversationId === deleteConversationMutation.variables) {
        setCurrentConversationId(null);
      }
      toast.success('Conversation deleted');
    },
  });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewConversation = () => {
    setCurrentConversationId(null);
  };

  const handleSendMessage = (message) => {
    sendMessageMutation.mutate(message);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={setCurrentConversationId}
        onNewConversation={handleNewConversation}
        onDeleteConversation={deleteConversationMutation.mutate}
      />

      <main className="flex-1 flex flex-col">
        {/* Chat Header */}
        <header className="border-b p-4 bg-background">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">
              {currentConversationId
                ? conversations.find((c) => c.id === currentConversationId)?.title
                : 'New Conversation'}
            </h2>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-4">
          {messagesLoading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
              <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="h-8 w-8 text-primary" />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-semibold">
                  Welcome to ChatterMate Pro
                </h3>
                <p className="text-muted-foreground max-w-md">
                  Start a conversation with AI. Ask questions, get help, or just chat!
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    handleSendMessage('What can you help me with?')
                  }
                >
                  What can you help me with?
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    handleSendMessage('Explain quantum computing in simple terms')
                  }
                >
                  Explain quantum computing
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    handleSendMessage('Write a Python function to reverse a string')
                  }
                >
                  Write Python code
                </Button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {sendMessageMutation.isPending && (
                <div className="flex gap-4 p-4">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-secondary">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-muted-foreground">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t p-4 bg-background">
          <div className="max-w-4xl mx-auto">
            <ChatInput
              onSend={handleSendMessage}
              isLoading={sendMessageMutation.isPending}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
