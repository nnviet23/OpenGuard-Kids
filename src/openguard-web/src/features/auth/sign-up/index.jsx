import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, UserPlus } from 'lucide-react';
import AuthLayout from '../auth-layout';
import { Button, Input } from '../../../shared';
import styles from './sign-up.module.css';

export default function SignUpPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("Mật khẩu xác nhận không khớp!");
      return;
    }
    // Giả lập đăng ký thành công chuyển sang OTP hoặc đăng nhập
    navigate('/otp');
  };

  return (
    <AuthLayout
      title="Create an account"
      description={
        <span>
          Enter your email and password to create an account. Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--text-main)', textDecoration: 'underline' }}>
            Sign In
          </Link>
        </span>
      }
      footerNote={
        <span>
          By creating an account, you agree to our{' '}
          <a href="#" className="footerLink">Terms of Service</a> and{' '}
          <a href="#" className="footerLink">Privacy Policy</a>.
        </span>
      }
    >
      <form onSubmit={handleSubmit} className={styles.form}>
        <Input
          id="email"
          label="Email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="name@example.com"
        />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
          <label style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Password
          </label>
          <div className={styles.passwordInputWrapper}>
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              required
              minLength={10}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{ paddingRight: '2.5rem' }}
            />
            <button
              type="button"
              className={styles.eyeButton}
              onClick={() => setShowPassword(!showPassword)}
              tabIndex={-1}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
          <label style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Confirm Password
          </label>
          <div className={styles.passwordInputWrapper}>
            <Input
              id="confirmPassword"
              type={showConfirm ? 'text' : 'password'}
              required
              minLength={10}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              style={{ paddingRight: '2.5rem' }}
            />
            <button
              type="button"
              className={styles.eyeButton}
              onClick={() => setShowConfirm(!showConfirm)}
              tabIndex={-1}
            >
              {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <Button type="submit" variant="primary" fullWidth style={{ marginTop: '0.25rem' }}>
          <UserPlus size={16} />
          <span>Create Account</span>
        </Button>
      </form>

      <div className={styles.dividerRow}>
        <div className={styles.dividerLine} />
        <span className={styles.dividerText}>or continue with</span>
        <div className={styles.dividerLine} />
      </div>

      <div className={styles.socialRow}>
        <Button variant="outline" fullWidth onClick={() => alert("GitHub SSO Demo")}>
          GitHub
        </Button>
        <Button variant="outline" fullWidth onClick={() => alert("Facebook SSO Demo")}>
          Facebook
        </Button>
      </div>
    </AuthLayout>
  );
}
