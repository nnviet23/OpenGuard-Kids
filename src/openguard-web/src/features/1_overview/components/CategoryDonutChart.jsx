import styles from './CategoryDonutChart.module.css';

export default function CategoryDonutChart({ totalTime = '1h 45m' }) {
  // 6 danh mục chuẩn (tổng = 100% thời lượng sử dụng thực tế)
  const categories = [
    {
      name: 'Giáo dục',
      percent: 52,
      duration: '55 phút',
      color: 'var(--chart-study)',
      dashArray: '52 48',
      dashOffset: 25,
      blockedText: null,
    },
    {
      name: 'Cổng Thông tin Điện tử',
      percent: 18,
      duration: '19 phút',
      color: 'var(--chart-portal)',
      dashArray: '18 82',
      dashOffset: 73,
      blockedText: 'Miễn chặn',
    },
    {
      name: 'Giải trí',
      percent: 18,
      duration: '19 phút',
      color: 'var(--chart-leisure)',
      dashArray: '18 82',
      dashOffset: 55,
      blockedText: null,
    },
    {
      name: 'Mạng xã hội',
      percent: 7,
      duration: '7 phút',
      color: 'var(--chart-social)',
      dashArray: '7 93',
      dashOffset: 37,
      blockedText: 'Chặn 1 lượt',
    },
    {
      name: 'Trò chơi',
      percent: 5,
      duration: '5 phút',
      color: 'var(--chart-games)',
      dashArray: '5 95',
      dashOffset: 30,
      blockedText: 'Chặn 1 lượt',
    },
    {
      name: 'Nội dung không phù hợp',
      percent: 0, // Luôn bằng 0% theo yêu cầu
      duration: '0 phút',
      color: 'var(--chart-inappropriate)',
      dashArray: '0 100',
      dashOffset: 25,
      blockedText: 'Luôn chặn 100%',
    },
  ];

  return (
    <div className={styles.container}>
      {/* SVG Donut */}
      <div className={styles.svgBox}>
        <svg width="100%" height="100%" viewBox="0 0 42 42">
          <circle cx="21" cy="21" r="15.9155" fill="transparent" stroke="#f1f5f9" strokeWidth="5" />
          
          {categories
            .filter((c) => c.percent > 0)
            .map((c) => (
              <circle
                key={c.name}
                cx="21"
                cy="21"
                r="15.9155"
                fill="transparent"
                stroke={c.color}
                strokeWidth="5"
                strokeDasharray={c.dashArray}
                strokeDashoffset={c.dashOffset}
              />
            ))}
        </svg>

        <div className={styles.innerContent}>
          <span className={styles.timeSum}>{totalTime}</span>
          <span className={styles.labelSub}>Tổng dùng</span>
        </div>
      </div>

      {/* Danh sách 6 nhóm phân loại */}
      <div className={styles.list}>
        {categories.map((c) => (
          <div key={c.name} className={styles.row}>
            <span className={styles.chip}>
              <span className={styles.colorBox} style={{ background: c.color }} />
              {c.name}
            </span>

            <div className={styles.metaGroup}>
              {c.blockedText && (
                <span className={styles.blockedBadge}>{c.blockedText}</span>
              )}
              <span 
                className={styles.percentTxt}
                style={c.percent === 0 ? { color: 'var(--text-sub)' } : {}}
              >
                {c.percent}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}