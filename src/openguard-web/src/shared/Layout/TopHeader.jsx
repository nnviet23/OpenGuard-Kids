import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, ChevronRight, Clock, ShieldAlert } from 'lucide-react';
import styles from './TopHeader.module.css';

export default function TopHeader() {
  const [isNotiOpen, setIsNotiOpen] = useState(false);
  const location = useLocation();
  const notiRef = useRef(null);

  // Ánh xạ URL sang tên trang
  const pageNames = {
    '/': 'Tổng quan',
    '/time-schedule': 'Thời gian sử dụng',
    '/calendar': 'Lịch tuần',
    '/sites': 'Ứng dụng & Website',
    '/chats': 'Yêu cầu từ trẻ',
    '/reports': 'Báo cáo',
    '/tasks': 'Nhật ký & Kiểm toán',
    '/settings': 'Cài đặt hệ thống'
  };
  const currentPage = pageNames[location.pathname] || 'Dashboard';

  // Đóng noti khi click ra ngoài
  useEffect(() => {
    function handleClickOutside(event) {
      if (notiRef.current && !notiRef.current.contains(event.target)) {
        setIsNotiOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className={styles.topHeader}>
      {/* Breadcrumb thống nhất */}
      <div className={styles.breadcrumb}>
         <ChevronRight size={14} /> <span className={styles.breadcrumbActive}>{currentPage}</span>
      </div>

      <div className={styles.rightActions}>

        {/* Nút Chuông & Popover Thông báo */}
        <div className={styles.notiWrapper} ref={notiRef}>
          <button className={styles.bellBtn} onClick={() => setIsNotiOpen(!isNotiOpen)}>
            <Bell size={18} />
            <span className={styles.bellBadge}>2</span>
          </button>

          {isNotiOpen && (
            <div className={styles.notiDropdown}>
              <div className={styles.notiHeader}>
                <span className={styles.notiTitle}>Thông báo quan trọng</span>
                <span className={styles.notiLink}>Đánh dấu đã đọc</span>
              </div>
              <div className={styles.notiList}>
                <div className={styles.notiItem}>
                  <div className={styles.notiIcon} style={{ backgroundColor: 'var(--primary-light)', color: 'var(--primary-action)' }}><Clock size={16}/></div>
                  <div className={styles.notiContent}>
                    <span className={styles.notiText}>Yêu cầu xin thêm giờ</span>
                    <span className={styles.notiDesc}>14:20 • Laptop Nam muốn thêm 30 phút. Đang chờ bạn duyệt.</span>
                  </div>
                </div>
                <div className={styles.notiItem}>
                  <div className={styles.notiIcon} style={{ backgroundColor: '#fee2e2', color: 'var(--cisco-danger)' }}><ShieldAlert size={16}/></div>
                  <div className={styles.notiContent}>
                    <span className={styles.notiText}>Trang web bị chặn</span>
                    <span className={styles.notiDesc}>11:42 • Truy cập bị chặn tự động bởi hệ thống.</span>
                  </div>
                </div>
                {/* Cuộn mượt mà nếu có nhiều thông báo */}
              </div>
            </div>
          )}
        </div>

        {/* Profile */}
        <div className={styles.profile}>
          <div className={styles.avatar}>PA</div>
          <div className={styles.userInfo}>
            <span className={styles.userName}>Phụ huynh</span>
            <span className={styles.userRole}>Quản trị viên</span>
          </div>
        </div>
      </div>
    </header>
  );
}
