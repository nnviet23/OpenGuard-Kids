import { useState } from 'react';
import styles from './CategoryModal.module.css';
import Modal from '../../../components/common/Modal';
import Button from '../../../components/common/Button';
import Badge from '../../../components/common/Badge';

const DEFAULT_CATEGORIES = [
  { id: 'cat_1', name: '📚 Học tập & Giáo dục', statusText: 'Mặc định: Cho phép', badge: 'ok' },
  { id: 'cat_2', name: '🎬 Giải trí phù hợp', statusText: 'Mặc định: Quota', badge: 'leisure' },
  { id: 'cat_3', name: '💬 Mạng xã hội', statusText: 'Mặc định: Chặn', badge: 'block' },
  { id: 'cat_4', name: '🎮 Trò chơi trực tuyến', statusText: 'Mặc định: Chặn', badge: 'block' },
  { id: 'cat_5', name: '🚫 Không phù hợp lứa tuổi', statusText: 'Mặc định: Chặn vĩnh viễn', badge: 'block' },
];

export default function CategoryModal({ isOpen, onClose }) {
  const [categories, setCategories] = useState(DEFAULT_CATEGORIES);
  const [newCatName, setNewCatName] = useState('');

  if (!isOpen) return null;

  const handleAddCategory = (e) => {
    e.preventDefault();
    if (!newCatName.trim()) return;

    setCategories((prev) => [
      ...prev,
      {
        id: `cat_${Date.now()}`,
        name: `📁 ${newCatName.trim()}`,
        statusText: 'Mặc định: Tùy chỉnh',
        badge: 'study',
      },
    ]);
    setNewCatName('');
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Quản lý Danh mục Ứng dụng & Web">
      <p className={styles.description}>
        Hệ thống phân loại theo các nhóm mặc định cho trẻ 6-11 tuổi theo đồ án[cite: 7]. Bạn có thể bổ sung danh mục mới.
      </p>

      <div className={styles.categoryList}>
        {categories.map((cat) => (
          <div key={cat.id} className={styles.categoryItem}>
            <span>{cat.name}</span>
            <Badge variant={cat.badge}>{cat.statusText}</Badge>
          </div>
        ))}
      </div>

      <form onSubmit={handleAddCategory} className={styles.addForm}>
        <label className={styles.label}>Thêm loại mới:</label>
        <div className={styles.inputGroup}>
          <input
            type="text"
            className={styles.input}
            placeholder="Tên danh mục (vd: Đọc sách, Ngoại ngữ)"
            value={newCatName}
            onChange={(e) => setNewCatName(e.target.value)}
          />
          <Button type="submit" variant="primary">
            + Thêm
          </Button>
        </div>
      </form>

      <div className={styles.actions}>
        <Button variant="secondary" onClick={onClose}>
          Đóng
        </Button>
      </div>
    </Modal>
  );
}