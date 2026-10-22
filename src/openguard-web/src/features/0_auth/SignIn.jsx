import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Auth.module.css';
import AuthLayout from './AuthLayout';
import Button from '../../components/common/Button';
import { IconEye, IconEyeOff } from '../../components/icons/PixelIcons';

export default function SignIn() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('parent@openguard.local');
  const [password, setPassword] = useState('OpenGuard@2026');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) {
      alert('Vui lòng nhập đầy đủ thông tin đăng nhập!');
      return;
    }

    if (email.includes('2fa')) {
      navigate('/auth/2fa', { state: { email } });
    } else {
      navigate('/overview');
    }
  };

  return (
    <AuthLayout
      title="Đăng nhập Phụ huynh"
      subtitle="Quản lý và đồng hành cùng môi trường máy tính của con"
    >
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Tài khoản email</label>
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label className={styles.label}>Mật khẩu</label>
            <Link to="/auth/forgot-password" className={styles.link} style={{ fontSize: '0.72rem' }}>
              Quên mật khẩu?
            </Link>
          </div>
          <div className={styles.passwordWrapper}>
            <input
              type={showPassword ? 'text' : 'password'}
              className={styles.passwordInput}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
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
        </div>

        <div className={styles.securityNote}>
          Tài khoản sẽ tạm 15 phút nếu nhập sai quá 5 lần liên tiếp.
        </div>

        <Button type="submit" variant="primary" className={styles.submitBtn}>
          Đăng nhập an toàn
        </Button>

        <div className={styles.footerLinks} style={{ justifyContent: 'center', gap: 6 }}>
          <span>Chưa có tài khoản phụ huynh?</span>
          <Link to="/auth/signup" className={styles.link}>
            Đăng ký ngay
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}