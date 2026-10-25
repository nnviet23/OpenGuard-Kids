import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './core/AuthContext';
import { ChildProvider } from './core/ChildContext';
import SignInPage from './features/auth/sign-in';
import SignUpPage from './features/auth/sign-up';
import { DashboardLayout } from './shared';
import DashboardPage from './features/dashboard/page';
import TimeSchedulePage from './features/time-schedule/page';
import RulesPage from './features/rules/page';
import RequestsPage from './features/requests/page';
import FamilyPage from './features/family/page';
import AuditPage from './features/audit/page';
import TodayPage from './features/today/page';
import SettingsPage from './features/settings/page';

function Protected({ children }) {
  const { account, loading } = useAuth();
  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Đang tải…</div>;
  return account ? children : <Navigate to="/login" replace />;
}

function Home() {
  const { isChildView } = useAuth();
  return isChildView ? <Navigate to="/today" replace /> : <DashboardPage />;
}

// Trang chỉ dành cho phụ huynh; tài khoản “trẻ xem” được đưa về trang minh bạch.
function ParentOnly({ children }) {
  const { isChildView } = useAuth();
  return isChildView ? <Navigate to="/today" replace /> : children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<SignInPage />} />
          <Route path="/sign-up" element={<SignUpPage />} />
          <Route path="/" element={<Protected><ChildProvider><DashboardLayout /></ChildProvider></Protected>}>
            <Route index element={<Home />} />
            <Route path="today" element={<TodayPage />} />
            <Route path="audit" element={<AuditPage />} />
            <Route path="requests" element={<RequestsPage />} />
            <Route path="time-schedule" element={<ParentOnly><TimeSchedulePage /></ParentOnly>} />
            <Route path="rules" element={<ParentOnly><RulesPage /></ParentOnly>} />
            <Route path="family" element={<ParentOnly><FamilyPage /></ParentOnly>} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
