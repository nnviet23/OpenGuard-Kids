import { useState } from 'react';
import styles from './EraseDataModal.module.css';
import Modal from '../../../components/common/Modal';
import Button from '../../../components/common/Button';

export default function EraseDataModal({ isOpen, onClose, targetChild, onConfirm }) {
  const [password, setPassword] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!password) {
      alert('Vui lòng nhập mật khẩu tài khoản phụ huynh để xác thực!');
      return;
    }
    onConfirm(password);
    setPassword('');
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Xác nhận xóa sạch dữ liệu">
      <form onSubmit={handleSubmit}>
        <p className={styles.legalNotice}>
          Thao tác này thực thi điều khoản bảo vệ dữ liệu cá nhân theo <strong>Điều 21 Luật Trẻ em 2016</strong> và <strong>Nghị định 13/2023/NĐ-CP</strong>.
        </p>

        <div className={styles.warningBox}>
          ⚠️ <strong>Hành động này sẽ thực hiện ngay lập tức:</strong><br />
          1. Xóa toàn bộ lịch sử web, ứng dụng và sự kiện trên máy chủ FastAPI.<br />
          2. Gửi tín hiệu xóa sạch bộ đệm cục bộ (SQLite) của Agent trên máy con.<br />
          3. Thu hồi Access Token và Refresh Token của thiết bị.
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>
            Nhập mật khẩu phụ huynh để xác nhận:
          </label>
          <input
            type="password"
            className={styles.input}
            placeholder="Nhập mật khẩu tài khoản phụ huynh..."
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className={styles.actions}>
          <Button type="button" variant="secondary" onClick={onClose}>
            Hủy bỏ
          </Button>
          <Button type="submit" variant="danger">
            Xác nhận xóa vĩnh viễn
          </Button>
        </div>
      </form>
    </Modal>
  );
}