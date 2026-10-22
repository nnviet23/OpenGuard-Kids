import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import styles from './DashboardLayout.module.css';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function DashboardLayout() {
  const [selectedChild, setSelectedChild] = useState('child_1');

  const handleEmergency = (action) => {
    if (action === 'lock') {
      if (window.confirm("Xác nhận gửi tín hiệu KHÓA MÁY khẩn cấp qua WebSocket?")) {
        alert(`[WebSocket] Gửi lệnh: LOCK_NOW -> Thiết bị: ${selectedChild}`);
      }
    } else if (action === 'unlock') {
      alert(`[WebSocket] Gửi lệnh: UNLOCK_NOW -> Thiết bị: ${selectedChild}`);
    } else if (action === 'extend15') {
      alert(`[WebSocket] Gửi lệnh: OVERRIDE_TIME (+15 mins) -> Thiết bị: ${selectedChild}`);
    }
  };

  return (
    <div className={styles.layout}>
      <Sidebar pendingCount={2} />
      <div className={styles.mainWrapper}>
        <Topbar 
          currentChild={selectedChild} 
          onSelectChild={setSelectedChild} 
          onEmergencyCommand={handleEmergency}
        />
        <main className={styles.content}>
          <Outlet context={{ selectedChild }} />
        </main>
      </div>
    </div>
  );
}