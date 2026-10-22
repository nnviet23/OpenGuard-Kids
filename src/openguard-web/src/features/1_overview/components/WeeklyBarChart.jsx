import { useState } from 'react';
import styles from './WeeklyBarChart.module.css';

const DEFAULT_DAYS = [
  {
    day: 'T2',
    fullName: 'Thứ Hai',
    totalShort: '2h00',
    studyPercent: 75,
    studyTime: '1h30m',
    leisurePercent: 25,
    leisureTime: '30m',
    barStudy: 50,
    barLeisure: 15,
  },
  {
    day: 'T3',
    fullName: 'Thứ Ba',
    totalShort: '2h48',
    studyPercent: 71,
    studyTime: '2h00',
    leisurePercent: 29,
    leisureTime: '48m',
    barStudy: 60,
    barLeisure: 25,
  },
  {
    day: 'T4',
    fullName: 'Thứ Tư',
    totalShort: '2h00',
    studyPercent: 83,
    studyTime: '1h40m',
    leisurePercent: 17,
    leisureTime: '20m',
    barStudy: 55,
    barLeisure: 10,
  },
  {
    day: 'T5',
    fullName: 'Thứ Năm (Hôm nay)',
    totalShort: '1h45m',
    studyPercent: 67,
    studyTime: '1h10m',
    leisurePercent: 33,
    leisureTime: '35m',
    barStudy: 40,
    barLeisure: 18,
  },
  {
    day: 'T6',
    fullName: 'Thứ Sáu',
    totalShort: '0h00',
    studyPercent: 0,
    studyTime: '0m',
    leisurePercent: 0,
    leisureTime: '0m',
    barStudy: 0,
    barLeisure: 0,
  },
  {
    day: 'T7',
    fullName: 'Thứ Bảy',
    totalShort: '0h00',
    studyPercent: 0,
    studyTime: '0m',
    leisurePercent: 0,
    leisureTime: '0m',
    barStudy: 0,
    barLeisure: 0,
  },
  {
    day: 'CN',
    fullName: 'Chủ Nhật',
    totalShort: '0h00',
    studyPercent: 0,
    studyTime: '0m',
    leisurePercent: 0,
    leisureTime: '0m',
    barStudy: 0,
    barLeisure: 0,
  },
];

export default function WeeklyBarChart({ onSelectDay }) {
  const [selectedDayKey, setSelectedDayKey] = useState('T5');
  const selectedDay = DEFAULT_DAYS.find((d) => d.day === selectedDayKey) || DEFAULT_DAYS[3];

  const handleDayClick = (dayItem) => {
    setSelectedDayKey(dayItem.day);
    if (onSelectDay) {
      onSelectDay(dayItem);
    }
  };

  return (
    <div className={styles.container}>
      {/* 7 thanh biểu đồ cột */}
      <div className={styles.barsSection}>
        <div className={styles.chartWrap}>
          {DEFAULT_DAYS.map((item) => {
            const isSelected = item.day === selectedDayKey;
            return (
              <div
                key={item.day}
                className={styles.col}
                onClick={() => handleDayClick(item)}
                title={`${item.fullName}: Bấm để xem chi tiết`}
              >
                <div className={`${styles.track} ${isSelected ? styles.selectedTrack : ''}`}>
                  <div className={styles.fillStudy} style={{ height: `${item.barStudy}%` }} />
                  <div className={styles.fillLeisure} style={{ height: `${item.barLeisure}%` }} />
                </div>
                <span className={`${styles.dayLabel} ${isSelected ? styles.selectedLabel : ''}`}>
                  {item.day}
                </span>
              </div>
            );
          })}
        </div>

        <span className={styles.hintText}>💡 Bấm vào cột để xem chi tiết ngày</span>
      </div>

      {/* Cột chú thích danh mục, % và tổng giờ như bên Pie Chart */}
      <div className={styles.summaryPanel}>
        <div className={styles.dayHeader}>
          <span className={styles.dayTitle}>📅 {selectedDay.fullName}</span>
          <div className={styles.sumBadgeBox}>
            <span className={styles.timeSum}>{selectedDay.totalShort}</span>
            <span className={styles.labelSub}>Tổng dùng</span>
          </div>
        </div>

        <div className={styles.list}>
          <div className={styles.row}>
            <span className={styles.chip}>
              <span className={styles.colorBox} style={{ background: 'var(--chart-study)' }} />
              Giáo dục
            </span>
            <div className={styles.metaGroup}>
              <span className={styles.durationTxt}>{selectedDay.studyTime}</span>
              <strong className={styles.percentTxt}>{selectedDay.studyPercent}%</strong>
            </div>
          </div>

          <div className={styles.row}>
            <span className={styles.chip}>
              <span className={styles.colorBox} style={{ background: 'var(--chart-leisure)' }} />
              Giải trí
            </span>
            <div className={styles.metaGroup}>
              <span className={styles.durationTxt}>{selectedDay.leisureTime}</span>
              <strong className={styles.percentTxt}>{selectedDay.leisurePercent}%</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}