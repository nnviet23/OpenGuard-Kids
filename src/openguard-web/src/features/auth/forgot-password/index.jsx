import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import AuthLayout from '../auth-layout';
import { Button, Input } from '../../../shared';
import styles from './forgot-password.module.css';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Đã gửi đường dẫn khôi phục tới: ${email}`);
  };

  return (
    <AuthLayout
      title="Forgot Password"
      description="Enter your registered email and we will send you a link to reset your password."
      footerNote={
        <span>
          Don't have an account?{' '}
          <Link to="/sign-up" style={{ color: 'var(--text-main)', textDecoration: 'underline' }}>
            Sign up.
          </Link>
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

        <Button type="submit" variant="primary" fullWidth>
          <span>Continue</span>
          <ArrowRight size={16} />
        </Button>
      </form>
    </AuthLayout>
  );
}
