import { Sidebar } from './Sidebar';
import { useQuery, useMutation, useQueryClient } from '@tantml:query';
import { chatAPI } from '@/services/api';
import { useLocation } from 'react-router-dom';

export function Layout({ children }) {
  const queryClient = useQueryClient();
  const location = useLocation();

  // Only fetch conversations on chat page
  const { data: conversations = [] } = useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      const response = await chatAPI.getConversations();
      return response.data;
    },
    enabled: location.pathname === '/chat',
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => chatAPI.deleteConversation(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['conversations']);
    },
  });

  return (
    <div className="flex h-screen">
      <Sidebar
        conversations={conversations}
        onDeleteConversation={deleteMutation.mutate}
      />
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
}
