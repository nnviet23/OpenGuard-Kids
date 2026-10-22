import React from 'react';
import { NavLink } from 'react-router-dom';
import styles from './Sidebar.module.css';
import {
  IconOverview,
  IconSchedule,
  IconRequests,
  IconApps,
  IconReports,
  IconAudit,
  IconSettings
} from '../icons/PixelIcons';

export default function Sidebar({ pendingCount = 2 }) {
  const navItems = [
    { to: '/overview', label: 'Tổng quan', icon: <IconOverview /> },
    { to: '/schedule', label: 'Lịch tuần', icon: <IconSchedule /> },
    { to: '/requests', label: 'Yêu cầu từ trẻ', icon: <IconRequests />, badge: pendingCount },
    { to: '/apps', label: 'Ứng dụng & Web', icon: <IconApps /> },
    { to: '/reports', label: 'Báo cáo', icon: <IconReports /> },
    { to: '/audit', label: 'Nhật ký (Audit)', icon: <IconAudit /> },
    { to: '/settings', label: 'Cài đặt', icon: <IconSettings /> },
  ];

  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <div className={styles.badge}>OG</div>
        <div>
          <h1 className={styles.title}>OpenGuard</h1>
          <span className={styles.sub}>PARENT CONTROL</span>
        </div>
      </div>

      <nav className={styles.menu}>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `${styles.navLink} ${isActive ? styles.active : ''}`
            }
          >
            <div className={styles.linkContent}>
              {item.icon}
              <span>{item.label}</span>
            </div>
            {item.badge > 0 && <span className={styles.counter}>{item.badge}</span>}
          </NavLink>
        ))}
      </nav>

      <div className={styles.bottom}>
        <div>PROTOCOL: TLS 1.3</div>
        <div>STATUS: ACTIVE_GUARD</div>
      </div>
    </aside>
  );
}