import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styles from './Auth.module.css';
import AuthLayout from './AuthLayout';
import Button from '../../components/common/Button';

export default function OtpSignUp() {
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email || 'parent@example.com';
  const fullName = location.state?.fullName || 'Phụ huynh';

  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [countdown, setCountdown] = useState(60);
  const inputsRef = useRef([]);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleChange = (val, idx) => {
    if (!/^[0-9]?$/.test(val)) return;
    const nextOtp = [...otp];
    nextOtp[idx] = val;
    setOtp(nextOtp);

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
      alert('Vui lòng nhập đầy đủ 6 chữ số OTP!');
      return;
    }

    alert(`[Kích hoạt hoàn tất] Chào mừng ${fullName}! Tài khoản đã được xác thực an toàn.`);
    navigate('/overview');
  };

  const handleResend = () => {
    setCountdown(60);
    alert(`Đã gửi lại mã OTP mới đến: ${email}`);
  };

  return (
    <AuthLayout
      title="Xác minh Hòm thư Email"
      subtitle="Kích hoạt tài khoản phụ huynh mới khởi tạo"
    >
      <form onSubmit={handleSubmit} className={styles.form}>
        <p style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Chúng tôi đã gửi mã xác minh 6 số đến:<br />
          <strong style={{ color: 'var(--text-main)' }}>{email}</strong>
        </p>

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

        <div className={styles.resendRow}>
          <span>Không nhận được mã?</span>
          {countdown > 0 ? (
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
              Gửi lại sau {countdown}s
            </span>
          ) : (
            <button
              type="button"
              className={styles.link}
              style={{ background: 'none', border: 'none', padding: 0 }}
              onClick={handleResend}
            >
              Gửi lại mã ngay
            </button>
          )}
        </div>

        <Button type="submit" variant="primary" className={styles.submitBtn}>
          Xác nhận & Kích hoạt
        </Button>
      </form>
    </AuthLayout>
  );
}