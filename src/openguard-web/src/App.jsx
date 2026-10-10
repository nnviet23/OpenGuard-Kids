import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './core/AuthContext';
import SignInPage from './features/auth/sign-in';
import SignUpPage from './features/auth/sign-up';
import ForgotPasswordPage from './features/auth/forgot-password';
import OtpPage from './features/auth/otp';

import { DashboardLayout } from './shared';
import DashboardPage from './features/dashboard/page';
import TasksPage from './features/tasks/page';
import SitesPage from './features/sites/page';
import ChatsPage from './features/chats/page';
import UsersPage from './features/users/page';
import TimeSchedulePage from './features/time-schedule/page';
import ReportsPage from './features/reports/page';
import SettingsPage from './features/settings/page';

const ProtectedRoute = ({ children }) => {
  const { parent, loading } = useAuth();
  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Đang tải...</div>;
  }
  return parent ? children : <Navigate to="/login" replace />;
};



export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Nhóm Auth */}
          <Route path="/login" element={<SignInPage />} />
          <Route path="/sign-up" element={<SignUpPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/otp" element={<OtpPage />} />

          {/* Nhóm Dashboard bọc bởi DashboardLayout */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="time-schedule" element={<TimeSchedulePage />} />
            <Route path="sites" element={<SitesPage />} />
            <Route path="chats" element={<ChatsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="tasks" element={<TasksPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
