import { useState } from 'react';
import { Button } from './ui/Button';
import { Send, Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';

export function ChatInput({ onSend, isLoading }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message... (Shift + Enter for new line)"
        disabled={isLoading}
        className={cn(
          'w-full min-h-[60px] max-h-[200px] p-4 pr-12 rounded-lg border border-input',
          'bg-background text-foreground resize-none',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          'disabled:cursor-not-allowed disabled:opacity-50',
          'scrollbar-thin'
        )}
        rows={1}
      />
      <Button
        type="submit"
        size="icon"
        disabled={!message.trim() || isLoading}
        className="absolute right-2 bottom-2"
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </Button>
    </form>
  );
}
