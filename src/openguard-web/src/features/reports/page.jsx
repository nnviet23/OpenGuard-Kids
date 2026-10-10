import { BarChart2, Calendar, Download, TrendingUp, TrendingDown, Clock, AlertTriangle, ShieldCheck, Gamepad2, BookOpen, MessageSquare, Video } from 'lucide-react';
import styles from './reports.module.css';

export default function ReportsPage() {

  // Dữ liệu mô phỏng cho biểu đồ (Stack bar chart)
  const chartData = [
    { day: 'T2', edu: 30, ent: 40, other: 10 },
    { day: 'T3', edu: 40, ent: 20, other: 15 },
    { day: 'T4', edu: 20, ent: 50, other: 10 },
    { day: 'T5', edu: 45, ent: 15, other: 20 },
    { day: 'T6', edu: 35, ent: 30, other: 15 },
    { day: 'T7', edu: 10, ent: 70, other: 10 },
    { day: 'CN', edu: 5,  ent: 60, other: 15 },
  ];

  const topCategories = [
    { name: 'Học tập & Tra cứu', time: '8h 15m', percent: 45, icon: BookOpen, color: 'var(--cisco-success)' },
    { name: 'Giải trí & Video', time: '5h 30m', percent: 30, icon: Video, color: 'var(--primary-action)' },
    { name: 'Trò chơi', time: '3h 10m', percent: 18, icon: Gamepad2, color: '#f59e0b' },
    { name: 'Mạng xã hội', time: '1h 20m', percent: 7, icon: MessageSquare, color: '#8b5cf6' },
  ];

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.titleWrap}>
          <div className={styles.headerIcon}><BarChart2 size={24} /></div>
          <div>
            <h1 className={styles.title}>Báo cáo hoạt động</h1>
            <p className={styles.subtitle}>Phân tích thói quen sử dụng máy tính của con trong 7 ngày qua.</p>
          </div>
        </div>

        <div className={styles.toolbar}>
          <button className={styles.filterBtn}>
            <Calendar size={16} /> 7 ngày qua
          </button>
          <button className={styles.primaryBtn}>
            <Download size={16} /> Xuất PDF
          </button>
        </div>
      </header>

      {/* 4 Thẻ KPI */}
      <div className={styles.grid4}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}><Clock size={16} color="var(--primary-action)" /> Tổng thời gian</div>
          <div className={styles.kpiValue}>18h 15m</div>
          <div className={`${styles.kpiTrend} ${styles.trendDown}`}>
            <TrendingDown size={14} /> 2.5h so với tuần trước (Tốt)
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}><BookOpen size={16} color="var(--cisco-success)" /> Nội dung học tập</div>
          <div className={styles.kpiValue}>45%</div>
          <div className={`${styles.kpiTrend} ${styles.trendUp}`} style={{ color: 'var(--cisco-success)' }}>
            <TrendingUp size={14} /> Tăng 12% so với tuần trước
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}><AlertTriangle size={16} color="var(--cisco-danger)" /> Nỗ lực truy cập bị chặn</div>
          <div className={styles.kpiValue}>14 lần</div>
          <div className={`${styles.kpiTrend} ${styles.trendDown}`}>
            <TrendingDown size={14} /> Giảm 5 lần so với tuần trước
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}><ShieldCheck size={16} color="#8b5cf6" /> Điểm an toàn</div>
          <div className={styles.kpiValue}>92/100</div>
          <div className={`${styles.kpiTrend} ${styles.trendNeutral}`}>
            Tuyệt vời, thiết bị được bảo vệ tốt!
          </div>
        </div>
      </div>

      {/* Main Charts */}
      <div className={styles.grid2}>

        {/* Biểu đồ phân bổ thời gian */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>Phân bổ thời gian trong tuần</h2>
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--cisco-success)' }}></div> Học tập</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary-action)' }}></div> Giải trí</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: '#cbd5e1' }}></div> Khác</span>
            </div>
          </div>

          <div className={styles.chartArea}>
            {chartData.map((d, i) => (
              <div key={i} className={styles.barCol}>
                <div className={`${styles.barSegment} ${styles.barOther}`} style={{ height: `${d.other}%` }}></div>
                <div className={`${styles.barSegment} ${styles.barEnt}`} style={{ height: `${d.ent}%` }}></div>
                <div className={`${styles.barSegment} ${styles.barEdu}`} style={{ height: `${d.edu}%` }}></div>
                <div className={styles.barLabel}>{d.day}</div>
              </div>
            ))}
          </div>
          <div style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Thời gian cao điểm: <strong>Thứ 7 (8h 30m)</strong>
          </div>
        </div>

        {/* Danh mục hàng đầu */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>Danh mục yêu thích</h2>
          </div>

          <div className={styles.catList}>
            {topCategories.map((cat, i) => {
              const Icon = cat.icon;
              return (
                <div key={i} className={styles.catItem}>
                  <div className={styles.catIcon} style={{ color: cat.color, backgroundColor: `${cat.color}20` }}>
                    <Icon size={18} />
                  </div>
                  <div className={styles.catInfo}>
                    <div className={styles.catNameRow}>
                      <span>{cat.name}</span>
                      <span>{cat.time}</span>
                    </div>
                    <div className={styles.progressTrack}>
                      <div className={styles.progressFill} style={{ width: `${cat.percent}%`, backgroundColor: cat.color }}></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
}
