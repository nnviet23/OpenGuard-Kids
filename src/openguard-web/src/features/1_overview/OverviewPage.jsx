import React from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import styles from './OverviewPage.module.css';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import WeeklyBarChart from './components/WeeklyBarChart';
import CategoryDonutChart from './components/CategoryDonutChart';
import { IconClock, IconAlert } from '../../components/icons/PixelIcons';

export default function OverviewPage() {
  const { selectedChild } = useOutletContext();

  return (
    <div>
      <div className={styles.pageHeader}>
        <h2 className={styles.heading}>Trung tâm giám sát tổng quan</h2>
        <p className={styles.subheading}>
          Dữ liệu thời gian thực đồng bộ từ OGK-Agent qua giao thức bảo mật cho: {selectedChild}
        </p>
      </div>

      <div className={styles.kpiRow}>
        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Thời gian hôm nay</span>
            <IconClock color="var(--color-primary)" />
          </div>
          <div className={styles.kpiNum}>1h 45m</div>
          <div className={styles.kpiBottom}>
            <span>Hạn mức: <strong>2h 00m</strong></span>
            <Badge variant="leisure">87% Quota</Badge>
          </div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Đồng hồ còn lại</span>
            <IconClock color="var(--color-danger)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-danger)' }}>15:00</div>
          <div className={styles.kpiBottom}>
            <span>Đang trừ lùi theo Active Time</span>
          </div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Agent Host</span>
            <Badge variant="ok">ONLINE</Badge>
          </div>
          <div className={styles.kpiNum} style={{ fontSize: '1.35rem', color: 'var(--color-success)' }}>
            CONNECTED
          </div>
          <div className={styles.kpiBottom}>
            <span>CPU: <strong>1.4%</strong> | RAM: <strong>48MB</strong></span>
          </div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Ngăn chặn / Vi phạm</span>
            <IconAlert color="var(--color-danger)" />
          </div>
          <div className={styles.kpiNum}>03 lần</div>
          <div className={styles.kpiBottom}>
            <Badge variant="block">2 tên miền</Badge>
            <Badge variant="block">1 app</Badge>
          </div>
        </Card>
      </div>

      <div className={styles.chartsGrid}>
        <Card 
          title="Thời lượng sử dụng tuần này"
          caption="Đơn vị: giờ (Phân tách Học tập vs Giải trí)"
        >
          <WeeklyBarChart />
        </Card>

        <Card 
          title="Phân loại hôm nay"
          caption="Tỷ lệ theo danh mục ứng dụng"
        >
          <CategoryDonutChart totalTime="1h45m" />
        </Card>
      </div>

      <div className={styles.detailGrid}>
        <Card 
          title="Tên miền ghi nhận hôm nay"
          caption="DNS Proxy 127.0.0.1:53 (Chỉ lưu Domain cấp 2 - Tuân thủ NT2)"
          action={<Badge variant="ok">DNS FILTER: ON</Badge>}
        >
          <div className="table-container">
            <table className="data-table-box">
              <thead>
                <tr>
                  <th>Tên miền</th>
                  <th>Phân loại</th>
                  <th>Thời gian / Query</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong style={{ fontFamily: 'var(--font-mono)' }}>khanacademy.org</strong></td>
                  <td><Badge variant="study">Giáo dục</Badge></td>
                  <td>55 phút (14 req)</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td><strong style={{ fontFamily: 'var(--font-mono)' }}>scratch.mit.edu</strong></td>
                  <td><Badge variant="study">Lập trình</Badge></td>
                  <td>30 phút (19 req)</td>
                  <td><Badge variant="ok">Cho phép</Badge></td>
                </tr>
                <tr>
                  <td><strong style={{ fontFamily: 'var(--font-mono)' }}>youtube.com</strong></td>
                  <td><Badge variant="leisure">Giải trí</Badge></td>
                  <td>20 phút (8 req)</td>
                  <td><Badge variant="leisure">SafeSearch</Badge></td>
                </tr>
                <tr>
                  <td><strong style={{ fontFamily: 'var(--font-mono)' }}>roblox.com</strong></td>
                  <td><Badge variant="block">Trò chơi</Badge></td>
                  <td>15:30:12</td>
                  <td><Badge variant="block">BLOCKED</Badge></td>
                </tr>
                <tr>
                  <td><strong style={{ fontFamily: 'var(--font-mono)' }}>discord.com</strong></td>
                  <td><Badge variant="block">Mạng XH</Badge></td>
                  <td>16:05:44</td>
                  <td><Badge variant="block">BLOCKED</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>

        <Card 
          title="Tiến trình Windows (psutil)"
          caption="Theo dõi tên file thực thi & mã băm SHA-256"
        >
          <div className={styles.processList}>
            <div className={styles.processItem}>
              <div className={styles.processMeta}>
                <span><strong>chrome.exe</strong> (Trình duyệt)</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>1h 15m</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: '75%' }} />
              </div>
            </div>

            <div className={styles.processItem}>
              <div className={styles.processMeta}>
                <span><strong>Code.exe</strong> (VS Code)</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>25m</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: '25%' }} />
              </div>
            </div>

            <div className={styles.processItem}>
              <div className={styles.processMeta}>
                <span><strong>RobloxPlayer.exe</strong></span>
                <Badge variant="block">KILL PROCESS</Badge>
              </div>
              <div className="progress-track">
                <div className="progress-fill progress-fill-danger" style={{ width: '100%' }} />
              </div>
            </div>
          </div>

          <div className={styles.banner}>
            <div>
              <div className={styles.bannerTitle}>Yêu cầu chờ xử lý (02)</div>
              <div className={styles.bannerDesc}>Bé xin thêm 30 phút • Báo nhầm chặn web</div>
            </div>
            <Link to="/requests">
              <Button variant="primary" size="sm">Mở duyệt</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}