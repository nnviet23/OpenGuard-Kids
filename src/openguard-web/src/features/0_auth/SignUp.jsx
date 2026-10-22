import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Auth.module.css';
import AuthLayout from './AuthLayout';
import Button from '../../components/common/Button';
import { IconEye, IconEyeOff } from '../../components/icons/PixelIcons';

export default function SignUp() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeConsent, setAgreeConsent] = useState(false);

  const getStrengthLevel = () => {
    if (password.length === 0) return 0;
    if (password.length < 10) return 1;
    if (!/[A-Z]/.test(password) || !/[0-9]/.test(password)) return 2;
    return 3;
  };
  const strength = getStrengthLevel();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password.length < 10) {
      alert('Mật khẩu phải có tối thiểu 10 ký tự theo chuẩn NIST SP 800-63B![cite: 8]');
      return;
    }
    if (password !== confirmPassword) {
      alert('Xác nhận mật khẩu không khớp!');
      return;
    }
    if (!agreeConsent) {
      alert('Vui lòng đồng thuận với điều khoản bảo vệ dữ liệu trẻ em![cite: 3]');
      return;
    }

    navigate('/auth/verify-email', { state: { email, fullName } });
  };

  return (
    <AuthLayout
      title="Đăng ký Phụ huynh"
      subtitle="Thiết lập tài khoản quản trị theo nguyên tắc minh bạch hai chiều"
    >
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Họ và tên phụ huynh</label>
          <input
            type="text"
            className={styles.input}
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Nguyễn Văn A"
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Địa chỉ Email</label>
          <input
            type="email"
            className={styles.input}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="parent@example.com"
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Mật khẩu (Tối thiểu 10 ký tự)[cite: 8]</label>
          <div className={styles.passwordWrapper}>
            <input
              type={showPassword ? 'text' : 'password'}
              className={styles.passwordInput}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Ít nhất 10 ký tự..."
              required
            />
            <button
              type="button"
              className={styles.eyeBtn}
              onClick={() => setShowPassword(!showPassword)}
              title={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
            >
              {showPassword ? <IconEyeOff size={16} /> : <IconEye size={16} />}
            </button>
          </div>

          <div className={styles.strengthBar}>
            <div className={`${styles.strengthSeg} ${strength >= 1 ? styles.activeWeak : ''}`} />
            <div className={`${styles.strengthSeg} ${strength >= 2 ? styles.activeMed : ''}`} />
            <div className={`${styles.strengthSeg} ${strength >= 3 ? styles.activeStr : ''}`} />
          </div>
          <div
            className={styles.strengthText}
            style={{
              color: strength === 1 ? 'var(--color-danger)' : strength === 2 ? 'var(--color-warning)' : strength === 3 ? 'var(--color-success)' : 'var(--text-sub)'
            }}
          >
            {strength === 0 && 'Độ mạnh: Chưa nhập'}
            {strength === 1 && `Độ mạnh: Yếu (${password.length}/10 ký tự)[cite: 8]`}
            {strength === 2 && 'Độ mạnh: Trung bình (Cần chữ in hoa & số)'}
            {strength === 3 && 'Độ mạnh: Rất an toàn (Đáp ứng NIST SP 800-63B)'}
          </div>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Xác nhận mật khẩu</label>
          <div className={styles.passwordWrapper}>
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              className={styles.passwordInput}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
            <button
              type="button"
              className={styles.eyeBtn}
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              title={showConfirmPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
            >
              {showConfirmPassword ? <IconEyeOff size={16} /> : <IconEye size={16} />}
            </button>
          </div>
        </div>

        <label className={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={agreeConsent}
            onChange={(e) => setAgreeConsent(e.target.checked)}
          />
          <span>
            Tôi cam kết là cha mẹ/người giám hộ hợp pháp và đồng ý tuân thủ <strong>Điều 21 Luật Trẻ em 2016</strong> & <strong>Nghị định 13/2023/NĐ-CP</strong> về bảo vệ dữ liệu cá nhân.
          </span>
        </label>

        <Button type="submit" variant="primary" className={styles.submitBtn}>
          Tiếp tục: Xác minh Email
        </Button>

        <div className={styles.footerLinks} style={{ justifyContent: 'center', gap: 6 }}>
          <span>Đã có tài khoản?</span>
          <Link to="/login" className={styles.link}>
            Đăng nhập
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}