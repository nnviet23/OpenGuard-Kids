import { useState } from 'react';
import {
  ListCheck, Search, Download, Filter, Monitor, Smartphone,
  Settings, Globe, ShieldAlert, CheckCircle2, ChevronLeft, ChevronRight
} from 'lucide-react';
import styles from './tasks.module.css';

// Dữ liệu giả lập hoạt động hệ thống
const LOGS_DATA = [
  { id: 1, time: '14:32', date: 'Hôm nay', device: 'Laptop PC-Nam', type: 'desktop', action: 'Truy cập website', detail: 'youtube.com', status: 'Access' },
  { id: 2, time: '11:42', date: 'Hôm nay', device: 'Tablet Của Bi', type: 'tablet', action: 'Bị chặn truy cập', detail: 'tiktok.com', status: 'Alert' },
  { id: 3, time: '09:15', date: 'Hôm nay', device: 'Hệ thống (Phụ huynh)', type: 'system', action: 'Cập nhật luật', detail: 'Giới hạn thời gian YouTube còn 30p', status: 'Setting' },
  { id: 4, time: '20:15', date: 'Hôm qua', device: 'Hệ thống (Phụ huynh)', type: 'system', action: 'Gia hạn thời gian', detail: '+30 phút cho Laptop PC-Nam', status: 'Setting' },
  { id: 5, time: '17:00', date: 'Hôm qua', device: 'Tablet Của Bi', type: 'tablet', action: 'Khóa máy tự động', detail: 'Hết thời hạn sử dụng trong ngày', status: 'System' },
  { id: 6, time: '15:30', date: 'Hôm qua', device: 'Laptop PC-Nam', type: 'desktop', action: 'Truy cập ứng dụng', detail: 'Microsoft Word', status: 'Access' },
];

export default function TasksPage() {
  const [activeTab, setActiveTab] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Lọc dữ liệu
  const filteredLogs = LOGS_DATA.filter(log => {
    const matchesTab = activeTab === 'All' || log.status === activeTab;
    const matchesSearch = log.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          log.detail.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          log.device.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTab && matchesSearch;
  });

  const getDeviceIcon = (type) => {
    switch(type) {
      case 'desktop': return <Monitor size={16} className={styles.deviceIcon} />;
      case 'tablet': return <Smartphone size={16} className={styles.deviceIcon} />;
      case 'system': return <Settings size={16} className={styles.deviceIcon} />;
      default: return <Monitor size={16} className={styles.deviceIcon} />;
    }
  };

  const getStatusBadge = (status) => {
    switch(status) {
      case 'Alert': return <span className={`${styles.badge} ${styles.badgeAlert}`}><ShieldAlert size={14}/> Cảnh báo</span>;
      case 'Access': return <span className={`${styles.badge} ${styles.badgeAccess}`}><Globe size={14}/> Cho phép</span>;
      case 'System': return <span className={`${styles.badge} ${styles.badgeSystem}`}><Monitor size={14}/> Tự động</span>;
      case 'Setting': return <span className={`${styles.badge} ${styles.badgeSetting}`}><CheckCircle2 size={14}/> Cài đặt</span>;
      default: return null;
    }
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.titleWrap}>
          <div className={styles.headerIcon}><ListCheck size={24} /></div>
          <div>
            <h1 className={styles.title}>Nhật ký & Kiểm toán</h1>
            <p className={styles.subtitle}>Ghi nhận toàn bộ hoạt động truy cập, cảnh báo và thay đổi cài đặt hệ thống.</p>
          </div>
        </div>

        <div className={styles.headerActions}>
          <button className={styles.btnOutline}>
            <Filter size={16} /> Bộ lọc nâng cao
          </button>
          <button className={styles.btnOutline}>
            <Download size={16} /> Xuất dữ liệu
          </button>
        </div>
      </header>

      {/* Main Card */}
      <div className={styles.card}>

        {/* Toolbar */}
        <div className={styles.toolbar}>
          <div className={styles.filterTabs}>
            <button className={`${styles.pill} ${activeTab === 'All' ? styles.pillActive : ''}`} onClick={() => setActiveTab('All')}>Tất cả</button>
            <button className={`${styles.pill} ${activeTab === 'Alert' ? styles.pillActive : ''}`} onClick={() => setActiveTab('Alert')}>Cảnh báo chặn</button>
            <button className={`${styles.pill} ${activeTab === 'Setting' ? styles.pillActive : ''}`} onClick={() => setActiveTab('Setting')}>Thay đổi cài đặt</button>
            <button className={`${styles.pill} ${activeTab === 'Access' ? styles.pillActive : ''}`} onClick={() => setActiveTab('Access')}>Truy cập</button>
          </div>

          <div className={styles.searchBox}>
            <Search size={16} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Tìm kiếm hành động, thiết bị..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Table */}
        <table className={styles.table}>
          <thead>
            <tr>
              <th style={{ width: '150px' }}>Thời gian</th>
              <th style={{ width: '220px' }}>Nguồn / Thiết bị</th>
              <th>Hành động / Sự kiện</th>
              <th style={{ width: '150px' }}>Phân loại</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.map(log => (
              <tr key={log.id}>
                <td>
                  <div className={styles.timeCell}>
                    <span className={styles.timeText}>{log.time}</span>
                    <span className={styles.dateText}>{log.date}</span>
                  </div>
                </td>
                <td>
                  <div className={styles.deviceCell}>
                    {getDeviceIcon(log.type)}
                    {log.device}
                  </div>
                </td>
                <td>
                  <div className={styles.actionCell}>
                    <span className={styles.actionTitle}>{log.action}</span>
                    <span className={styles.actionDetail}>{log.detail}</span>
                  </div>
                </td>
                <td>
                  {getStatusBadge(log.status)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div className={styles.pagination}>
          <span>Hiển thị 1 - {filteredLogs.length} trong {filteredLogs.length} kết quả</span>
          <div className={styles.pageControls}>
            <button className={styles.pageBtn}><ChevronLeft size={16}/></button>
            <button className={`${styles.pageBtn} ${styles.pageBtnActive}`}>1</button>
            <button className={styles.pageBtn}>2</button>
            <button className={styles.pageBtn}>3</button>
            <button className={styles.pageBtn}><ChevronRight size={16}/></button>
          </div>
        </div>

      </div>
    </div>
  );
}
