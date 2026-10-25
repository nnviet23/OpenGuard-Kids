import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import api, { errorText } from '../../../core/api-client';
import { useAuth } from '../../../core/AuthContext';
import { Button, Input } from '../../../shared';
import AuthLayout from '../auth-layout';
import styles from '../sign-in/sign-in.module.css';

export default function SignUpPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [f, setF] = useState({ display_name: '', email: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (f.password !== f.confirm) return setError('Mật khẩu nhập lại không khớp.');
    setBusy(true);
    try {
      await api.post('/auth/register', { email: f.email, password: f.password, display_name: f.display_name });
      await login(f.email, f.password);
      navigate('/family');
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout title="Tạo tài khoản phụ huynh"
      description={<span>Đã có tài khoản? <Link to="/login" style={{ color: 'var(--text-main)', textDecoration: 'underline' }}>Đăng nhập</Link></span>}
      footerNote={<span>Mật khẩu tối thiểu 10 ký tự, gồm chữ hoa, chữ thường và chữ số.</span>}>
      {error && <div className={styles.errorAlert}>{error}</div>}
      <form onSubmit={submit} className={styles.form}>
        <Input id="name" label="Tên hiển thị" value={f.display_name} onChange={set('display_name')} placeholder="Ví dụ: Mẹ Lan" />
        <Input id="email" label="Email" type="email" required autoComplete="username" value={f.email} onChange={set('email')} />
        <Input id="pw" label="Mật khẩu" type="password" required minLength={10} autoComplete="new-password" value={f.password} onChange={set('password')} />
        <Input id="pw2" label="Nhập lại mật khẩu" type="password" required minLength={10} autoComplete="new-password" value={f.confirm} onChange={set('confirm')} />
        <Button type="submit" fullWidth disabled={busy}>{busy ? <Loader2 size={16} className="animate-spin" /> : 'Đăng ký'}</Button>
      </form>
    </AuthLayout>
  );
}
