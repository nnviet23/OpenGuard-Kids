import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import api from '../../core/api-client';
import { useAuth } from '../../core/AuthContext';
import Sidebar from '../Sidebar/Sidebar';
import TopHeader from './TopHeader';

export default function DashboardLayout() {
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(0);
  const { isParent } = useAuth();
  const loc = useLocation();
  useEffect(() => {
    if (!isParent) return undefined;
    let alive = true;
    const load = () => api.get('/requests', { params: { status: 'pending' } }).then((r) => alive && setPending(r.data.length)).catch(() => {});
    load();
    const t = setInterval(load, 30000);
    return () => { alive = false; clearInterval(t); };
  }, [isParent, loc.pathname]);
  return (
    <div className="og-shell">
      <Sidebar open={open} onNavigate={() => setOpen(false)} pending={pending} />
      {open && <div className="og-scrim" onClick={() => setOpen(false)} />}
      <div className="og-main">
        <TopHeader onMenu={() => setOpen((o) => !o)} />
        <main className="og-content"><Outlet /></main>
      </div>
    </div>
  );
}
