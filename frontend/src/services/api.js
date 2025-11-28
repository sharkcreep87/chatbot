import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  }),
  getCurrentUser: () => api.get('/api/auth/me'),
};

// Chat APIs
export const chatAPI = {
  createConversation: (data) => api.post('/api/chat/conversations', data),
  getConversations: (params) => api.get('/api/chat/conversations', { params }),
  getConversation: (id) => api.get(`/api/chat/conversations/${id}`),
  updateConversation: (id, data) => api.patch(`/api/chat/conversations/${id}`, data),
  deleteConversation: (id) => api.delete(`/api/chat/conversations/${id}`),
  getMessages: (conversationId, params) =>
    api.get(`/api/chat/conversations/${conversationId}/messages`, { params }),
  sendMessage: (data) => api.post('/api/chat/chat', data),
  sendMessageStream: (data) => {
    const token = localStorage.getItem('token');
    return new EventSource(
      `${API_BASE_URL}/api/chat/chat/stream?${new URLSearchParams({
        ...data,
        token,
      })}`
    );
  },
};

export default api;
