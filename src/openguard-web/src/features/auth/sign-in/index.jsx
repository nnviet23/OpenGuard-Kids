import { Link } from 'react-router-dom';
import AuthLayout from '../auth-layout';
import UserAuthForm from './components/user-auth-form';

export default function SignInPage() {
  return (
    <AuthLayout
      title="Sign in"
      description={
        <span>
          Enter your email and password below to log into your account. Don't have an account?{' '}
          <Link to="/sign-up" style={{ color: 'var(--text-main)', textDecoration: 'underline' }}>
            Sign Up
          </Link>
        </span>
      }
      footerNote={
        <span>
          By clicking sign in, you agree to our{' '}
          <a href="#" className="footerLink">Terms of Service</a> and{' '}
          <a href="#" className="footerLink">Privacy Policy</a>.
        </span>
      }
    >
      <UserAuthForm />
    </AuthLayout>
  );
}
