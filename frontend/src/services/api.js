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

// Knowledge Base APIs
export const knowledgeBaseAPI = {
  createKnowledgeBase: (data) => api.post('/api/kb/knowledge-bases', data),
  getKnowledgeBases: (params) => api.get('/api/kb/knowledge-bases', { params }),
  getKnowledgeBase: (id) => api.get(`/api/kb/knowledge-bases/${id}`),
  updateKnowledgeBase: (id, data) => api.patch(`/api/kb/knowledge-bases/${id}`, data),
  deleteKnowledgeBase: (id) => api.delete(`/api/kb/knowledge-bases/${id}`),
  uploadDocument: (kbId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/api/kb/knowledge-bases/${kbId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getDocuments: (kbId, params) => api.get(`/api/kb/knowledge-bases/${kbId}/documents`, { params }),
  deleteDocument: (docId) => api.delete(`/api/kb/documents/${docId}`),
  searchKnowledgeBase: (kbId, query, nResults = 5) => {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('n_results', nResults);
    return api.post(`/api/kb/knowledge-bases/${kbId}/search`, formData);
  },
};

// Analytics APIs
export const analyticsAPI = {
  getAnalytics: (days = 30) => api.get('/api/analytics', { params: { days } }),
  getKnowledgeBaseAnalytics: () => api.get('/api/analytics/knowledge-bases'),
  trackEvent: (eventType, eventData) =>
    api.post('/api/analytics/track', { event_type: eventType, event_data: eventData }),
};

// Vendor APIs
export const vendorAPI = {
  createVendor: (data) => api.post('/api/vendor/vendors', data),
  getMyVendor: () => api.get('/api/vendor/vendors/me'),
  updateMyVendor: (data) => api.patch('/api/vendor/vendors/me', data),
  getSubscription: () => api.get('/api/vendor/subscription'),
  createOrUpdateSubscription: (data) => api.post('/api/vendor/subscription', data),
  getUsageLimits: () => api.get('/api/vendor/usage-limits'),
};

// Subscription Plan APIs
export const subscriptionAPI = {
  getPlans: () => api.get('/api/subscription/plans'),
  getPlan: (id) => api.get(`/api/subscription/plans/${id}`),
};

export default api;
