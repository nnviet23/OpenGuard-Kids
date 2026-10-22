import React, { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import styles from './SchedulePage.module.css';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import TimeMatrix7x48 from './components/TimeMatrix7x48';

export default function SchedulePage() {
  const { selectedChild } = useOutletContext();
  const [weekdayQuota, setWeekdayQuota] = useState('02:00');
  const [weekendQuota, setWeekendQuota] = useState('03:30');
  const [scheduleMatrixState, setScheduleMatrixState] = useState(null);

  const handleSavePolicy = () => {
    alert(
      `[OpenGuard API] Đã đóng gói chính sách mới:\n- Target: ${selectedChild}\n- Quota ngày thường: ${weekdayQuota}\n- Quota cuối tuần: ${weekendQuota}\n- Ma trận 7x48 đã ký HMAC SHA-256.\nAgent sẽ nhận cấu hình trong vòng tối đa 60 giây.`
    );
  };

  const handleReset = () => {
    setWeekdayQuota('02:00');
    setWeekendQuota('03:30');
    alert('Đã khôi phục các giá trị mặc định.');
  };

  return (
    <div>
      <div className={styles.pageHeader}>
        <div>
          <h2 className={styles.heading}>Cấu hình lịch tuần & Hạn mức Quota</h2>
          <p className={styles.subheading}>
            Độ phân giải 30 phút. Ngoài khung giờ xanh hoặc vượt quota, agent sẽ khóa máy trong 5 giây.
          </p>
        </div>
        <div className={styles.actionControls}>
          <Button variant="secondary" onClick={handleReset}>
            Khôi phục mặc định
          </Button>
          <Button variant="primary" onClick={handleSavePolicy}>
            Lưu & Đẩy xuống Agent
          </Button>
        </div>
      </div>

      <div className={styles.quotaGrid}>
        <Card className={styles.quotaCard}>
          <span className={styles.kpiTitle}>Quota ngày thường (T2 - T6)</span>
          <div className={styles.quotaInputGroup}>
            <input
              type="text"
              className={styles.quotaInput}
              value={weekdayQuota}
              onChange={(e) => setWeekdayQuota(e.target.value)}
            />
            <span className={styles.quotaUnit}>giờ / ngày</span>
          </div>
          <span className={styles.quotaNote}>Không tính khi máy Sleep / Khóa</span>
        </Card>

        <Card className={styles.quotaCard}>
          <span className={styles.kpiTitle}>Quota cuối tuần (T7 - CN)</span>
          <div className={styles.quotaInputGroup}>
            <input
              type="text"
              className={styles.quotaInput}
              value={weekendQuota}
              onChange={(e) => setWeekendQuota(e.target.value)}
            />
            <span className={styles.quotaUnit}>giờ / ngày</span>
          </div>
          <span className={styles.quotaNote}>Cho phép thêm thời gian thư giãn</span>
        </Card>

        <Card className={styles.ruleBox}>
          <div className={styles.ruleTitle}>🛡️ Quy định bảo vệ & ân hạn bài học</div>
          <div className={styles.ruleDesc}>
            • Cảnh báo trước: <strong>10 phút, 5 phút, 1 phút</strong><br />
            • Khoảng ân hạn: <strong>60 giây</strong> trước khi khóa để trẻ kịp lưu bài.
          </div>
        </Card>
      </div>

      <Card>
        <TimeMatrix7x48 onMatrixChange={setScheduleMatrixState} />
      </Card>
    </div>
  );
}