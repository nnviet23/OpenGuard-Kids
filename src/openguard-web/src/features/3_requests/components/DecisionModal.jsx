import { useState } from 'react';
import styles from './DecisionModal.module.css';
import Modal from '../../../components/common/Modal';
import Button from '../../../components/common/Button';

function getDefaultReply(data) {
  if (!data) return '';
  if (data.action === 'approve') {
    return data.type === 'time'
      ? 'Ba/mẹ đồng ý thêm giờ. Con nhớ giữ gìn mắt nhé!'
      : 'Ba/mẹ đã mở chặn trang web này cho con.';
  }
  return 'Hôm nay con đã dùng đủ thời gian rồi, hãy nghỉ ngơi nhé.';
}

export default function DecisionModal({ isOpen, onClose, data, onConfirm }) {
  const [replyNote, setReplyNote] = useState(() => getDefaultReply(data));

  if (!data) return null;

  const isApprove = data.action === 'approve';
  const title = isApprove ? 'Đồng ý yêu cầu của con' : 'Từ chối yêu cầu của con';

  const handleSubmit = (e) => {
    e.preventDefault();
    onConfirm(data.id, data.action, replyNote);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <form onSubmit={handleSubmit}>
        <div className={styles.targetCard}>
          <div>Mục tiêu: <strong>{data.childName}</strong> ({data.device})</div>
          <div>
            Nội dung: <span className={styles.targetHighlight}>{data.detail}</span>
          </div>
        </div>

        <div>
          <label className={styles.label}>
            Lời nhắn gửi về khay hệ thống của con:
          </label>
          <textarea
            rows={3}
            className={styles.textarea}
            value={replyNote}
            onChange={(e) => setReplyNote(e.target.value)}
            placeholder="Nhập lý do gửi đến con..."
            required
          />
        </div>

        <div className={styles.actions}>
          <Button type="button" variant="secondary" onClick={onClose}>
            Hủy bỏ
          </Button>
          <Button
            type="submit"
            variant={isApprove ? 'primary' : 'danger'}
          >
            {isApprove ? 'Đồng ý & Gửi phản hồi' : 'Từ chối & Gửi phản hồi'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}