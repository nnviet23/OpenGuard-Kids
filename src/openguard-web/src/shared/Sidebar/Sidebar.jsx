import { NavLink } from 'react-router-dom';
import { BookOpenCheck, ClipboardList, Clock, Layers, LayoutDashboard, MessageSquare, Settings, ShieldCheck, Users } from 'lucide-react';
import { useAuth } from '../../core/AuthContext';

export default function Sidebar({ open, onNavigate, pending = 0 }) {
  const { isChildView } = useAuth();
  const items = isChildView
    ? [
        { label: 'Hôm nay em đã dùng gì', icon: BookOpenCheck, path: '/today' },
        { label: 'Ai đổi quy tắc', icon: ClipboardList, path: '/audit' },
        { label: 'Xin thêm giờ / báo chặn nhầm', icon: MessageSquare, path: '/requests' },
        { label: 'Tài khoản', icon: Settings, path: '/settings' },
      ]
    : [
        { label: 'Tổng quan', icon: LayoutDashboard, path: '/' },
        { label: 'Thời gian sử dụng', icon: Clock, path: '/time-schedule' },
        { label: 'Ứng dụng & Website', icon: Layers, path: '/rules' },
        { label: 'Yêu cầu từ trẻ', icon: MessageSquare, path: '/requests', badge: pending || null },
        { label: 'Màn hình của trẻ', icon: BookOpenCheck, path: '/today' },
        { label: 'Nhật ký & Kiểm toán', icon: ClipboardList, path: '/audit' },
        { label: 'Gia đình & Thiết bị', icon: Users, path: '/family' },
        { label: 'Cài đặt & Quyền riêng tư', icon: Settings, path: '/settings' },
      ];
  return (
    <aside className={`og-side ${open ? 'open' : ''}`}>
      <div className="og-brand">
        <div className="og-brand-icon"><ShieldCheck size={18} /></div>
        <div><div className="og-brand-t">OpenGuard Kids</div><div className="og-brand-s">Cùng con an toàn</div></div>
      </div>
      <nav>
        {items.map(({ label, icon: Icon, path, badge }) => (
          <NavLink key={path} to={path} end={path === '/'} onClick={onNavigate}
            className={({ isActive }) => `og-nav ${isActive ? 'on' : ''}`}>
            <Icon size={18} /><span>{label}</span>
            {badge ? <span className="og-badge">{badge}</span> : null}
          </NavLink>
        ))}
      </nav>
      <div className="og-side-foot">Chỉ ghi tên ứng dụng & tên miền. Dữ liệu tự xóa sau 90 ngày.</div>
    </aside>
  );
}
