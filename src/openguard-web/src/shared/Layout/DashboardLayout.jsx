import { Outlet } from 'react-router-dom';
import { SidebarProvider } from '../../core/SidebarContext';
import Sidebar from '../Sidebar/Sidebar';
import TopHeader from './TopHeader';

export default function DashboardLayout() {
  return (
    <SidebarProvider>
      <div style={{ display: 'flex', height: '100vh', width: '100%', backgroundColor: 'var(--bg-app)', overflow: 'hidden' }}>

        {/* 1. Sidebar cố định bên trái */}
        <Sidebar />

        {/* 2. Cột nội dung bên phải (chứa Header + Outlet) */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>

          <TopHeader />

          {/* Outlet là nơi hiển thị nội dung các trang con (Tổng quan, Lịch tuần, v.v.) */}
          <main style={{ flex: 1, padding: '1.5rem', overflowY: 'auto' }}>
            <Outlet />
          </main>

        </div>
      </div>
    </SidebarProvider>
  );
}
