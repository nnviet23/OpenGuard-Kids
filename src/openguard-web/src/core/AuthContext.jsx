import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import api, { setCsrf, setUnauthorizedHandler } from './api-client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const { data } = await api.get('/auth/me');
      setCsrf(data.csrf_token);
      setAccount(data.account);
    } catch {
      setAccount(null);
      setCsrf(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => { setAccount(null); setCsrf(null); });
    api.get('/auth/me')
      .then(({ data }) => { setCsrf(data.csrf_token); setAccount(data.account); })
      .catch(() => { setAccount(null); setCsrf(null); })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password, totp) => {
    const { data } = await api.post('/auth/login', { email, password, totp: totp || null });
    setCsrf(data.csrf_token);
    setAccount(data.account);
    return data.account;
  };

  const logout = async () => {
    try { await api.post('/auth/logout'); } finally { setAccount(null); setCsrf(null); }
  };

  const isChildView = account?.role === 'child_view';
  const isParent = account?.role === 'parent';
  return (
    <AuthContext.Provider value={{ account, parent: account, loading, login, logout, reload: load, isChildView, isParent }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth phải nằm trong AuthProvider');
  return ctx;
}
