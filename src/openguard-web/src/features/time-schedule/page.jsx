import { Clock, Calendar, ShieldCheck, ChevronRight, ChevronLeft, Edit2, Info } from 'lucide-react';
import styles from './time.module.css';

export default function TimeSchedulePage() {

  // Dữ liệu giả lập cho biểu đồ tuần (Sử dụng CSS conic-gradient để tạo vòng Donut)
  const weekData = [
    { day: 'Thứ 2', date: '29/09', used: '3h 10m', total: '/ 4h', appP: 50, webP: 20, active: false },
    { day: 'Thứ 3', date: '30/09', used: '2h 45m', total: '/ 4h', appP: 45, webP: 15, active: false },
    { day: 'Thứ 4', date: '01/10', used: '3h 50m', total: '/ 4h', appP: 60, webP: 30, active: false },
    { day: 'Thứ 5', date: '02/10', used: '2h 20m', total: '/ 4h', appP: 40, webP: 10, active: true }, // Ngày hiện tại
    { day: 'Thứ 6', date: '03/10', used: '1h 50m', total: '/ 4h', appP: 30, webP: 10, active: false },
    { day: 'Thứ 7', date: '04/10', used: '4h 0m', total: '/ 4h', appP: 70, webP: 30, active: false },
    { day: 'CN', date: '05/10', used: '2h 30m', total: '/ 4h', appP: 50, webP: 10, active: false },
  ];

  return (
    <div className={styles.container}>

      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerIcon}><Clock size={20} /></div>
        <div>
          <h1 className={styles.title}>Quản lý thời gian và lịch tuần</h1>
          <p className={styles.subtitle}>Đặt giới hạn thời gian sử dụng máy tính, lên lịch theo ngày trong tuần và theo khung giờ cụ thể.</p>
        </div>
      </div>

      {/* 3 Top Cards */}
      <div className={styles.topGrid}>
        {/* Card 1 */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <div className={styles.cardTitleWrap}>
              <Clock size={18} color="var(--primary-action)" /> Tổng thời gian hôm nay
            </div>
            <span className={styles.badge}>Còn 1 giờ 45 phút</span>
          </div>
          <div>
            <span className={styles.timeValue}>2 giờ 15 phút</span>
            <span className={styles.timeLimit}> / 4 giờ</span>
          </div>
          <div className={styles.progressTrack}>
            <div className={styles.progressFill} style={{ width: '56%' }}></div>
          </div>
        </div>

        {/* Card 2 */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <div className={styles.cardTitleWrap}>
              <Calendar size={18} color="#8B5CF6" /> Lịch tuần
            </div>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <div className={styles.timeValue} style={{ fontSize: '1.125rem' }}>Đang áp dụng</div>
            <div className={styles.timeLimit}>Từ Thứ 2 (29/09) đến CN (05/10)</div>
          </div>
          <button className={styles.btnOutline} style={{ width: 'fit-content' }}>
            <Edit2 size={14} /> Chỉnh sửa lịch
          </button>
        </div>

        {/* Card 3 */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <div className={styles.cardTitleWrap}>
              <ShieldCheck size={18} color="var(--cisco-success)" /> Giới hạn theo khung giờ
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flex: 1 }}>
            <div>
              <div className={styles.timeValue} style={{ fontSize: '1.125rem' }}>Đã bật</div>
              <div className={styles.timeLimit}>Tự động khóa khi hết giờ</div>
            </div>
            {/* Toggle Switch mô phỏng */}
            <div className={styles.toggleSwitch}>
              <div className={styles.toggleCircle}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Biểu đồ Lịch sử dụng trong tuần */}
      <div className={styles.chartCard}>
        <div className={styles.chartHeader}>
          <div className={styles.cardTitleWrap} style={{ fontSize: '1rem' }}>
            <Calendar size={18} /> Lịch sử dụng trong tuần
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
            <div className={styles.chartLegend}>
              <div className={styles.legendItem}><div className={styles.dot} style={{ backgroundColor: 'var(--primary-action)' }}></div> Đã sử dụng</div>
              <div className={styles.legendItem}><div className={styles.dot} style={{ backgroundColor: '#e2e8f0' }}></div> Còn lại</div>
              <div className={styles.legendItem}><div className={styles.dot} style={{ backgroundColor: '#F59E0B' }}></div> Ngoài giờ</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-main)', fontWeight: 500 }}>
              <ChevronLeft size={16} cursor="pointer" />
              <Calendar size={14} color="var(--text-muted)" /> 29/09 - 05/10/2025
              <ChevronRight size={16} cursor="pointer" />
            </div>
          </div>
        </div>

        {/* Grid 7 ngày */}
        <div className={styles.weekGrid}>
          {weekData.map((d, i) => (
            <div key={i} className={`${styles.dayColumn} ${d.active ? styles.dayActive : ''}`}>
              <div className={styles.dayName}>{d.day}</div>
              <div className={styles.dayDate}>{d.date}</div>

              {/* Vòng tròn Donut Chart bằng CSS conic-gradient */}
              <div className={styles.donutWrap} style={{
                background: `conic-gradient(var(--primary-action) 0% ${d.appP}%, #8B5CF6 ${d.appP}% ${d.appP + d.webP}%, #e2e8f0 ${d.appP + d.webP}% 100%)`
              }}>
                <div className={styles.donutInner}>
                  <span className={styles.donutVal}>{d.used.split(' ')[0]}</span>
                  <span className={styles.donutTotal}>{d.total}</span>
                </div>
              </div>

              {/* Thông số chi tiết bên dưới vòng tròn */}
              <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}><span style={{ color: 'var(--primary-action)' }}>●</span> Ứng dụng</span>
                  <span style={{ fontWeight: 600 }}>{d.active ? '2h 30m' : '1h 20m'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}><span style={{ color: '#8B5CF6' }}>●</span> Website</span>
                  <span style={{ fontWeight: 600 }}>{d.active ? '50m' : '30m'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Khu vực Cài đặt bên dưới */}
      <div className={styles.bottomGrid}>

        {/* Box trái: Thiết lập */}
        <div className={styles.card}>
          <div className={styles.cardTitleWrap} style={{ fontSize: '1rem', marginBottom: '1.5rem' }}>
            Thiết lập hạn mức thời gian
          </div>

          <div className={styles.settingGroup}>
            <div className={styles.settingLabel}>Thời gian sử dụng mỗi ngày</div>
            <div className={styles.inputRow}>
              <input type="number" defaultValue={4} className={styles.timeInput} />
              <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>giờ</span>
              <button className={styles.btnPrimary} style={{ marginLeft: 'auto' }}>Lưu thay đổi</button>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', gap: '0.375rem', alignItems: 'center' }}>
              <Info size={14} /> Thay đổi sẽ có hiệu lực từ ngày mai.
            </div>
          </div>

          <div className={styles.settingGroup} style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.5rem' }}>
            <div className={styles.settingLabel} style={{ marginBottom: '0.5rem' }}>Khung giờ cho phép</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <Clock size={20} color="var(--primary-action)" />
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Thời gian cho phép trong ngày</div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>07:00 - 21:00 <span className={styles.badge} style={{ marginLeft: '0.5rem' }}>Đang áp dụng</span></div>
                </div>
              </div>
              <button className={styles.btnOutline}><Edit2 size={14} /> Chỉnh sửa</button>
            </div>
          </div>
        </div>

        {/* Box phải: Bảng lịch chi tiết */}
        <div className={styles.card}>
          <div className={styles.cardHeader} style={{ marginBottom: '0.5rem' }}>
            <div className={styles.cardTitleWrap} style={{ fontSize: '1rem' }}>Lịch chi tiết trong tuần</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Hiển thị theo khung giờ
              <div className={styles.toggleSwitch} style={{ width: '2rem', height: '1rem' }}>
                <div className={styles.toggleCircle} style={{ width: '0.75rem', height: '0.75rem', top: '2px', right: '2px' }}></div>
              </div>
            </div>
          </div>

          <table className={styles.scheduleTable}>
            <thead>
              <tr>
                <th>Ngày</th>
                <th>Thời gian cho phép</th>
                <th>Ghi chú</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6'].map(day => (
                <tr key={day}>
                  <td style={{ fontWeight: 500 }}>{day}</td>
                  <td>07:00 - 21:00</td>
                  <td style={{ color: 'var(--text-muted)' }}>Học và giải trí</td>
                  <td style={{ textAlign: 'right' }}><Edit2 size={14} color="var(--primary-action)" cursor="pointer" /></td>
                </tr>
              ))}
              <tr>
                <td style={{ fontWeight: 500, color: 'var(--primary-action)' }}>Thứ 7</td>
                <td>08:00 - 22:00</td>
                <td style={{ color: 'var(--text-muted)' }}>Cuối tuần</td>
                <td style={{ textAlign: 'right' }}><Edit2 size={14} color="var(--primary-action)" cursor="pointer" /></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 500, color: 'var(--cisco-danger)' }}>CN</td>
                <td>08:00 - 21:00</td>
                <td style={{ color: 'var(--text-muted)' }}>Nghỉ ngơi</td>
                <td style={{ textAlign: 'right' }}><Edit2 size={14} color="var(--primary-action)" cursor="pointer" /></td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
}
