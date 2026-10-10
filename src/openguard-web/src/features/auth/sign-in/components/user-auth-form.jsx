import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2, LogIn } from 'lucide-react';
import { useAuth } from '../../../../core/AuthContext';
import { Button, Input } from '../../../../shared';
import styles from '../sign-in.module.css';

export default function UserAuthForm() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('parent@openguard.com');
  const [password, setPassword] = useState('OpenGuard@2026');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      const detail = err.response?.data?.detail;

      // Xử lý chuẩn an toàn: nếu FastAPI trả về array validation error (422) hoặc string (400, 401)
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(', '));
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      {error && <div className={styles.errorAlert}>{error}</div>}

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
          <div className={styles.passwordLabelRow}>
            <label htmlFor="password" style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Mật khẩu
            </label>
            <Link to="/forgot-password" className={styles.forgotLink}>
              Forgot password?
            </Link>
          </div>

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

        <Button type="submit" variant="primary" fullWidth disabled={isSubmitting} style={{ marginTop: '0.25rem' }}>
          {isSubmitting ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <>
              <LogIn size={16} />
              <span>Sign in</span>
            </>
          )}
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
    </div>
  );
}
