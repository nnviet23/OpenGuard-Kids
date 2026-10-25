import { Link } from 'react-router-dom';
import AuthLayout from '../auth-layout';
import UserAuthForm from './components/user-auth-form';

export default function SignInPage() {
  return (
    <AuthLayout
      title="Đăng nhập"
      description={<span>Dành cho phụ huynh và tài khoản xem của trẻ. Chưa có tài khoản?{' '}
        <Link to="/sign-up" style={{ color: 'var(--text-main)', textDecoration: 'underline' }}>Đăng ký</Link></span>}
      footerNote={<span>OpenGuard Kids chỉ ghi tên ứng dụng, tên miền, thời lượng và thời điểm — không đọc tin nhắn, không chụp màn hình.</span>}
    >
      <UserAuthForm />
    </AuthLayout>
  );
}
