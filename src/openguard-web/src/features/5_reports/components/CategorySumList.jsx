import styles from './CategorySumList.module.css';

const DEFAULT_BREAKDOWN = [
  { id: 'edu', name: 'Học tập & Giáo dục', duration: '7h 15m', percent: 57, color: 'var(--chart-study)' },
  { id: 'lei', name: 'Giải trí phù hợp', duration: '3h 50m', percent: 30, color: 'var(--chart-leisure)' },
  { id: 'soc', name: 'Mạng xã hội', duration: '1h 10m', percent: 9, color: 'var(--chart-social)' },
  { id: 'blk', name: 'Trò chơi & Bị chặn', duration: '30m', percent: 4, color: 'var(--chart-blocked)', isDanger: true },
];

export default function CategorySumList({ items = DEFAULT_BREAKDOWN }) {
  return (
    <div className={styles.card}>
      {items.map((item) => (
        <div key={item.id} className={styles.row}>
          <div className={styles.meta}>
            <span className={styles.labelGroup}>
              <span className={styles.chipColor} style={{ background: item.color }} />
              {item.name}
            </span>
            <span 
              className={styles.timeVal} 
              style={item.isDanger ? { color: 'var(--color-danger)' } : {}}
            >
              {item.duration} ({item.percent}%)
            </span>
          </div>
          <div className={styles.barTrack}>
            <div 
              className={styles.barFill} 
              style={{ width: `${item.percent}%`, background: item.color }} 
            />
          </div>
        </div>
      ))}

      <div className={styles.adviceBox}>
        💡 <strong>Đánh giá tuần:</strong> Bé dành 57% thời gian cho ứng dụng học tập, lịch sinh hoạt cân đối và lành mạnh.
      </div>
    </div>
  );
}