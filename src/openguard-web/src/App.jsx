import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './components/layout/DashboardLayout';

// Features 0: Auth
import SignIn from './features/0_auth/SignIn';
import SignUp from './features/0_auth/SignUp';
import ForgotPassword from './features/0_auth/ForgotPassword';
import Otp2FA from './features/0_auth/Otp2FA';
import OtpSignUp from './features/0_auth/OtpSignUp';

// Features 1 -> 7: Dashboard
import OverviewPage from './features/1_overview/OverviewPage';
import SchedulePage from './features/2_schedule/SchedulePage';
import RequestsPage from './features/3_requests/RequestsPage';
import AppsPage from './features/4_apps/AppsPage';
import ReportsPage from './features/5_reports/ReportsPage';
import AuditPage from './features/6_audit/AuditPage';
import SettingsPage from './features/7_settings/SettingsPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<SignIn />} />
        <Route path="/auth/signup" element={<SignUp />} />
        <Route path="/auth/forgot-password" element={<ForgotPassword />} />
        <Route path="/auth/2fa" element={<Otp2FA />} />
        <Route path="/auth/verify-email" element={<OtpSignUp />} />

        {/* Protected Dashboard Layout */}
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Navigate to="/overview" replace />} />
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/requests" element={<RequestsPage />} />
          <Route path="/apps" element={<AppsPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/audit" element={<AuditPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}