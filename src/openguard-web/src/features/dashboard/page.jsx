import { Clock, LayoutGrid, Globe, ShieldCheck, ChevronRight, Monitor, ArrowRight } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell
} from 'recharts';
import styles from './dashboard.module.css';

// --- DỮ LIỆU MÔ PHỎNG CHO BIỂU ĐỒ ---
const barData = [
  { name: 'T2', hocTap: 2.5, giaiTri: 1.0, khac: 0.5 },
  { name: 'T3', hocTap: 3.0, giaiTri: 1.5, khac: 0.5 },
  { name: 'T4', hocTap: 2.0, giaiTri: 2.0, khac: 1.0 },
  { name: 'T5', hocTap: 2.5, giaiTri: 1.0, khac: 0.5 },
  { name: 'T6', hocTap: 1.5, giaiTri: 2.5, khac: 1.0 },
  { name: 'T7', hocTap: 1.0, giaiTri: 3.5, khac: 1.5 },
  { name: 'CN', hocTap: 0.5, giaiTri: 4.0, khac: 1.5 },
];

const pieData = [
  { name: 'Microsoft Edge', value: 32 },
  { name: 'YouTube', value: 21 },
  { name: 'Google Chrome', value: 15 },
  { name: 'Zalo', value: 12 },
  { name: 'Khác', value: 20 },
];

// Bộ màu cho Pie Chart
const COLORS = ['#054b85', '#8B5CF6', '#0fa397', '#F59E0B', '#cbd5e1'];

export default function DashboardPage() {
  const metrics = [
    {
      title: "Tổng thời gian sử dụng", value: "2 giờ 15 phút",
      sub: "Trong giới hạn 3 giờ", subClass: styles.metricSubHighlight,
      icon: Clock, colorClass: styles.iconBlue
    },
    {
      title: "Ứng dụng đã dùng", value: "12 ứng dụng",
      sub: "Trong đó 2 ứng dụng bị giới hạn", subClass: '',
      icon: LayoutGrid, colorClass: styles.iconPurple
    },
    {
      title: "Website đã truy cập", value: "8 trang web",
      sub: "Không có trang bị chặn", subClass: '',
      icon: Globe, colorClass: styles.iconGreen
    },
    {
      title: "Trạng thái thiết bị", value: "Được bảo vệ",
      sub: "Windows 11 - Agent online", subClass: '',
      icon: ShieldCheck, colorClass: styles.iconYellow
    }
  ];

  const topApps = [
    { name: 'Microsoft Edge', time: '1h 05m', percent: 45 },
    { name: 'YouTube', time: '45m', percent: 30 },
    { name: 'Google Chrome', time: '32m', percent: 20 },
    { name: 'Word', time: '18m', percent: 15 },
  ];

  // Custom Tooltip cho Bar Chart để bo góc và format đẹp hơn
    const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ backgroundColor: '#fff', padding: '10px', border: '1px solid var(--border-subtle)', borderRadius: '8px', boxShadow: 'var(--shadow-md)', fontSize: '0.8125rem' }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: 600, color: 'var(--text-main)' }}>{label} (Giờ)</p>
          {payload.map((entry, index) => (
            <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: entry.color }}></div>
              <span style={{ color: 'var(--text-muted)' }}>{entry.name}:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{entry.value}h</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={styles.container}>

      {/* Header gọn gàng */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
        <div style={{ width: '2.5rem', height: '2.5rem', backgroundColor: 'var(--primary-action)', color: '#fff', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <LayoutGrid size={24} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.25rem 0', color: 'var(--text-main)' }}>Tổng quan hệ thống</h1>
          <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-muted)' }}>Giám sát tình hình sử dụng thiết bị và sự an toàn của con.</p>
        </div>
      </div>

      {/* 4 Thẻ Metrics */}
      <div className={styles.metricsGrid}>
        {metrics.map((metric, idx) => {
          const Icon = metric.icon;
          return (
            <div key={idx} className={styles.metricCard}>
              <div className={styles.metricHeader}>
                <div className={`${styles.iconWrapper} ${metric.colorClass}`}>
                  <Icon size={18} />
                </div>
                <ChevronRight size={16} className={styles.metricArrow} />
              </div>
              <div style={{ flex: 1 }}>
                <div className={styles.metricTitle}>{metric.title}</div>
                <div className={styles.metricValue}>{metric.value}</div>
              </div>
              <div className={`${styles.metricSub} ${metric.subClass}`}>
                {metric.sub}
              </div>
            </div>
          );
        })}
      </div>

      {/* Khu vực Biểu đồ Recharts */}
      <div className={styles.rowGrid}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Thời gian sử dụng trong tuần</h3>
          </div>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-subtle)" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />

                {/* 3. SỬA CÁCH TRUYỀN CONTENT TẠI ĐÂY */}
                <RechartsTooltip content={CustomTooltip} cursor={{ fill: 'transparent' }} />

                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="hocTap" name="Ứng dụng học tập" stackId="a" fill="var(--primary-action)" radius={[0, 0, 4, 4]} barSize={24} />
                <Bar dataKey="giaiTri" name="Giải trí" stackId="a" fill="#8B5CF6" />
                <Bar dataKey="khac" name="Khác" stackId="a" fill="#e2e8f0" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cột 2: Pie (Donut) Chart */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Tỷ lệ ứng dụng</h3>
          </div>
          <div style={{ width: '100%', height: 260, position: 'relative' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="40%" /* Đẩy biểu đồ sang trái một chút để chừa chỗ cho Legend */
                  cy="50%"
                  innerRadius={70}
                  outerRadius={95}
                  paddingAngle={2}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-md)', fontSize: '0.8125rem' }}
                  itemStyle={{ color: 'var(--text-main)', fontWeight: 600 }}
                />
                <Legend
                  layout="vertical"
                  verticalAlign="middle"
                  align="right"
                  iconType="circle"
                  wrapperStyle={{ fontSize: '12px', color: 'var(--text-main)', lineHeight: '24px' }}
                />
              </PieChart>
            </ResponsiveContainer>

            {/* Chữ hiển thị ở giữa Donut Chart */}
            <div style={{ position: 'absolute', top: '50%', left: '40%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', lineHeight: 1.2 }}>2h 15m</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>hôm nay</div>
            </div>
          </div>
        </div>

      </div>

      {/* Danh sách ứng dụng và Hoạt động */}
      <div className={styles.rowGrid}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Ứng dụng sử dụng nhiều</h3>
            <a href="#" className={styles.cardLink}>Xem tất cả →</a>
          </div>
          <div>
            {topApps.map((app, idx) => (
              <div key={idx} className={styles.listItem}>
                <div className={styles.listIndex}>{idx + 1}</div>
                <div className={styles.listIcon}>{app.name.substring(0, 1)}</div>
                <div className={styles.listName}>{app.name}</div>
                <div className={styles.listValue}>{app.time}</div>
                <div className={styles.progressTrack}>
                  <div className={styles.progressFill} style={{ width: `${app.percent}%`, backgroundColor: idx === 1 ? '#8B5CF6' : idx === 2 ? '#0fa397' : 'var(--primary-action)' }}></div>
                </div>
                <ArrowRight size={14} color="var(--text-muted)" style={{ marginLeft: '0.5rem' }} />
              </div>
            ))}
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Hoạt động gần đây</h3>
            <a href="#" className={styles.cardLink}>Xem tất cả →</a>
          </div>
          <div>
            {[
              { time: '14:32', name: 'Microsoft Edge', action: 'Truy cập', color: 'var(--cisco-success)' },
              { time: '14:20', name: 'YouTube', action: 'Truy cập', color: 'var(--cisco-success)' },
              { time: '11:42', name: 'TikTok', action: 'Bị chặn', color: 'var(--cisco-danger)' },
            ].map((log, idx) => (
              <div key={idx} className={styles.listItem}>
                <div className={styles.listValue} style={{ width: '3rem' }}>{log.time}</div>
                <div className={styles.listIcon} style={{ background: 'transparent' }}><Monitor size={16} color="var(--text-muted)" /></div>
                <div className={styles.listName}>{log.name}</div>
                <div style={{ fontSize: '0.75rem', fontWeight: 500, color: log.color }}>{log.action}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
