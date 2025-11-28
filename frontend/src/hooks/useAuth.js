import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '@/services/api';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setAuth: (user, token) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        set({ user, token, isAuthenticated: true });
      },

      logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        set({ user: null, token: null, isAuthenticated: false });
      },

      loadUser: async () => {
        try {
          const token = localStorage.getItem('token');
          if (token) {
            const response = await authAPI.getCurrentUser();
            set({ user: response.data, token, isAuthenticated: true });
          }
        } catch (error) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          set({ user: null, token: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);

export const useAuth = () => {
  const { user, token, isAuthenticated, setAuth, logout, loadUser } = useAuthStore();
  return { user, token, isAuthenticated, setAuth, logout, loadUser };
};
