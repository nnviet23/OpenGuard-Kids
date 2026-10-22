import { useState } from 'react';
import styles from './DeviceList.module.css';
import Badge from '../../../components/common/Badge';
import Button from '../../../components/common/Button';

const INITIAL_DEVICES = [
  {
    id: 'dev_1',
    name: 'Dell Inspiron 15 (Máy Bé Nam Việt)',
    status: 'online',
    statusBadge: 'ok',
    statusText: 'AGENT ONLINE',
    fingerprint: 'SHA256:7f9a...88b2',
    ip: '192.168.1.18',
    date: '12/10/2026',
    revoked: false,
  },
  {
    id: 'dev_2',
    name: 'PC Học tập (Máy Bé Mai Anh)',
    status: 'idle',
    statusBadge: 'study',
    statusText: 'AGENT IDLE',
    fingerprint: 'SHA256:4a12...99c1',
    ip: '192.168.1.25',
    date: '14/10/2026',
    revoked: false,
  },
];

export default function DeviceList() {
  const [devices, setDevices] = useState(INITIAL_DEVICES);

  const handleRevoke = (id, name) => {
    if (window.confirm(`Bạn có chắc muốn THU HỒI TOKEN và hủy kết nối với thiết bị '${name}' không?`)) {
      setDevices((prev) =>
        prev.map((d) => (d.id === id ? { ...d, revoked: true } : d))
      );
      alert(`[Revocation Notice] Đã đưa Device ID vào Danh sách thu hồi (Revocation list). Agent sẽ không thể đồng bộ chính sách.`);
    }
  };

  return (
    <div>
      {devices.map((device) => (
        <div 
          key={device.id} 
          className={styles.deviceRow}
          style={device.revoked ? { opacity: 0.5 } : {}}
        >
          <div>
            <div className={styles.deviceMeta}>
              <strong 
                className={styles.deviceName}
                style={device.revoked ? { textDecoration: 'line-through' } : {}}
              >
                {device.name}
              </strong>
              <Badge variant={device.revoked ? 'block' : device.statusBadge}>
                {device.revoked ? 'DE-ENROLLED' : device.statusText}
              </Badge>
            </div>

            {device.revoked ? (
              <div className={styles.revokedNotice}>ĐÃ THU HỒI TOKEN (REVOKED)</div>
            ) : (
              <>
                <div className={styles.deviceDetails}>
                  Fingerprint: <strong>{device.fingerprint}</strong> • IP: <strong>{device.ip}</strong> • Token hạn: 15p
                </div>
                <div className={styles.deviceDate}>
                  Ghép đôi ngày {device.date} qua mã xác thực 8 ký tự
                </div>
              </>
            )}
          </div>

          <div>
            {!device.revoked && (
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleRevoke(device.id, device.name)}
              >
                Thu hồi Token (Hủy ghép)
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}