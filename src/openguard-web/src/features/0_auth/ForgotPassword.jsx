import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Auth.module.css';
import AuthLayout from './AuthLayout';
import Button from '../../components/common/Button';

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isSent, setIsSent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email) return;

    // Mô phỏng gọi API gửi link khôi phục mật khẩu bảo mật (hạn 15 phút)
    setIsSent(true);
  };

  return (
    <AuthLayout
      title="Khôi phục Mật khẩu"
      subtitle="Thiết lập lại mật khẩu tài khoản phụ huynh qua kênh an toàn"
    >
      {!isSent ? (
        <form onSubmit={handleSubmit} className={styles.form}>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
            Nhập địa chỉ email đăng ký. Chúng tôi sẽ gửi mã bảo mật khôi phục mật khẩu có hiệu lực trong vòng 15 phút.
          </p>

          <div className={styles.formGroup}>
            <label className={styles.label}>Email tài khoản</label>
            <input
              type="email"
              className={styles.input}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="parent@example.com"
              required
            />
          </div>

          <Button type="submit" variant="primary" className={styles.submitBtn}>
            Gửi liên kết khôi phục
          </Button>

          <div className={styles.footerLinks} style={{ justifyContent: 'center' }}>
            <Link to="/login" className={styles.link}>
              ← Quay lại Đăng nhập
            </Link>
          </div>
        </form>
      ) : (
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ fontSize: '2.2rem' }}>✉️</div>
          <h3 style={{ fontSize: '1rem', fontWeight: 800 }}>Đã gửi hướng dẫn khôi phục!</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
            Vui lòng kiểm tra hòm thư <strong>{email}</strong> để lấy mã và thiết lập lại mật khẩu mới.
          </p>
          <Button variant="secondary" onClick={() => navigate('/login')}>
            Trở về trang Đăng nhập
          </Button>
        </div>
      )}
    </AuthLayout>
  );
}