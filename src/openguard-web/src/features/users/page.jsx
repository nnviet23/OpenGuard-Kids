import { useState } from 'react';
import {
  Search, PlusCircle, Monitor, Laptop, Smartphone,
  UserPlus, Lock, Unlock, Clock, MoreHorizontal
} from 'lucide-react';
import styles from './users.module.css';

// Dữ liệu giả lập danh sách thiết bị
const DEVICES_DATA = [
  { id: 'ogk_dev_1', name: 'PC Phòng Khách', type: 'desktop', user: 'Bi (Nguyễn Văn A)', status: 'Active', used: '2h 15m', limit: '3h/ngày' },
  { id: 'ogk_dev_2', name: 'Laptop Nam', type: 'laptop', user: 'Nam (Nguyễn Văn B)', status: 'Offline', used: '0h 0m', limit: '2h/ngày' },
  { id: 'ogk_dev_3', name: 'Tablet Của Bi', type: 'tablet', user: 'Bi (Nguyễn Văn A)', status: 'Locked', used: '1h 0m', limit: '1h/ngày' },
];

export default function UsersPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const getDeviceIcon = (type) => {
    switch (type) {
      case 'desktop': return <Monitor size={18} />;
      case 'laptop': return <Laptop size={18} />;
      case 'tablet': return <Smartphone size={18} />;
      default: return <Monitor size={18} />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Active': return <span className={`${styles.badge} ${styles.badgeActive}`}>Đang hoạt động</span>;
      case 'Offline': return <span className={`${styles.badge} ${styles.badgeOffline}`}>Ngoại tuyến</span>;
      case 'Locked': return <span className={`${styles.badge} ${styles.badgeLocked}`}>Đang khóa</span>;
      default: return null;
    }
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Quản lý thiết bị con</h1>
          <p className={styles.subtitle}>Giám sát trạng thái, giới hạn thời gian và quản lý quyền truy cập.</p>
        </div>
      </header>

      {/* Toolbar */}
      <div className={styles.toolbar}>
        <div className={styles.leftToolbar}>
          <div className={styles.searchBox}>
            <Search size={15} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Tìm kiếm thiết bị hoặc người dùng..."
              className={styles.searchInput}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button className={styles.filterBtn}>
            <PlusCircle size={14} />
            <span>Trạng thái</span>
          </button>
        </div>

        <button className={styles.addBtn}>
          <UserPlus size={16} />
          <span>Thêm thiết bị mới</span>
        </button>
      </div>

      {/* Table */}
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>Thiết bị</th>
              <th className={styles.th}>Định danh con</th>
              <th className={styles.th}>Trạng thái</th>
              <th className={styles.th}>Thời gian / Giới hạn</th>
              <th className={styles.th}>Thao tác nhanh</th>
            </tr>
          </thead>
          <tbody>
            {DEVICES_DATA.filter(dev =>
              dev.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
              dev.user.toLowerCase().includes(searchQuery.toLowerCase())
            ).map((device) => (
              <tr key={device.id} className={styles.tr}>
                {/* Cột 1: Thông tin thiết bị */}
                <td className={styles.td}>
                  <div className={styles.deviceCell}>
                    <div className={styles.deviceIcon}>
                      {getDeviceIcon(device.type)}
                    </div>
                    <div className={styles.deviceInfo}>
                      <span className={styles.deviceName}>{device.name}</span>
                      <span className={styles.deviceId}>{device.id}</span>
                    </div>
                  </div>
                </td>

                {/* Cột 2: Tên con */}
                <td className={styles.td} style={{ fontWeight: 500 }}>
                  {device.user}
                </td>

                {/* Cột 3: Trạng thái */}
                <td className={styles.td}>
                  {getStatusBadge(device.status)}
                </td>

                {/* Cột 4: Hạn mức thời gian */}
                <td className={styles.td}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    <span style={{ fontWeight: 600 }}>{device.used}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ {device.limit}</span>
                  </div>
                </td>

                {/* Cột 5: Hành động */}
                <td className={styles.td}>
                  <div className={styles.actionsCell}>
                    {device.status === 'Locked' ? (
                      <button className={styles.actionBtn} onClick={() => alert(`Mở khóa ${device.name}`)}>
                        <Unlock size={14} /> Mở khóa
                      </button>
                    ) : (
                      <button className={`${styles.actionBtn} ${styles.actionBtnDanger}`} onClick={() => alert(`Khóa ${device.name}`)}>
                        <Lock size={14} /> Khóa máy
                      </button>
                    )}

                    <button className={styles.actionBtn} onClick={() => alert(`Gia hạn thêm 15 phút cho ${device.name}`)}>
                      <Clock size={14} /> +15p
                    </button>

                    <button className={styles.iconBtn}>
                      <MoreHorizontal size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
