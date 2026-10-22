import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import styles from './ReportsPage.module.css';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import CategorySumList from './components/CategorySumList';
import { 
  IconDownload, 
  IconPrint, 
  IconClock, 
  IconCheck, 
  IconAlert 
} from '../../components/icons/PixelIcons';

const WEEK_BARS = [
  { day: 'T2', study: 60, leisure: 20, hours: '2.2h' },
  { day: 'T3', study: 55, leisure: 20, hours: '2.0h' },
  { day: 'T4', study: 65, leisure: 15, hours: '2.4h' },
  { day: 'T5', study: 45, leisure: 20, hours: '1.8h' },
  { day: 'T6', study: 40, leisure: 20, hours: '1.6h' },
  { day: 'T7', study: 35, leisure: 55, hours: '3.2h' },
  { day: 'CN', study: 30, leisure: 50, hours: '2.8h' },
];

export default function ReportsPage() {
  const { selectedChild } = useOutletContext();
  const [activeTab, setActiveTab] = useState('top-apps');

  const handleExportCSV = () => {
    const csvContent = 
`BÁO CÁO HOẠT ĐỘNG SỬ DỤNG MÁY TÍNH - OPENGUARD KIDS
Thiết bị / Trẻ: ${selectedChild}
Kỳ báo cáo: 12/10/2026 - 18/10/2026
Nguyên tắc: Tối thiểu dữ liệu NT2 (Chỉ lưu Domain cấp 2 & Metadata tiến trình)

# THỐNG KÊ TỔNG HỢP THEO LOẠI
Loại danh mục,Thời lượng (phút),Tỷ lệ (%)
Học tập & Giáo dục,435,57%
Giải trí phù hợp,230,30%
Mạng xã hội,70,9%
Trò chơi & Bị chặn,30,4%

# TOP ỨNG DỤNG (APPS)
Tiến trình,Danh mục,Thời lượng (phút),Trạng thái
chrome.exe,Trình duyệt học tập,315,Cho phép
Code.exe,Học lập trình,165,Cho phép
msedge.exe,Học trực tuyến,90,Cho phép
WINWORD.EXE,Soạn thảo,70,Cho phép
Spotify.exe,Âm nhạc,50,Cho phép
RobloxPlayerBeta.exe,Trò chơi,0,Đã ngắt tiến trình

# SỰ KIỆN VI PHẠM BỊ NGĂN CHẶN
Dấu thời gian,Tầng lọc,Đối tượng,Hành động
2026-10-18 16:30:12,DNS,roblox.com,Trả NXDOMAIN (NT4 Lý do rõ ràng)
2026-10-17 21:05:44,Process,RobloxPlayerBeta.exe,Terminated (Khớp SHA-256)
2026-10-16 22:15:00,Screen-time,Khóa đêm,Khóa màn hình máy tính
`;

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `OpenGuard_Report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportPDF = () => {
    window.print();
  };

  return (
    <div>
      <div className={styles.toolbar}>
        <div>
          <h2 className={styles.heading}>Báo cáo hoạt động & Tuân thủ</h2>
          <p className={styles.subheading}>
            Số liệu thời gian thực được tổng hợp trong vòng 90 ngày theo Nghị định 13/2023.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className={styles.dateBadge}>
            📅 12/10/2026 - 18/10/2026
          </div>
          <Button variant="secondary" icon={<IconDownload />} onClick={handleExportCSV}>
            Xuất file CSV
          </Button>
          <Button variant="primary" icon={<IconPrint />} onClick={handleExportPDF}>
            Xuất báo cáo PDF
          </Button>
        </div>
      </div>

      <div className={styles.kpiRow}>
        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Tổng thời gian tuần</span>
            <IconClock color="var(--color-primary)" />
          </div>
          <div className={styles.kpiNum}>12h 45m</div>
          <div className={styles.kpiBottom}>
            Hạn mức tuần: <strong>17h 00m</strong> (75%)
          </div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Trung bình mỗi ngày</span>
            <IconCheck color="var(--color-primary)" />
          </div>
          <div className={styles.kpiNum}>1h 49m</div>
          <div className={styles.kpiBottom}>
            Nằm trong ngưỡng an toàn độ tuổi
          </div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Quy tắc nghỉ mắt 20-20-20</span>
            <IconCheck color="var(--color-success)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-success)' }}>
            28 / 32 lần
          </div>
          <div className={styles.kpiBottom}>
            Trẻ tuân thủ tạm dừng nhìn màn hình
          </div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Tổng lần bị chặn</span>
            <IconAlert color="var(--color-danger)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-danger)' }}>
            09 lần
          </div>
          <div className={styles.kpiBottom}>
            7 chặn DNS • 2 ngắt Process
          </div>
        </Card>
      </div>

      <div className={styles.chartsGrid}>
        <Card
          title="Thời lượng sử dụng thực tế trong tuần"
          caption="Tính bằng Active-Time (không tính khi máy Sleep/Khóa)"
          action={
            <div className={styles.chartLegend}>
              <div className={styles.legendChip}>
                <span className={styles.chipColor} style={{ background: 'var(--chart-study)' }} /> Học tập
              </div>
              <div className={styles.legendChip}>
                <span className={styles.chipColor} style={{ background: 'var(--chart-leisure)' }} /> Giải trí
              </div>
            </div>
          }
        >
          <div className={styles.barChartWrap}>
            {WEEK_BARS.map((item) => (
              <div key={item.day} className={styles.barCol}>
                <div className={styles.barTrack} title={`${item.day}: ${item.hours}`}>
                  <div className={styles.fillStudy} style={{ height: `${item.study}%` }} />
                  <div className={styles.fillLeisure} style={{ height: `${item.leisure}%` }} />
                </div>
                <span className={styles.dayLabel}>{item.day}</span>
              </div>
            ))}
          </div>
          <div className={styles.chartFooter}>
            Sai số bộ đếm: <strong>≤ ±30s / giờ</strong> (Đạt tiêu chuẩn F1)
          </div>
        </Card>

        <Card
          title="Tổng thời lượng theo Loại ứng dụng"
          caption="Sum(duration_sec) phân theo danh mục"
        >
          <CategorySumList />
        </Card>
      </div>

      <Card>
        <div className={styles.tabsHeader}>
          <button
            type="button"
            className={`${styles.tabBtn} ${activeTab === 'top-apps' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('top-apps')}
          >
            Top 10 Ứng Dụng (Apps)
          </button>
          <button
            type="button"
            className={`${styles.tabBtn} ${activeTab === 'top-domains' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('top-domains')}
          >
            Top 10 Tên Miền (Domains)
          </button>
          <button
            type="button"
            className={`${styles.tabBtn} ${activeTab === 'blocked-logs' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('blocked-logs')}
          >
            Nhật Ký Ngăn Chặn (Blocked Events)
          </button>
        </div>

        {activeTab === 'top-apps' && (
          <div className="table-container">
            <table className="data-table-box">
              <thead>
                <tr>
                  <th style={{ width: 50 }}>#</th>
                  <th>Tên tiến trình ứng dụng</th>
                  <th style={{ width: 150 }}>Loại danh mục</th>
                  <th style={{ width: 150 }}>Thời lượng</th>
                  <th style={{ width: 120 }}>Tỷ lệ</th>
                  <th style={{ width: 140 }}>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className={styles.monoCol}>01</td>
                  <td><strong className={styles.monoCol}>chrome.exe</strong> (Google Chrome)</td>
                  <td><Badge variant="study">Trình duyệt học tập</Badge></td>
                  <td className={styles.monoCol}><strong>5h 15m</strong></td>
                  <td>41%</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol}>02</td>
                  <td><strong className={styles.monoCol}>Code.exe</strong> (VS Code)</td>
                  <td><Badge variant="study">Học lập trình</Badge></td>
                  <td className={styles.monoCol}><strong>2h 45m</strong></td>
                  <td>21%</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol}>03</td>
                  <td><strong className={styles.monoCol}>msedge.exe</strong> (Edge)</td>
                  <td><Badge variant="study">Học trực tuyến</Badge></td>
                  <td className={styles.monoCol}><strong>1h 30m</strong></td>
                  <td>12%</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol}>04</td>
                  <td><strong className={styles.monoCol}>WINWORD.EXE</strong> (Word)</td>
                  <td><Badge variant="study">Soạn thảo bài học</Badge></td>
                  <td className={styles.monoCol}><strong>1h 10m</strong></td>
                  <td>9%</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol}>05</td>
                  <td><strong className={styles.monoCol}>Spotify.exe</strong></td>
                  <td><Badge variant="leisure">Âm nhạc thư giãn</Badge></td>
                  <td className={styles.monoCol}><strong>50m</strong></td>
                  <td>6%</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol} style={{ color: 'var(--color-danger)' }}>06</td>
                  <td><strong className={styles.monoCol} style={{ color: 'var(--color-danger)' }}>RobloxPlayerBeta.exe</strong></td>
                  <td><Badge variant="block">Trò chơi</Badge></td>
                  <td className={styles.monoCol}><strong>0m</strong></td>
                  <td>0%</td>
                  <td><Badge variant="block">Đã ngắt tiến trình</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'top-domains' && (
          <div className="table-container">
            <table className="data-table-box">
              <thead>
                <tr>
                  <th style={{ width: 50 }}>#</th>
                  <th>Tên miền cấp 2 (NT2 - Data Minimisation)</th>
                  <th style={{ width: 140 }}>Phân loại</th>
                  <th style={{ width: 140 }}>Số truy vấn</th>
                  <th style={{ width: 150 }}>Thời gian ước tính</th>
                  <th style={{ width: 120 }}>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className={styles.monoCol}>01</td>
                  <td><strong className={styles.monoCol}>khanacademy.org</strong></td>
                  <td><Badge variant="study">Giáo dục</Badge></td>
                  <td className={styles.monoCol}>142 lượt</td>
                  <td className={styles.monoCol}>3h 20m</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol}>02</td>
                  <td><strong className={styles.monoCol}>scratch.mit.edu</strong></td>
                  <td><Badge variant="study">Giáo dục</Badge></td>
                  <td className={styles.monoCol}>98 lượt</td>
                  <td className={styles.monoCol}>2h 10m</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol}>03</td>
                  <td><strong className={styles.monoCol}>youtube.com</strong></td>
                  <td><Badge variant="leisure">Giải trí</Badge></td>
                  <td className={styles.monoCol}>85 lượt</td>
                  <td className={styles.monoCol}>2h 00m</td>
                  <td><Badge variant="leisure">SafeSearch</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol}>04</td>
                  <td><strong className={styles.monoCol}>wikipedia.org</strong></td>
                  <td><Badge variant="study">Tra cứu</Badge></td>
                  <td className={styles.monoCol}>45 lượt</td>
                  <td className={styles.monoCol}>45m</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td className={styles.monoCol}>05</td>
                  <td><strong className={styles.monoCol}>tongdai111.vn</strong></td>
                  <td><Badge variant="study">Cứu hộ khẩn cấp</Badge></td>
                  <td className={styles.monoCol}>2 lượt</td>
                  <td className={styles.monoCol}>5m</td>
                  <td><Badge variant="ok">NT6 Whitelist</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'blocked-logs' && (
          <div className="table-container">
            <table className="data-table-box">
              <thead>
                <tr>
                  <th style={{ width: 140 }}>Dấu thời gian</th>
                  <th style={{ width: 110 }}>Tầng lọc</th>
                  <th>Đối tượng (Subject)</th>
                  <th style={{ width: 180 }}>Quy tắc áp dụng</th>
                  <th>Hành động của Agent</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className={styles.monoCol} style={{ fontSize: '0.75rem' }}>18/10 16:30:12</td>
                  <td><Badge variant="block">DNS (Port 53)</Badge></td>
                  <td><strong className={styles.monoCol} style={{ color: 'var(--color-danger)' }}>roblox.com</strong></td>
                  <td>Chặn danh mục Trò chơi</td>
                  <td>Trả NXDOMAIN + Popup thông báo lý do (NT4)</td>
                </tr>
                <tr>
                  <td className={styles.monoCol} style={{ fontSize: '0.75rem' }}>17/10 21:05:44</td>
                  <td><Badge variant="block">Process (psutil)</Badge></td>
                  <td><strong className={styles.monoCol} style={{ color: 'var(--color-danger)' }}>RobloxPlayerBeta.exe</strong></td>
                  <td>Khớp SHA-256 danh mục cấm</td>
                  <td>Terminated Process + Ghi sự kiện audit</td>
                </tr>
                <tr>
                  <td className={styles.monoCol} style={{ fontSize: '0.75rem' }}>16/10 22:15:00</td>
                  <td><Badge variant="leisure">Screen Quota</Badge></td>
                  <td><strong className={styles.monoCol}>Hết giờ ngày thường</strong></td>
                  <td>Lịch tuần 7x48 (Khóa đêm 22h)</td>
                  <td>Khóa phiên đăng nhập Windows (Lock Workstation)</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}