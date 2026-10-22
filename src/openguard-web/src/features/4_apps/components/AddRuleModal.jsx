import { useState } from 'react';
import styles from './AddRuleModal.module.css';
import Modal from '../../../components/common/Modal';
import Button from '../../../components/common/Button';

export default function AddRuleModal({ isOpen, onClose, onAddRule }) {
  const [ruleType, setRuleType] = useState('dns');
  const [target, setTarget] = useState('');
  const [targetHash, setTargetHash] = useState('');
  const [category, setCategory] = useState('education');
  const [action, setAction] = useState('block');
  const [scope, setScope] = useState('global');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!target.trim()) {
      alert('Vui lòng nhập tên miền hoặc tên ứng dụng!');
      return;
    }

    onAddRule({
      id: Date.now(),
      type: ruleType,
      target: target.trim(),
      hash: ruleType === 'app' ? targetHash.trim() : null,
      category,
      action,
      scope,
    });

    setTarget('');
    setTargetHash('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Thêm quy tắc kiểm soát mới">
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Loại đối tượng kiểm soát:</label>
          <select 
            className={styles.select} 
            value={ruleType} 
            onChange={(e) => setRuleType(e.target.value)}
          >
            <option value="dns">🌐 Tên miền Website (DNS Proxy 127.0.0.1:53)</option>
            <option value="app">💻 Ứng dụng Windows (Tiến trình .exe & SHA-256)</option>
          </select>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>
            {ruleType === 'dns'
              ? 'Tên miền cấp 2 (ví dụ: steamcommunity.com):'
              : 'Tên tiến trình thực thi (ví dụ: discord.exe):'}
          </label>
          <input
            type="text"
            className={`${styles.input} ${styles.monoInput}`}
            placeholder={ruleType === 'dns' ? 'nhập tên miền website' : 'tên file .exe chạy trên Windows'}
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            required
          />
        </div>

        {ruleType === 'app' && (
          <div className={styles.formGroup}>
            <label className={styles.label}>
              Mã băm SHA-256 tệp thực thi (Chống đổi tên notepad.exe):
            </label>
            <input
              type="text"
              className={`${styles.input} ${styles.monoInput}`}
              placeholder="Để trống nếu muốn agent tự tính hash khi phát hiện"
              value={targetHash}
              onChange={(e) => setTargetHash(e.target.value)}
            />
          </div>
        )}

        <div className={styles.formGroup}>
          <label className={styles.label}>Thuộc Loại danh mục:</label>
          <select 
            className={styles.select} 
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="education">Học tập & Giáo dục</option>
            <option value="leisure">Giải trí phù hợp</option>
            <option value="social">Mạng xã hội</option>
            <option value="games">Trò chơi trực tuyến</option>
            <option value="inappropriate">Không phù hợp lứa tuổi</option>
          </select>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Chính sách ban đầu:</label>
          <select 
            className={styles.select} 
            value={action} 
            onChange={(e) => setAction(e.target.value)}
          >
            <option value="block">🚫 Chặn truy cập (Kill process / DNS NXDOMAIN)</option>
            <option value="allow">✅ Cho phép sử dụng (Nằm trong Quota)</option>
          </select>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Phạm vi áp dụng:</label>
          <select 
            className={styles.select} 
            value={scope} 
            onChange={(e) => setScope(e.target.value)}
          >
            <option value="global">🌐 Toàn bộ các bé (Chính sách chung)</option>
            <option value="child_1">👤 Chỉ áp dụng cho Bé Nam Việt</option>
            <option value="child_2">👤 Chỉ áp dụng cho Bé Mai Anh</option>
          </select>
        </div>

        <div className={styles.actions}>
          <Button type="button" variant="secondary" onClick={onClose}>
            Hủy bỏ
          </Button>
          <Button type="submit" variant="primary">
            Thêm quy tắc
          </Button>
        </div>
      </form>
    </Modal>
  );
}