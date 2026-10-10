import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell, ChevronRight, Clock, ShieldAlert, LogOut, User } from 'lucide-react';
import { useAuth } from '../../core/AuthContext';
import styles from './TopHeader.module.css';

export default function TopHeader() {
  const [isNotiOpen, setIsNotiOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false); // Thêm state cho profile dropdown

  const notiRef = useRef(null);
  const profileRef = useRef(null); // Thêm ref cho profile dropdown

  const location = useLocation();
  const navigate = useNavigate();
  const { parent, logout } = useAuth(); // Lấy thông tin user và hàm logout từ Context

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

  // Đóng dropdown khi click ra ngoài
  useEffect(() => {
    function handleClickOutside(event) {
      if (notiRef.current && !notiRef.current.contains(event.target)) {
        setIsNotiOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setIsProfileOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Xử lý sự kiện đăng xuất
  const handleLogout = () => {
    setIsProfileOpen(false);
    if (logout) {
      logout(); // Gọi hàm xóa token/session ở Context
    }
    navigate('/login'); // Chuyển hướng về trang đăng nhập
  };

  const displayName = parent?.email?.split('@')[0] || 'Phụ huynh';
  const initial = displayName.substring(0, 2).toUpperCase();

  return (
    <header className={styles.topHeader}>
      {/* Breadcrumb thống nhất */}
      <div className={styles.breadcrumb}>
        Trang chủ <ChevronRight size={14} /> <span className={styles.breadcrumbActive}>{currentPage}</span>
      </div>

      <div className={styles.rightActions}>

        {/* Nút Chuông & Popover Thông báo */}
        <div className={styles.notiWrapper} ref={notiRef}>
          <button className={styles.bellBtn} onClick={() => { setIsNotiOpen(!isNotiOpen); setIsProfileOpen(false); }}>
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
              </div>
            </div>
          )}
        </div>

        {/* --- Khu vực User Profile có Dropdown --- */}
        <div className={styles.profileWrapper} ref={profileRef}>
          <div
            className={styles.profile}
            onClick={() => { setIsProfileOpen(!isProfileOpen); setIsNotiOpen(false); }}
          >
            <div className={styles.avatar}>{initial}</div>
            <div className={styles.userInfo}>
              <span className={styles.userName}>{displayName}</span>
              <span className={styles.userRole}>Quản trị viên</span>
            </div>
          </div>

          {/* Menu sổ xuống khi click vào Profile */}
          {isProfileOpen && (
            <div className={styles.profileDropdown}>

              {/* Nút Cài đặt */}
              <div
                className={styles.profileMenuItem}
                onClick={() => {
                  setIsProfileOpen(false);
                  navigate('/settings');
                }}
              >
                <User size={16} /> Thông tin cá nhân
              </div>

              {/* Nút Đăng xuất */}
              <div
                className={`${styles.profileMenuItem} ${styles.profileMenuItemDanger}`}
                onClick={handleLogout}
              >
                <LogOut size={16} /> Đăng xuất khỏi hệ thống
              </div>

            </div>
          )}
        </div>
      </div>
    </header>
  );
}
