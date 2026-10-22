import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import styles from './AuditPage.module.css';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import EraseDataModal from './components/EraseDataModal';
import { 
  IconAudit, 
  IconCheck, 
  IconAlert, 
  IconSearch 
} from '../../components/icons/PixelIcons';

const INITIAL_LOGS = [
  {
    id: 1,
    ts: '18/10 16:32:04',
    actor: 'parent',
    actorLabel: 'Phụ huynh',
    actorSub: 'Web Dashboard',
    actionType: 'request',
    method: 'POST',
    endpoint: '/requests/1/approve',
    diffText: 'Duyệt yêu cầu xin giờ:',
    oldVal: '0m',
    newVal: '+30m',
    ip: '192.168.1.5',
    device: 'Dell Inspiron 15',
    childId: 'child_1',
    status: 'SUCCESS',
  },
  {
    id: 2,
    ts: '18/10 15:35:10',
    actor: 'parent',
    actorLabel: 'Phụ huynh',
    actorSub: 'Lệnh khẩn Web',
    actionType: 'emergency',
    method: 'WSS',
    endpoint: '/ws/emergency/lock',
    diffText: 'Cưỡng chế khóa máy:',
    oldVal: 'Unlocked',
    newVal: 'Locked',
    ip: '192.168.1.5',
    device: 'Latency 0.8s',
    childId: 'child_1',
    status: 'EXECUTED',
  },
  {
    id: 3,
    ts: '17/10 19:40:22',
    actor: 'parent',
    actorLabel: 'Phụ huynh',
    actorSub: 'Cập nhật chính sách',
    actionType: 'policy',
    method: 'PUT',
    endpoint: '/policy/child_1',
    diffText: 'Điều chỉnh Quota ngày thường:',
    oldVal: '01:30',
    newVal: '02:00',
    ip: '192.168.1.5',
    device: 'Policy v1.5',
    childId: 'child_1',
    status: 'SYNCED',
  },
  {
    id: 4,
    ts: '17/10 21:05:44',
    actor: 'agent',
    actorLabel: 'OGK-Agent',
    actorSub: 'SYSTEM Service',
    actionType: 'policy',
    method: 'POST',
    endpoint: '/events/security',
    diffText: 'Chặn tệp thực thi cấm:',
    oldVal: null,
    newVal: 'RobloxPlayerBeta.exe (Kill process)',
    ip: '127.0.0.1',
    device: 'Local psutil',
    childId: 'child_1',
    status: 'ENFORCED',
  },
  {
    id: 5,
    ts: '16/10 17:15:30',
    actor: 'child',
    actorLabel: 'Bé Nam Việt',
    actorSub: 'Tray UI',
    actionType: 'request',
    method: 'POST',
    endpoint: '/requests/new',
    diffText: 'Xin thêm 30 phút (Học bài tập Scratch)',
    oldVal: null,
    newVal: null,
    ip: '192.168.1.18',
    device: 'Windows Client',
    childId: 'child_1',
    status: 'RECEIVED',
  },
  {
    id: 6,
    ts: '12/10 09:20:11',
    actor: 'parent',
    actorLabel: 'Phụ huynh',
    actorSub: 'Xác thực cha mẹ',
    actionType: 'enroll',
    method: 'POST',
    endpoint: '/auth/enroll',
    diffText: 'Ghép đôi PC Học tập (Bé Mai Anh) với mã 8 ký tự',
    oldVal: null,
    newVal: null,
    ip: '192.168.1.5',
    device: 'Token Issued',
    childId: 'child_2',
    status: 'ENROLLED',
  },
];

export default function AuditPage() {
  const { selectedChild } = useOutletContext();
  const [logs, setLogs] = useState(INITIAL_LOGS);
  const [actorFilter, setActorFilter] = useState('all');
  const [actionFilter, setActionFilter] = useState('all');
  const [childFilter, setChildFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isEraseModalOpen, setIsEraseModalOpen] = useState(false);

  const handleEraseConfirm = (pwd) => {
    alert(
      `[ĐÃ THỰC THI NGHỊ ĐỊNH 13/2023 - QUYỀN ĐƯỢC XÓA DỮ LIỆU]\n\nĐã gửi lệnh xóa sạch dữ liệu cho mục tiêu:\n- Server: Đã dọn sạch cơ sở dữ liệu SQLite.\n- Agent: Đã xóa bộ nhớ đệm SQLite trong ProgramData.\n- Mã xác thực: Tokens đã bị thu hồi.`
    );
    setIsEraseModalOpen(false);

    const newLog = {
      id: Date.now(),
      ts: 'Vừa xong',
      actor: 'parent',
      actorLabel: 'Phụ huynh',
      actorSub: 'Web Dashboard',
      actionType: 'privacy',
      method: 'DEL',
      endpoint: '/privacy/erase-all',
      diffText: 'Xóa toàn bộ dữ liệu:',
      oldVal: 'Toàn bộ dữ liệu',
      newVal: 'Đã dọn sạch (0 bản ghi)',
      ip: '192.168.1.5',
      device: 'Localhost',
      childId: selectedChild,
      status: 'PURGED',
    };
    setLogs((prev) => [newLog, ...prev]);
  };

  const filteredLogs = logs.filter((log) => {
    const matchActor = actorFilter === 'all' || log.actor === actorFilter;
    const matchAction = actionFilter === 'all' || log.actionType === actionFilter;
    const matchChild = childFilter === 'all' || log.childId === childFilter;
    const matchSearch = !searchQuery || 
      log.endpoint.toLowerCase().includes(searchQuery.toLowerCase()) || 
      log.ip.includes(searchQuery) ||
      (log.diffText && log.diffText.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchActor && matchAction && matchChild && matchSearch;
  });

  return (
    <div>
      <div className={styles.dangerZoneCard}>
        <div>
          <div className={styles.dangerMetaTitle}>
            <IconAlert size={18} color="var(--color-danger)" />
            <span>Quyền xóa dữ liệu theo yêu cầu (Nghị định 13/2023/NĐ-CP & Luật Trẻ em 2016)</span>
          </div>
          <p className={styles.dangerMetaDesc}>
            Khi bấm nút này, toàn bộ lịch sử sử dụng, sự kiện mạng, và bản ghi quy tắc liên quan đến trẻ sẽ bị xóa vĩnh viễn trên máy chủ FastAPI và xóa sạch bộ nhớ đệm SQLite trên máy của con. Hành động này không thể hoàn tác.
          </p>
        </div>
        <Button variant="danger" onClick={() => setIsEraseModalOpen(true)}>
          Xóa toàn bộ dữ liệu của con
        </Button>
      </div>

      <div className={styles.pageHeader}>
        <h2 className={styles.heading}>Nhật ký kiểm toán hệ thống (Audit Trail)</h2>
        <p className={styles.subheading}>
          Ghi nhận mọi thay đổi chính sách, hành động khẩn cấp và gọi API. Cả phụ huynh và trẻ đều có thể đọc được (Nguyên tắc NT5).
        </p>
      </div>

      <div className={styles.kpiRow}>
        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Tổng số bản ghi</span>
            <IconAudit color="var(--color-primary)" />
          </div>
          <div className={styles.kpiNum}>{logs.length} mục</div>
          <div className={styles.kpiBottom}>Tự động xóa sau 90 ngày</div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Phiên bản chính sách</span>
            <IconCheck color="var(--color-success)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-primary)' }}>v1.5.2</div>
          <div className={styles.kpiBottom}>Ký xác thực HMAC-SHA256</div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Lệnh khẩn cấp (24h)</span>
            <IconAlert color="var(--color-warning)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-warning)' }}>02 lần</div>
          <div className={styles.kpiBottom}>WebSocket Latency &lt; 1.2s</div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Tính toàn vẹn</span>
            <IconCheck color="var(--color-success)" />
          </div>
          <div className={styles.kpiNum} style={{ fontSize: '1.35rem', color: 'var(--color-success)' }}>
            CHỐNG CAN THIỆP
          </div>
          <div className={styles.kpiBottom}>NIST & OWASP ASVS</div>
        </Card>
      </div>

      <Card>
        <div className={styles.toolbar}>
          <div className={styles.filterGroup}>
            <select
              className={styles.select}
              value={childFilter}
              onChange={(e) => setChildFilter(e.target.value)}
            >
              <option value="all">Toàn bộ thiết bị & người dùng</option>
              <option value="child_1">Bé Nam Việt (Dell Inspiron 15)</option>
              <option value="child_2">Bé Mai Anh (PC Học tập)</option>
            </select>

            <select
              className={styles.select}
              value={actorFilter}
              onChange={(e) => setActorFilter(e.target.value)}
            >
              <option value="all">Tất cả người thao tác (Actor)</option>
              <option value="parent">Phụ huynh (Parent Web)</option>
              <option value="agent">Agent Service (SYSTEM)</option>
              <option value="child">Trẻ (Tray UI)</option>
            </select>

            <select
              className={styles.select}
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
            >
              <option value="all">Tất cả loại hành động</option>
              <option value="policy">Thay đổi chính sách / Lịch tuần</option>
              <option value="emergency">Lệnh khẩn cấp (Khóa / +15p)</option>
              <option value="request">Duyệt yêu cầu của trẻ</option>
              <option value="enroll">Ghép đôi thiết bị</option>
            </select>
          </div>

          <div className={styles.searchWrap}>
            <IconSearch color="var(--text-muted)" />
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Tìm IP, API endpoint, giá trị..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="table-container">
          <table className="data-table-box">
            <thead>
              <tr>
                <th style={{ width: 135 }}>Thời điểm (ts)</th>
                <th style={{ width: 140 }}>Người thực hiện (Actor)</th>
                <th style={{ width: 210 }}>API Endpoint / Sự kiện</th>
                <th>Giá trị cũ ➔ Giá trị mới (Diff)</th>
                <th style={{ width: 145 }}>Địa chỉ IP / Thiết bị</th>
                <th style={{ width: 100, textAlign: 'center' }}>Trạng thái</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log) => (
                <tr key={log.id}>
                  <td className={styles.timeCol}>{log.ts}</td>
                  <td>
                    <strong style={{ color: log.actor === 'agent' ? 'var(--color-primary)' : log.actor === 'child' ? 'var(--color-secondary)' : 'inherit' }}>
                      {log.actorLabel}
                    </strong>
                    <span className={styles.subText}>{log.actorSub}</span>
                  </td>
                  <td>
                    <span className={`${styles.methodBadge} ${styles[log.method.toLowerCase()] || styles.post}`}>
                      {log.method}
                    </span>
                    <span className={styles.monoCol}>{log.endpoint}</span>
                  </td>
                  <td>
                    <span>{log.diffText}</span>
                    {log.oldVal && <span className={`${styles.diffValBox} ${styles.diffOld}`}>{log.oldVal}</span>}
                    {log.oldVal && log.newVal && <span style={{ fontSize: '0.75rem' }}>➔</span>}
                    {log.newVal && <span className={`${styles.diffValBox} ${styles.diffNew}`}>{log.newVal}</span>}
                  </td>
                  <td className={styles.monoCol}>
                    {log.ip}
                    <span className={styles.subText}>({log.device})</span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <Badge variant={log.status === 'ENFORCED' ? 'block' : log.status === 'RECEIVED' ? 'study' : 'ok'}>
                      {log.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <EraseDataModal
        isOpen={isEraseModalOpen}
        onClose={() => setIsEraseModalOpen(false)}
        targetChild={selectedChild}
        onConfirm={handleEraseConfirm}
      />
    </div>
  );
}