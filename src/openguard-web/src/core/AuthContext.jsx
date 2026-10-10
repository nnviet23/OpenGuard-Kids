import { createContext, useContext, useState, useEffect } from 'react';
import apiClient from './api-client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [parent, setParent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isSubscribed = true;

    const initializeAuth = async () => {
      try {
        const response = await apiClient.get('/auth/me');
        if (isSubscribed) {
          setParent(response.data);
        }
      } catch {
        if (isSubscribed) {
          setParent(null);
        }
      } finally {
        if (isSubscribed) {
          setLoading(false);
        }
      }
    };

    initializeAuth();

    return () => {
      isSubscribed = false;
    };
  }, []);

  const login = async (email, password) => {
    await apiClient.post('/auth/login', { email, password });
    const response = await apiClient.get('/auth/me');
    setParent(response.data);
  };

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      setParent(null);
      window.location.href = '/login';
    }
  };

  return (
    <AuthContext.Provider value={{ parent, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
