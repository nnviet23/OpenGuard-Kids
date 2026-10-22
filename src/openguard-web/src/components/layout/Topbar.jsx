import React, { useState } from 'react';
import styles from './Topbar.module.css';
import Button from '../common/Button';
import Badge from '../common/Badge';
import Modal from '../common/Modal';
import { IconLock, IconUnlock, IconPlus } from '../icons/PixelIcons';

export default function Topbar({ 
  currentChild = 'child_1', 
  onSelectChild, 
  onEmergencyCommand 
}) {
  const [isPairModalOpen, setIsPairModalOpen] = useState(false);

  const handleCommand = (cmd) => {
    if (onEmergencyCommand) {
      onEmergencyCommand(cmd);
    }
  };

  return (
    <>
      <header className={styles.topbar}>
        <div className={styles.pickerWrap}>
          <span className={styles.label}>Mục tiêu:</span>
          <select 
            className={styles.select} 
            value={currentChild} 
            onChange={(e) => onSelectChild && onSelectChild(e.target.value)}
          >
            <option value="child_1">Bé Nam Việt (Dell Inspiron 15)</option>
            <option value="child_2">Bé Mai Anh (PC Học tập)</option>
          </select>

          <Button 
            variant="secondary" 
            icon={<IconPlus />} 
            onClick={() => setIsPairModalOpen(true)}
          >
            Ghép đôi thiết bị
          </Button>
        </div>

        <div className={styles.rightGroup}>
          <div className={styles.emergencyBar}>
            <span className={styles.barTag}>LỆNH KHẨN:</span>
            <Button 
              variant="danger" 
              icon={<IconLock />} 
              onClick={() => handleCommand('lock')}
            >
              Khóa ngay
            </Button>
            <Button 
              variant="secondary" 
              icon={<IconUnlock />} 
              onClick={() => handleCommand('unlock')}
            >
              Mở máy
            </Button>
            <Button 
              variant="primary" 
              onClick={() => handleCommand('extend15')}
            >
              +15 phút
            </Button>
          </div>

          <div className={styles.identity}>
            <div className={styles.avatar}>PH</div>
            <div style={{ fontSize: '0.8rem' }}>
              <strong style={{ display: 'block', lineHeight: 1.1 }}>Phụ huynh</strong>
              <Badge variant="ok" style={{ fontSize: '0.65rem' }}>CONNECTED</Badge>
            </div>
          </div>
        </div>
      </header>

      <Modal 
        isOpen={isPairModalOpen} 
        onClose={() => setIsPairModalOpen(false)}
        title="Ghép đôi thiết bị mới"
      >
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Nhập mã xác thực 8 ký tự bên dưới vào phần mềm <strong>OpenGuard Agent</strong> trên máy tính con để kích hoạt kết nối an toàn.
        </p>

        <div className={styles.codeBox}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
            Mã kết nối (10 phút)
          </span>
          <div className={styles.codeValue}>OGK-8492</div>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--color-danger)', fontWeight: 700 }}>
            Hết hạn sau: 09:42
          </span>
        </div>

        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'var(--bg-subtle)', padding: '8px 10px', borderRadius: 'var(--radius-xs)', marginBottom: 16, border: '1px solid var(--border-light)' }}>
          ⚖️ Căn cứ Điều 21 Luật Trẻ em 2016 & Nghị định 13/2023/NĐ-CP về sự đồng thuận của cha mẹ.
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <Button variant="secondary" onClick={() => setIsPairModalOpen(false)}>Đóng</Button>
          <Button variant="primary" onClick={() => alert('Đã sinh mã ghép đôi mới!')}>Làm mới mã</Button>
        </div>
      </Modal>
    </>
  );
}