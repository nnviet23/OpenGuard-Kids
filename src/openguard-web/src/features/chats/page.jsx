import { Clock, ShieldAlert, Check, X, Calendar, Monitor, Globe, ChevronLeft, ChevronRight, User } from 'lucide-react';
import styles from './chats.module.css';
import {MessageSquare} from "lucide-react";

export default function ChatsPage() {

  // Dữ liệu mock bám sát ảnh thiết kế
  const requestsData = [
    {
      id: 1,
      type: 'Xin thêm giờ sử dụng',
      message: 'Con muốn được thêm 30 phút để học bài môn Toán ạ.',
      child: 'Minh Anh (Con bạn)',
      time: '29/09/2025 15:42',
      device: 'Laptop học tập',
      app: 'Microsoft Edge',
      status: 'pending_time', // Màu vàng
      icon: Clock,
    },
    {
      id: 2,
      type: 'Báo chặn nhầm',
      message: 'Con nghĩ trang này bị chặn nhầm ạ. Đây là trang học tiếng Anh, không phải trang game.',
      child: 'Minh Anh (Con bạn)',
      time: '29/09/2025 12:17',
      device: 'Laptop học tập',
      app: 'https://www.duolingo.com',
      status: 'pending_block', // Màu đỏ
      icon: ShieldAlert,
    },
    {
      id: 3,
      type: 'Xin thêm giờ sử dụng',
      message: 'Con muốn được thêm 15 phút để hoàn thành bài tập tiếng Anh ạ.',
      child: 'Minh Anh (Con bạn)',
      time: '29/09/2025 20:03',
      device: 'Laptop học tập',
      app: 'Google Chrome',
      status: 'approved', // Màu xanh
      icon: Clock,
      actionNote: 'Phụ huynh đã đồng ý\nThêm 15 phút (20:15 - 20:30)'
    },
    {
      id: 4,
      type: 'Cho phép mở ứng dụng',
      message: 'Con muốn được mở ứng dụng Canva để làm bài thuyết trình ạ.',
      child: 'Minh Anh (Con bạn)',
      time: '29/09/2025 16:45',
      device: 'Laptop học tập',
      app: 'Canva',
      status: 'rejected', // Màu tím/nhạt
      icon: Calendar,
      actionNote: 'Lý do: Ứng dụng chưa nằm trong danh sách cho phép hiện tại.'
    },
  ];

  // Helper render styling dựa trên status
  const getCardStyle = (status) => {
    switch (status) {
      case 'pending_time': return { card: styles.cardWarning, icon: styles.iconWarning, statusBg: styles.statusWarning, statusText: 'Đang chờ xử lý' };
      case 'pending_block': return { card: styles.cardDanger, icon: styles.iconDanger, statusBg: styles.statusDanger, statusText: 'Đang chờ xử lý' };
      case 'approved': return { card: styles.cardSuccess, icon: styles.iconSuccess, statusBg: styles.statusSuccess, statusText: 'Đã xử lý' };
      case 'rejected': return { card: styles.cardNeutral, icon: styles.iconPurple, statusBg: styles.statusNeutral, statusText: 'Đã từ chối' };
      default: return { card: '', icon: '', statusBg: '', statusText: '' };
    }
  };

  return (
    <div className={styles.container}>

      {/* Banner */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <div style={{ width: '2.5rem', height: '2.5rem', backgroundColor: 'var(--primary-action)', color: '#fff', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <MessageSquare size={24} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.25rem 0', color: 'var(--text-main)' }}>Yêu cầu từ trẻ</h1>
          <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-muted)' }}>Xem và xử lý các yêu cầu xin thêm giờ hoặc báo chặn nhầm.</p>
        </div>
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        <button className={`${styles.tabBtn} ${styles.tabActive}`}>
          Lịch sử yêu cầu <span className={styles.badgeTab}>2</span>
        </button>
      </div>

      {/* Danh sách Card */}
      <div className={styles.cardList}>
        {requestsData.map(req => {
          const style = getCardStyle(req.status);
          const Icon = req.icon;
          const isPending = req.status.includes('pending');

          return (
            <div key={req.id} className={`${styles.card} ${style.card}`}>

              {/* Icon Trái */}
              <div className={`${styles.iconWrap} ${style.icon}`}>
                <Icon size={24} />
              </div>

              {/* Nội dung Giữa */}
              <div className={styles.cardContent}>
                <h3 className={styles.cardTitle}>{req.type}</h3>
                <p className={styles.cardMessage}>{req.message}</p>
                <div className={styles.childBadge}>
                  <User size={14} /> Từ: {req.child}
                </div>

                <div className={styles.infoRow}>
                  <div className={styles.infoItem}><Calendar size={14} /> {req.time}</div>
                  <div className={styles.infoItem}><Monitor size={14} /> {req.device}</div>
                  <div className={styles.infoItem}><Globe size={14} /> {req.app}</div>
                </div>
              </div>

              {/* Hành động / Trạng thái Phải */}
              <div className={styles.cardActions}>
                <span className={`${styles.statusBadge} ${style.statusBg}`}>
                  <span style={{ fontSize: '10px' }}>●</span> {style.statusText}
                </span>

                {isPending ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', width: '100%' }}>
                    <div className={styles.btnGroup}>
                      <button className={`${styles.btnAction} ${styles.btnApprove}`}><Check size={14} /> Đồng ý</button>
                      <button className={`${styles.btnAction} ${styles.btnReject}`}><X size={14} /> Từ chối</button>
                    </div>
                    <span className={styles.detailLink}>Xem chi tiết</span>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', width: '100%' }}>
                    <div className={styles.actionText} style={{ whiteSpace: 'pre-line' }}>{req.actionNote}</div>
                    <span className={styles.detailLink}>Xem chi tiết</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      <div className={styles.pagination}>
        <span>Hiển thị 1 - 4 trong 6 yêu cầu</span>
        <div className={styles.pageControls}>
          <button className={styles.pageBtn}><ChevronLeft size={16}/></button>
          <button className={`${styles.pageBtn} ${styles.pageBtnActive}`}>1</button>
          <button className={styles.pageBtn}>2</button>
          <button className={styles.pageBtn}><ChevronRight size={16}/></button>
        </div>
      </div>

    </div>
  );
}
