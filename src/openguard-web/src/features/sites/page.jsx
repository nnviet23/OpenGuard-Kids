import { ChevronRight, ChevronLeft, LayoutGrid, Globe, Search, Plus, CheckCircle2, Ban, Clock, MoreHorizontal, ShieldCheck, CheckSquare, XSquare } from 'lucide-react';
import styles from './sites.module.css';

export default function SitesPage() {

  // Dữ liệu giả lập (Apps)
  const appsData = [
    { id: 1, name: 'Google Chrome', cat: 'Trình duyệt web', status: 'Allowed', time: '07:00 - 21:00 (Hàng ngày)', color: '#10b981' },
    { id: 2, name: 'YouTube', cat: 'Giải trí', status: 'Allowed', time: '07:00 - 21:00 (Hàng ngày)', color: '#ef4444' },
    { id: 3, name: 'Zalo', cat: 'Liên lạc', status: 'Allowed', time: '07:00 - 22:00 (Hàng ngày)', color: '#3b82f6' },
    { id: 4, name: 'Microsoft Word', cat: 'Học tập', status: 'Allowed', time: '07:00 - 20:00 (Hàng ngày)', color: '#2563eb' },
    { id: 5, name: 'TikTok', cat: 'Mạng xã hội', status: 'Blocked', time: '--', color: '#000000' },
    { id: 6, name: 'Facebook', cat: 'Mạng xã hội', status: 'Blocked', time: '--', color: '#1877f2' },
    { id: 7, name: 'Instagram', cat: 'Mạng xã hội', status: 'Blocked', time: '--', color: '#e1306c' },
    { id: 8, name: 'Minecraft', cat: 'Trò chơi', status: 'Limited', time: '17:00 - 19:00 (Hàng ngày)', color: '#84cc16' },
  ];

  // Dữ liệu giả lập (Websites)
  const webData = [
    { id: 1, name: 'youtube.com', cat: 'Giải trí', status: 'Allowed', time: '07:00 - 21:00 (Hàng ngày)', color: '#ef4444' },
    { id: 2, name: 'facebook.com', cat: 'Mạng xã hội', status: 'Blocked', time: '--', color: '#1877f2' },
    { id: 3, name: 'tiktok.com', cat: 'Mạng xã hội', status: 'Blocked', time: '--', color: '#000000' },
    { id: 4, name: 'chat.openai.com', cat: 'Học tập', status: 'Allowed', time: '07:00 - 21:00 (Hàng ngày)', color: '#10b981' },
    { id: 5, name: 'gameviet.com', cat: 'Trò chơi', status: 'Limited', time: '17:00 - 19:00 (Hàng ngày)', color: '#f59e0b' },
  ];

  const getStatusBadge = (status) => {
    switch(status) {
      case 'Allowed': return <span className={`${styles.statusBadge} ${styles.badgeAllowed}`}><CheckCircle2 size={12}/> Được phép</span>;
      case 'Blocked': return <span className={`${styles.statusBadge} ${styles.badgeBlocked}`}><Ban size={12}/> Bị chặn</span>;
      case 'Limited': return <span className={`${styles.statusBadge} ${styles.badgeLimited}`}><Clock size={12}/> Giới hạn thời gian</span>;
      default: return null;
    }
  };

  return (
    <div className={styles.container}>
      {/* Breadcrumb */}
      <div className={styles.breadcrumb}>
        Trang chủ <ChevronRight size={14} /> Ứng dụng & Website
      </div>

      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerIcon}><LayoutGrid size={24} /></div>
        <div>
          <h1 className={styles.title}>Quản lý ứng dụng & Website</h1>
          <p className={styles.subtitle}>Thiết lập danh sách ứng dụng, website được phép hoặc bị chặn theo độ tuổi và thời gian.</p>
        </div>
      </div>

      {/* Main Tabs */}
      <div className={styles.mainTabs}>
        <button className={`${styles.tabBtn} ${styles.tabActive}`}><LayoutGrid size={16} /> Ứng dụng</button>
        <button className={styles.tabBtn}><Globe size={16} /> Website</button>
        <button className={styles.tabBtn}><CheckSquare size={16} /> Danh sách cho phép</button>
        <button className={styles.tabBtn}><XSquare size={16} /> Danh sách chặn</button>
      </div>

      {/* Info Banner */}
      <div className={styles.infoBanner}>
        <div className={styles.infoBannerLeft}>
          <ShieldCheck size={18} color="var(--primary-action)" />
          <span>Chế độ lọc hiện tại: <strong>Chặn theo danh sách đen + Giới hạn theo thời gian</strong></span>
        </div>
        <button className={styles.linkBtn}>Chỉnh sửa quy tắc <ChevronRight size={14}/></button>
      </div>

      {/* --- Khối Danh sách Ứng dụng --- */}
      <div className={styles.listCard}>
        <div className={styles.cardHeader}>
          <div className={styles.cardTitleWrap}>
            <LayoutGrid size={20} color="var(--primary-action)" />
            <h3 className={styles.cardTitle}>Danh sách ứng dụng</h3>
            <span className={styles.countBadge}>12 ứng dụng</span>
          </div>
          <button className={styles.primaryBtn}><Plus size={16}/> Thêm ứng dụng</button>
        </div>

        <div className={styles.toolbar}>
          <div className={styles.searchBox}>
            <Search size={16} color="var(--text-muted)" />
            <input type="text" placeholder="Tìm kiếm ứng dụng..." />
          </div>
          <div className={styles.filterPills}>
            <button className={`${styles.pill} ${styles.pillActive}`}>Tất cả (12)</button>
            <button className={styles.pill}>Được phép (7)</button>
            <button className={styles.pill}>Bị chặn (4)</button>
            <button className={styles.pill}>Giới hạn thời gian (1)</button>
          </div>
        </div>

        <table className={styles.table}>
          <thead>
            <tr>
              <th style={{ width: '40px' }}><input type="checkbox" /></th>
              <th>Tên ứng dụng</th>
              <th>Danh mục</th>
              <th>Trạng thái</th>
              <th>Thời gian cho phép</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {appsData.map(app => (
              <tr key={app.id}>
                <td><input type="checkbox" /></td>
                <td>
                  <div className={styles.nameCell}>
                    <div className={styles.appIcon} style={{ backgroundColor: app.color }}>
                      {app.name.substring(0, 1)}
                    </div>
                    {app.name}
                  </div>
                </td>
                <td className={styles.categoryText}>{app.cat}</td>
                <td>{getStatusBadge(app.status)}</td>
                <td className={styles.timeText}>{app.time}</td>
                <td>
                  <div className={styles.actionCell}>
                    <button className={styles.actionBtn}>Chỉnh sửa</button>
                    <MoreHorizontal size={16} className={styles.moreBtn} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className={styles.pagination}>
          <span>Hiển thị 1 - 8 trong 12 ứng dụng</span>
          <div className={styles.pageControls}>
            <button className={styles.pageBtn}><ChevronLeft size={16}/></button>
            <button className={`${styles.pageBtn} ${styles.pageBtnActive}`}>1</button>
            <button className={styles.pageBtn}>2</button>
            <button className={styles.pageBtn}><ChevronRight size={16}/></button>
          </div>
        </div>
      </div>

      {/* --- Khối Danh sách Website --- */}
      <div className={styles.listCard}>
        <div className={styles.cardHeader}>
          <div className={styles.cardTitleWrap}>
            <Globe size={20} color="var(--primary-action)" />
            <h3 className={styles.cardTitle}>Danh sách website</h3>
            <span className={styles.countBadge}>8 website</span>
          </div>
          <button className={styles.primaryBtn}><Plus size={16}/> Thêm website</button>
        </div>

        <div className={styles.toolbar}>
          <div className={styles.searchBox}>
            <Search size={16} color="var(--text-muted)" />
            <input type="text" placeholder="Tìm kiếm website..." />
          </div>
          <div className={styles.filterPills}>
            <button className={`${styles.pill} ${styles.pillActive}`}>Tất cả (8)</button>
            <button className={styles.pill}>Được phép (5)</button>
            <button className={styles.pill}>Bị chặn (2)</button>
            <button className={styles.pill}>Giới hạn thời gian (1)</button>
          </div>
        </div>

        <table className={styles.table}>
          <thead>
            <tr>
              <th style={{ width: '40px' }}><input type="checkbox" /></th>
              <th>Tên website / Miền</th>
              <th>Danh mục</th>
              <th>Trạng thái</th>
              <th>Thời gian cho phép</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {webData.map(web => (
              <tr key={`web-${web.id}`}>
                <td><input type="checkbox" /></td>
                <td>
                  <div className={styles.nameCell}>
                    <div className={styles.appIcon} style={{ backgroundColor: web.color }}>
                      {web.name.substring(0, 1).toUpperCase()}
                    </div>
                    {web.name}
                  </div>
                </td>
                <td className={styles.categoryText}>{web.cat}</td>
                <td>{getStatusBadge(web.status)}</td>
                <td className={styles.timeText}>{web.time}</td>
                <td>
                  <div className={styles.actionCell}>
                    <button className={styles.actionBtn}>Chỉnh sửa</button>
                    <MoreHorizontal size={16} className={styles.moreBtn} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className={styles.pagination}>
          <span>Hiển thị 1 - 5 trong 8 website</span>
          <div className={styles.pageControls}>
            <button className={styles.pageBtn}><ChevronLeft size={16}/></button>
            <button className={`${styles.pageBtn} ${styles.pageBtnActive}`}>1</button>
            <button className={styles.pageBtn}>2</button>
            <button className={styles.pageBtn}><ChevronRight size={16}/></button>
          </div>
        </div>
      </div>

    </div>
  );
}
