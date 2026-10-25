import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2, LogIn } from 'lucide-react';
import { useAuth } from '../../../../core/AuthContext';
import { errorText } from '../../../../core/api-client';
import { Button, Input } from '../../../../shared';
import styles from '../sign-in.module.css';

export default function UserAuthForm() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [totp, setTotp] = useState('');
  const [needTotp, setNeedTotp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      const acc = await login(email, password, totp);
      navigate(acc.role === 'child_view' ? '/today' : '/');
    } catch (err) {
      const msg = errorText(err, 'Đăng nhập thất bại.');
      setError(msg);
      if (err.response?.status === 401) setNeedTotp(true); // có thể tài khoản bật TOTP – cho phép nhập mã
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      {error && <div className={styles.errorAlert}>{error}</div>}
      <form onSubmit={submit} className={styles.form}>
        <Input id="email" label="Email" type="email" required autoComplete="username" value={email}
          onChange={(e) => setEmail(e.target.value)} placeholder="ten@example.com" />
        <div className={styles.passwordInputWrapper}>
          <Input id="password" label="Mật khẩu" type={showPassword ? 'text' : 'password'} required minLength={10}
            autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)}
            placeholder="Ít nhất 10 ký tự" style={{ paddingRight: '2.5rem' }} />
          <button type="button" className={styles.eyeButton} style={{ top: '2.1rem' }} onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}>
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
        {needTotp && (
          <Input id="totp" label="Mã xác thực 6 số (nếu đã bật)" inputMode="numeric" maxLength={6} value={totp}
            autoComplete="one-time-code" onChange={(e) => setTotp(e.target.value.replace(/\D/g, ''))} />
        )}
        <Button type="submit" fullWidth disabled={busy}>
          {busy ? <Loader2 size={16} className="animate-spin" /> : <><LogIn size={16} /><span>Đăng nhập</span></>}
        </Button>
      </form>
    </div>
  );
}
