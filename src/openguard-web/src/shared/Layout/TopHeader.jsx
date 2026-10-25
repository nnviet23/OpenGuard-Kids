import { LogOut, Menu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../core/AuthContext';
import { useChild } from '../../core/ChildContext';

export default function TopHeader({ onMenu }) {
  const { account, logout, isChildView } = useAuth();
  const { children, childId, select } = useChild();
  const navigate = useNavigate();
  const name = account?.display_name || account?.email?.split('@')[0] || '';
  return (
    <header className="og-top">
      <button className="og-menu" onClick={onMenu} aria-label="Mở menu"><Menu size={20} /></button>
      {!isChildView && children.length > 0 && (
        <select className="sel og-child-sel" value={childId || ''} onChange={(e) => select(e.target.value)} aria-label="Chọn trẻ">
          {children.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      )}
      <div style={{ flex: 1 }} />
      <div className="og-user">
        <div className="og-avatar">{name.slice(0, 2).toUpperCase()}</div>
        <div className="og-user-t"><b>{name}</b><span>{isChildView ? 'Xem (trẻ)' : account?.role === 'admin' ? 'Quản trị' : 'Phụ huynh'}</span></div>
      </div>
      <button className="og-menu" title="Đăng xuất" aria-label="Đăng xuất" onClick={async () => { await logout(); navigate('/login'); }}><LogOut size={18} /></button>
    </header>
  );
}
