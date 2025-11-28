import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from './ui/Button';
import { Card } from './ui/Card';
import {
  MessageSquarePlus,
  Trash2,
  Settings,
  Moon,
  Sun,
  LogOut,
  Menu,
  X,
  BarChart3,
  Database,
  Crown,
  CreditCard,
} from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/utils/cn';
import { format } from 'date-fns';

export function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed top-4 left-4 z-50 md:hidden"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed md:sticky top-0 left-0 z-40 h-screen w-64 border-r bg-background',
          'flex flex-col transition-transform md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h1 className="text-xl font-bold">ChatterMate Pro</h1>
        </div>

        {/* Navigation */}
        <div className="p-4 space-y-2">
          <Button
            onClick={() => navigate('/chat')}
            variant={location.pathname === '/chat' ? 'default' : 'ghost'}
            className="w-full justify-start gap-2"
          >
            <MessageSquarePlus className="h-4 w-4" />
            Chat
          </Button>
          <Button
            onClick={() => navigate('/knowledge-base')}
            variant={location.pathname === '/knowledge-base' ? 'default' : 'ghost'}
            className="w-full justify-start gap-2"
          >
            <Database className="h-4 w-4" />
            Knowledge Base
          </Button>
          <Button
            onClick={() => navigate('/analytics')}
            variant={location.pathname === '/analytics' ? 'default' : 'ghost'}
            className="w-full justify-start gap-2"
          >
            <BarChart3 className="h-4 w-4" />
            Analytics
          </Button>
        </div>

        {/* Subscription Section */}
        <div className="px-4 pb-2 border-t pt-2">
          <p className="text-xs text-muted-foreground mb-2 font-semibold">SUBSCRIPTION</p>
          <div className="space-y-1">
            <Button
              onClick={() => navigate('/subscription')}
              variant={location.pathname === '/subscription' ? 'default' : 'ghost'}
              className="w-full justify-start gap-2"
              size="sm"
            >
              <CreditCard className="h-4 w-4" />
              Usage & Limits
            </Button>
            <Button
              onClick={() => navigate('/pricing')}
              variant={location.pathname === '/pricing' ? 'default' : 'ghost'}
              className="w-full justify-start gap-2"
              size="sm"
            >
              <Crown className="h-4 w-4" />
              Upgrade Plan
            </Button>
          </div>
        </div>

        {/* New Chat Button */}
        {location.pathname === '/chat' && (
          <div className="px-4 pb-4">
            <Button
              onClick={onNewConversation}
              className="w-full justify-start gap-2"
              variant="outline"
            >
              <MessageSquarePlus className="h-4 w-4" />
              New Chat
            </Button>
          </div>
        )}

        {/* Conversations List */}
        {location.pathname === '/chat' && conversations && (
          <div className="flex-1 overflow-y-auto scrollbar-thin p-2 space-y-2">
            {conversations.map((conversation) => (
            <Card
              key={conversation.id}
              className={cn(
                'p-3 cursor-pointer transition-colors group',
                currentConversationId === conversation.id
                  ? 'bg-accent'
                  : 'hover:bg-accent/50'
              )}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{conversation.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {format(new Date(conversation.updated_at), 'MMM d, HH:mm')}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conversation.id);
                  }}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </Card>
          ))}
          </div>
        )}

        {/* User & Settings */}
        <div className="border-t p-4 space-y-2">
          <div className="flex items-center gap-2 mb-2">
            <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
              {user?.username?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.username}</p>
              <p className="text-xs text-muted-foreground truncate">
                {user?.email}
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={toggleTheme}
              title="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>
            <Button variant="outline" size="icon" title="Settings">
              <Settings className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={logout}
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-30 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
