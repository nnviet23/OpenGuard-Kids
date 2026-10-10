import { useState } from 'react';
import { Settings as SettingsIcon, User, Lock, ShieldCheck, CheckCircle2, Smartphone } from 'lucide-react';
import { useAuth } from '../../core/AuthContext';
import styles from './settings.module.css';

export default function SettingsPage() {
  const { parent } = useAuth();

  // State Form Đổi Username
  const [username, setUsername] = useState(parent?.email?.split('@')[0] || 'Phụ huynh');
  const [isUsernameSaved, setIsUsernameSaved] = useState(false);

  // State Form Đổi Mật khẩu
  const [passwords, setPasswords] = useState({ current: '', new: '', confirm: '' });
  const [isPasswordSaved, setIsPasswordSaved] = useState(false);

  // State 2FA
  const [is2FaEnabled, setIs2FaEnabled] = useState(false);

  const handleSaveProfile = (e) => {
    e.preventDefault();
    // Call API đổi tên ở đây
    setIsUsernameSaved(true);
    setTimeout(() => setIsUsernameSaved(false), 3000);
  };

  const handleChangePassword = (e) => {
    e.preventDefault();
    if (passwords.new !== passwords.confirm) {
      alert("Mật khẩu mới không khớp!");
      return;
    }
    // Call API đổi mật khẩu ở đây
    setIsPasswordSaved(true);
    setPasswords({ current: '', new: '', confirm: '' });
    setTimeout(() => setIsPasswordSaved(false), 3000);
  };

  const handleToggle2FA = () => {
    // Demo chuyển trạng thái 2FA (Thực tế sẽ mở Modal quét mã QR)
    setIs2FaEnabled(!is2FaEnabled);
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerIcon}><SettingsIcon size={22} /></div>
        <div>
          <h1 className={styles.title}>Cài đặt hệ thống</h1>
          <p className={styles.subtitle}>Quản lý thông tin tài khoản và cấu hình bảo mật của bạn.</p>
        </div>
      </header>

      <div className={styles.contentList}>

        {/* --- Card 1: Thông tin cá nhân --- */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <User size={20} className={styles.cardIcon} />
            <div className={styles.cardTitleWrap}>
              <h2 className={styles.cardTitle}>Thông tin cá nhân</h2>
              <p className={styles.cardDesc}>Cập nhật tên hiển thị trên hệ thống và email liên hệ.</p>
            </div>
          </div>
          <form onSubmit={handleSaveProfile}>
            <div className={styles.cardBody}>
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label className={styles.label}>Tên hiển thị (Username)</label>
                  <input
                    type="text"
                    className={styles.input}
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
                <div className={styles.formGroup}>
                  <label className={styles.label}>Địa chỉ Email</label>
                  <input
                    type="email"
                    className={styles.input}
                    value={parent?.email || 'parent@openguard.com'}
                    disabled
                  />
                </div>
              </div>
            </div>
            <div className={styles.cardFooter}>
              {isUsernameSaved && <span className={styles.successMsg}><CheckCircle2 size={16}/> Đã lưu thông tin</span>}
              <button type="submit" className={styles.btnPrimary}>Lưu thay đổi</button>
            </div>
          </form>
        </div>

        {/* --- Card 2: Đổi mật khẩu --- */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <Lock size={20} className={styles.cardIcon} />
            <div className={styles.cardTitleWrap}>
              <h2 className={styles.cardTitle}>Đổi mật khẩu</h2>
              <p className={styles.cardDesc}>Đảm bảo tài khoản của bạn đang sử dụng mật khẩu mạnh và an toàn.</p>
            </div>
          </div>
          <form onSubmit={handleChangePassword}>
            <div className={styles.cardBody}>
              <div className={styles.formGroup} style={{ maxWidth: '400px' }}>
                <label className={styles.label}>Mật khẩu hiện tại</label>
                <input
                  type="password"
                  className={styles.input}
                  placeholder="Nhập mật khẩu hiện tại"
                  value={passwords.current}
                  onChange={(e) => setPasswords({...passwords, current: e.target.value})}
                  required
                />
              </div>
              <div className={styles.formRow} style={{ marginTop: '0.5rem' }}>
                <div className={styles.formGroup}>
                  <label className={styles.label}>Mật khẩu mới</label>
                  <input
                    type="password"
                    className={styles.input}
                    placeholder="Tối thiểu 8 ký tự"
                    value={passwords.new}
                    onChange={(e) => setPasswords({...passwords, new: e.target.value})}
                    required
                  />
                </div>
                <div className={styles.formGroup}>
                  <label className={styles.label}>Xác nhận mật khẩu mới</label>
                  <input
                    type="password"
                    className={styles.input}
                    placeholder="Nhập lại mật khẩu mới"
                    value={passwords.confirm}
                    onChange={(e) => setPasswords({...passwords, confirm: e.target.value})}
                    required
                  />
                </div>
              </div>
            </div>
            <div className={styles.cardFooter}>
              {isPasswordSaved && <span className={styles.successMsg}><CheckCircle2 size={16}/> Đã cập nhật mật khẩu</span>}
              <button type="submit" className={styles.btnPrimary}>Cập nhật mật khẩu</button>
            </div>
          </form>
        </div>

        {/* --- Card 3: Xác thực 2 bước (2FA) --- */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <ShieldCheck size={20} className={styles.cardIcon} />
            <div className={styles.cardTitleWrap}>
              <h2 className={styles.cardTitle}>Xác thực 2 bước (2FA)</h2>
              <p className={styles.cardDesc}>Thêm một lớp bảo mật phụ bằng ứng dụng Authenticator (Google/Microsoft).</p>
            </div>
          </div>
          <div className={styles.cardBody}>
            <div className={styles.twoFaWrap}>
              <div className={styles.twoFaInfo}>
                <div style={{ backgroundColor: '#fff', padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid var(--border-subtle)' }}>
                  <Smartphone size={24} color="var(--text-muted)" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>Ứng dụng xác thực</div>
                  {is2FaEnabled ? (
                    <span className={`${styles.badge} ${styles.badgeOn}`}><CheckCircle2 size={12}/> Đang Bật</span>
                  ) : (
                    <span className={`${styles.badge} ${styles.badgeOff}`}>Đang Tắt</span>
                  )}
                </div>
              </div>
              <button
                type="button"
                className={is2FaEnabled ? styles.btnOutline : styles.btnPrimary}
                onClick={handleToggle2FA}
              >
                {is2FaEnabled ? 'Tắt 2FA' : 'Thiết lập 2FA'}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
