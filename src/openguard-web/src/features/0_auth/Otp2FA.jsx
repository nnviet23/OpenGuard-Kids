import { useState, useRef } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import styles from './Auth.module.css';
import AuthLayout from './AuthLayout';
import Button from '../../components/common/Button';

export default function Otp2FA() {
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email || 'parent@openguard.local';

  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const inputsRef = useRef([]);

  const handleChange = (val, idx) => {
    if (!/^[0-9]?$/.test(val)) return;
    const nextOtp = [...otp];
    nextOtp[idx] = val;
    setOtp(nextOtp);

    // Tự động nhảy ô tiếp theo
    if (val && idx < 5) {
      inputsRef.current[idx + 1]?.focus();
    }
  };

  const handleKeyDown = (e, idx) => {
    if (e.key === 'Backspace' && !otp[idx] && idx > 0) {
      inputsRef.current[idx - 1]?.focus();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const code = otp.join('');
    if (code.length < 6) {
      alert('Vui lòng nhập đủ 6 chữ số TOTP!');
      return;
    }

    alert(`[2FA Verified] Xác thực TOTP thành công cho tài khoản: ${email}`);
    navigate('/overview');
  };

  return (
    <AuthLayout
      title="Xác thực 2 yếu tố (2FA)"
      subtitle="Nhập mã 6 chữ số từ ứng dụng Google Authenticator hoặc Authy"
    >
      <form onSubmit={handleSubmit} className={styles.form}>
        <div style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Đang xác thực cho: <strong>{email}</strong>
        </div>

        <div className={styles.otpRow}>
          {otp.map((digit, idx) => (
            <input
              key={idx}
              ref={(el) => (inputsRef.current[idx] = el)}
              type="text"
              maxLength={1}
              className={styles.otpInput}
              value={digit}
              onChange={(e) => handleChange(e.target.value, idx)}
              onKeyDown={(e) => handleKeyDown(e, idx)}
              autoFocus={idx === 0}
            />
          ))}
        </div>

        <div className={styles.securityNote}>
          🔑 Không có điện thoại bên cạnh? Bạn có thể sử dụng một trong các <strong>Backup Codes (Mã cứu hộ)</strong> đã cấp khi thiết lập[cite: 8].
        </div>

        <Button type="submit" variant="primary" className={styles.submitBtn}>
          Xác thực & Vào Bảng điều khiển
        </Button>

        <div className={styles.footerLinks} style={{ justifyContent: 'center' }}>
          <Link to="/login" className={styles.link}>
            ← Quay lại màn hình đăng nhập
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}