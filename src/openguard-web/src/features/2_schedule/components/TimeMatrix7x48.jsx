import React, { useState, useEffect } from 'react';
import styles from './TimeMatrix7x48.module.css';
import Button from '../../../components/common/Button';

const DAYS = [
  { id: 'mon', name: 'Thứ 2' },
  { id: 'tue', name: 'Thứ 3' },
  { id: 'wed', name: 'Thứ 4' },
  { id: 'thu', name: 'Thứ 5' },
  { id: 'fri', name: 'Thứ 6' },
  { id: 'sat', name: 'Thứ 7' },
  { id: 'sun', name: 'Chủ nhật' },
];

export default function TimeMatrix7x48({ onMatrixChange }) {
  const [currentBrush, setCurrentBrush] = useState('allow');
  const [isMouseDown, setIsMouseDown] = useState(false);

  const initDefaultMatrix = () => {
    const initial = {};
    DAYS.forEach((day) => {
      initial[day.id] = new Array(48).fill(false);
      for (let s = 14; s <= 41; s++) {
        initial[day.id][s] = true;
      }
    });
    return initial;
  };

  const [matrixData, setMatrixData] = useState(initDefaultMatrix);

  useEffect(() => {
    const handleMouseUp = () => setIsMouseDown(false);
    window.addEventListener('mouseup', handleMouseUp);
    return () => window.removeEventListener('mouseup', handleMouseUp);
  }, []);

  const handleCellPaint = (dayId, slot) => {
    const targetState = currentBrush === 'allow';
    setMatrixData((prev) => {
      const updatedDay = [...prev[dayId]];
      updatedDay[slot] = targetState;
      const nextData = { ...prev, [dayId]: updatedDay };
      if (onMatrixChange) onMatrixChange(nextData);
      return nextData;
    });
  };

  const applyNightLock = () => {
    setMatrixData((prev) => {
      const nextData = {};
      DAYS.forEach((day) => {
        const slots = [...prev[day.id]];
        for (let s = 0; s < 12; s++) slots[s] = false;
        for (let s = 44; s < 48; s++) slots[s] = false;
        nextData[day.id] = slots;
      });
      if (onMatrixChange) onMatrixChange(nextData);
      return nextData;
    });
  };

  const applySchoolHours = () => {
    setMatrixData(() => {
      const nextData = {};
      DAYS.forEach((day) => {
        const slots = new Array(48).fill(false);
        for (let s = 16; s < 34; s++) slots[s] = true;
        nextData[day.id] = slots;
      });
      if (onMatrixChange) onMatrixChange(nextData);
      return nextData;
    });
  };

  const clearAll = () => {
    setMatrixData(() => {
      const nextData = {};
      DAYS.forEach((day) => {
        nextData[day.id] = new Array(48).fill(false);
      });
      if (onMatrixChange) onMatrixChange(nextData);
      return nextData;
    });
  };

  return (
    <div className={styles.matrixCard}>
      <div className={styles.controlsBar}>
        <div className={styles.brushTools}>
          <span className={styles.brushLabel}>Công cụ vẽ:</span>
          <button
            type="button"
            className={`${styles.brushBtn} ${currentBrush === 'allow' ? styles.activeAllow : ''}`}
            onClick={() => setCurrentBrush('allow')}
          >
            <span className={styles.brushIndicator} style={{ background: 'var(--color-primary)' }} />
            Cho phép dùng (Xanh)
          </button>
          <button
            type="button"
            className={`${styles.brushBtn} ${currentBrush === 'block' ? styles.activeBlock : ''}`}
            onClick={() => setCurrentBrush('block')}
          >
            <span className={styles.brushIndicator} style={{ background: '#cbd5e1' }} />
            Khóa máy (Xám)
          </button>
        </div>

        <div className={styles.presetGroup}>
          <span className={styles.brushLabel}>Mẫu nhanh:</span>
          <Button variant="secondary" size="sm" onClick={applyNightLock}>
            🌙 Khóa đêm (22h - 6h)
          </Button>
          <Button variant="secondary" size="sm" onClick={applySchoolHours}>
            🎒 Giờ học (8h - 17h)
          </Button>
          <Button variant="secondary" size="sm" onClick={clearAll}>
            ✕ Xóa hết
          </Button>
        </div>
      </div>

      <table className={styles.matrixTable}>
        <thead>
          <tr className={styles.headerTime}>
            <th className={styles.dayLabel} style={{ textAlign: 'left' }}>NGÀY</th>
            {Array.from({ length: 24 }).map((_, h) => {
              const hStr = h < 10 ? `0${h}` : `${h}`;
              return <th key={h} colSpan={2}>{hStr}h</th>;
            })}
            <th className={styles.daySum}>TỔNG MỞ</th>
          </tr>
        </thead>
        <tbody>
          {DAYS.map((day) => {
            const slots = matrixData[day.id] || [];
            const allowedSlotsCount = slots.filter(Boolean).length;
            const hoursTotal = (allowedSlotsCount * 0.5).toFixed(1);

            return (
              <tr key={day.id}>
                <td className={styles.dayLabel}>{day.name}</td>
                {slots.map((isAllowed, slot) => {
                  const h = Math.floor(slot / 2);
                  const m = slot % 2 === 0 ? '00' : '30';
                  const nextH = Math.floor((slot + 1) / 2);
                  const nextM = (slot + 1) % 2 === 0 ? '00' : '30';
                  const title = `${day.name}: ${h < 10 ? '0' + h : h}:${m} - ${nextH < 10 ? '0' + nextH : nextH}:${nextM}`;

                  return (
                    <td
                      key={slot}
                      className={`${styles.cell} ${isAllowed ? styles.allowed : styles.blocked} ${slot % 2 === 1 ? styles.hourBoundary : ''}`}
                      title={title}
                      onMouseDown={(e) => {
                        e.preventDefault();
                        setIsMouseDown(true);
                        handleCellPaint(day.id, slot);
                      }}
                      onMouseEnter={() => {
                        if (isMouseDown) {
                          handleCellPaint(day.id, slot);
                        }
                      }}
                    />
                  );
                })}
                <td className={styles.daySum}>{hoursTotal}h mở</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <div className={styles.footerNotes}>
        <span>💡 Nhấn giữ chuột và kéo qua các ô để quét nhanh nhiều khung giờ.</span>
        <span>HMAC Signed Policy • Chống can thiệp lùi giờ hệ thống</span>
      </div>
    </div>
  );
}