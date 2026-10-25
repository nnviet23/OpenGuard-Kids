import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import api from './api-client';
import { useAuth } from './AuthContext';

const ChildContext = createContext(null);

export function ChildProvider({ children: kids }) {
  const { account } = useAuth();
  const [children, setChildren] = useState([]);
  const [selectedId, setSelectedId] = useState(() => {
    try { return localStorage.getItem('ogk_child') || ''; } catch { return ''; }
  });
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    if (!account) return;
    try {
      const { data } = await api.get('/children');
      setChildren(data);
      setSelectedId((cur) => (data.some((c) => c.id === cur) ? cur : data[0]?.id || ''));
    } finally {
      setLoading(false);
    }
  }, [account]);

  useEffect(() => { reload(); }, [reload]);

  const select = (id) => {
    setSelectedId(id);
    try { localStorage.setItem('ogk_child', id); } catch { /* bỏ qua */ }
  };

  const child = children.find((c) => c.id === selectedId) || null;
  return (
    <ChildContext.Provider value={{ children, child, childId: child?.id || null, select, reload, loading }}>
      {kids}
    </ChildContext.Provider>
  );
}

export function useChild() {
  const ctx = useContext(ChildContext);
  if (!ctx) throw new Error('useChild phải nằm trong ChildProvider');
  return ctx;
}
