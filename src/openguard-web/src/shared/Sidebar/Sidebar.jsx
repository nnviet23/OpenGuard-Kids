import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Clock, Calendar, Layers,
  MessageSquare, BarChart2, ListCheck, Settings, ShieldCheck
} from 'lucide-react';
import { useSidebar } from '../../core/SidebarContext';
import styles from './Sidebar.module.css';

export default function Sidebar() {
  const { isCollapsed } = useSidebar();

  const navItems = [
    { label: 'Tổng quan', icon: LayoutDashboard, path: '/' },
    { label: 'Thời gian sử dụng', icon: Clock, path: '/time-schedule' },
    { label: 'Ứng dụng & Website', icon: Layers, path: '/sites' },
    { label: 'Yêu cầu từ trẻ', icon: MessageSquare, path: '/chats', badge: '2' },
    { label: 'Nhật ký & Kiểm toán', icon: ListCheck, path: '/tasks' },
    { label: 'Cài đặt', icon: Settings, path: '/settings' },
  ];

  return (
    <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : styles.expanded}`}>
      {/* Brand Logo */}
      <div className={`${styles.brandRow} ${isCollapsed ? styles.brandRowCollapsed : ''}`}>
        <div className={styles.brandIconBox}>
          <ShieldCheck size={18} />
        </div>
        {!isCollapsed && (
          <div className={styles.brandTextGroup}>
            <span className={styles.brandTitle}>OpenGuard Kids</span>
            <span className={styles.brandSubtitle}>Cùng con an toàn</span>
          </div>
        )}
      </div>

      {/* Menu Navigation */}
      <div className={styles.contentArea}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `${styles.navLink} ${isCollapsed ? styles.navLinkCollapsed : styles.navLinkExpanded} ${
                  isActive ? styles.navLinkActive : ''
                }`
              }
              title={isCollapsed ? item.label : undefined}
            >
              <Icon size={18} />
              {!isCollapsed && <span>{item.label}</span>}
              {!isCollapsed && item.badge && (
                <span className={styles.navBadge}>{item.badge}</span>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Cục User Profile ở dưới đã được xóa bỏ hoàn toàn */}
    </aside>
  );
}
