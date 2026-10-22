import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './SettingsPage.module.css';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import DeviceList from './components/DeviceList';

export default function SettingsPage() {
  const navigate = useNavigate();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [show2FASetup, setShow2FASetup] = useState(false);
  const [totpVerifyCode, setTotpVerifyCode] = useState('');

  const [isParentPaused, setIsParentPaused] = useState(false);
  const [uninstallPassword, setUninstallPassword] = useState('OpenGuardAdmin@2026');

  const getStrengthLevel = () => {
    if (newPassword.length === 0) return 0;
    if (newPassword.length < 10) return 1;
    if (!/[A-Z]/.test(newPassword)) return 2;
    return 3;
  };
  const strength = getStrengthLevel();

  const handleSavePassword = (e) => {
    e.preventDefault();
    if (!currentPassword) {
      alert('Vui lòng nhập mật khẩu hiện tại!');
      return;
    }
    if (newPassword.length < 10) {
      alert('Mật khẩu mới phải có tối thiểu 10 ký tự theo quy định NIST SP 800-63B!');
      return;
    }
    if (newPassword !== confirmPassword) {
      alert('Xác nhận mật khẩu mới không khớp!');
      return;
    }

    alert('[FastAPI Server Response] Đã băm mật khẩu mới bằng thuật toán Argon2id và lưu thành công!');
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  const handleForgotPw = () => {
    const email = prompt('Nhập địa chỉ email đăng ký phụ huynh để nhận link khôi phục:');
    if (email) {
      alert(`Đã gửi liên kết khôi phục mật khẩu (Hiệu lực 15 phút) đến hòm thư: ${email}`);
    }
  };

  const handleToggle2FA = (checked) => {
    if (checked) {
      setShow2FASetup(true);
    } else {
      if (window.confirm('Bạn có chắc chắn muốn TẮT xác thực 2 yếu tố?')) {
        setIs2FAEnabled(false);
        setShow2FASetup(false);
        alert('Đã tắt tính năng 2FA TOTP.');
      }
    }
  };

  const handleVerify2FA = () => {
    if (totpVerifyCode.trim().length !== 6 || isNaN(totpVerifyCode)) {
      alert('Vui lòng nhập mã TOTP gồm đúng 6 chữ số từ điện thoại!');
      return;
    }
    setIs2FAEnabled(true);
    setShow2FASetup(false);
    alert('[Xác thực 2FA thành công] Thiết bị phụ huynh đã được liên kết TOTP.');
  };

  const handleToggleParentPause = () => {
    if (!isParentPaused) {
      if (window.confirm('Kích hoạt chế độ TẠM NGHỈ 2 GIỜ?\nToàn bộ giới hạn quota và lọc DNS sẽ tạm ngưng. Hệ thống sẽ tự kích hoạt lại sau 2 giờ.')) {
        setIsParentPaused(true);
        alert('[WebSocket Broadcast] Đã phát lệnh PAUSE_ENFORCEMENT (2 hours) xuống toàn bộ máy của trẻ!');
      }
    } else {
      setIsParentPaused(false);
      alert('Đã kết thúc sớm chế độ tạm nghỉ. Mọi quy tắc và quota đã được kích hoạt lại!');
    }
  };

  const handleSaveUninstallPw = () => {
    if (!uninstallPassword.trim()) {
      alert('Mật khẩu gỡ cài đặt không được để trống!');
      return;
    }
    alert('[Policy Updated] Đã cập nhật mật khẩu gỡ cài đặt cục bộ cho Agent trên máy con.');
  };

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div>
      <div className={styles.pageHeader}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 className={styles.heading}>Cấu hình Tài khoản & An toàn Hệ thống</h2>
            <p className={styles.subheading}>
              Tuân thủ tiêu chuẩn NIST SP 800-63B và OWASP ASVS v4 về quản trị danh tính và phiên làm việc.
            </p>
          </div>
          <Button variant="danger" onClick={() => navigate('/login')}>
            Đăng xuất
          </Button>
        </div>
      </div>

      <div className={styles.settingsGrid}>
        <div className={styles.subnav}>
          <button type="button" className={styles.subnavBtn} onClick={() => scrollToSection('sec-password')}>
            <span>🔑</span> Mật khẩu & Xác thực
          </button>
          <button type="button" className={styles.subnavBtn} onClick={() => scrollToSection('sec-2fa')}>
            <span>🛡️</span> Xác thực 2 yếu tố (2FA)
          </button>
          <button type="button" className={styles.subnavBtn} onClick={() => scrollToSection('sec-devices')}>
            <span>💻</span> Quản lý Thiết bị con
          </button>
          <button type="button" className={styles.subnavBtn} onClick={() => scrollToSection('sec-pause')}>
            <span>☕</span> Tạm nghỉ & Gỡ cài đặt
          </button>
        </div>

        <div>
          <div id="sec-password">
            <Card
              className={styles.sectionCard}
              title="Mật khẩu phụ huynh (NIST SP 800-63B)"
              caption="Băm bằng Argon2id/scrypt, tối thiểu 10 ký tự, khóa tạm 15 phút sau 5 lần sai"
              action={<Badge variant="ok">ARGON2ID ACTIVE</Badge>}
            >
              <form onSubmit={handleSavePassword}>
                <div className={styles.formRow}>
                  <div>
                    <div className={styles.labelTitle}>Mật khẩu hiện tại</div>
                    <div className={styles.labelDesc}>Nhập mật khẩu đang dùng để xác thực thay đổi</div>
                  </div>
                  <div>
                    <input
                      type="password"
                      className={styles.input}
                      placeholder="••••••••••••"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                    />
                  </div>
                </div>

                <div className={styles.formRow}>
                  <div>
                    <div className={styles.labelTitle}>Mật khẩu mới</div>
                    <div className={styles.labelDesc}>Tối thiểu 10 ký tự, kết hợp chữ hoa, chữ thường và số</div>
                  </div>
                  <div>
                    <input
                      type="password"
                      className={styles.input}
                      placeholder="Nhập ít nhất 10 ký tự..."
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                    />
                    <div className={styles.strengthBar}>
                      <div className={`${styles.strengthSeg} ${strength >= 1 ? styles.activeWeak : ''}`} />
                      <div className={`${styles.strengthSeg} ${strength >= 2 ? styles.activeMed : ''}`} />
                      <div className={`${styles.strengthSeg} ${strength >= 3 ? styles.activeStr : ''}`} />
                    </div>
                    <div 
                      className={styles.strengthText}
                      style={{
                        color: strength === 1 ? 'var(--color-danger)' : strength === 2 ? 'var(--color-warning)' : strength === 3 ? 'var(--color-success)' : 'var(--text-sub)'
                      }}
                    >
                      {strength === 0 && 'Độ mạnh: Chưa nhập'}
                      {strength === 1 && `Độ mạnh: Yếu (${newPassword.length}/10 ký tự tối thiểu)`}
                      {strength === 2 && 'Độ mạnh: Trung bình (Nên thêm chữ in hoa)'}
                      {strength === 3 && 'Độ mạnh: Rất an toàn (Đáp ứng chuẩn NIST)'}
                    </div>
                  </div>
                </div>

                <div className={styles.formRow}>
                  <div>
                    <div className={styles.labelTitle}>Xác nhận mật khẩu</div>
                    <div className={styles.labelDesc}>Nhập lại chính xác mật khẩu mới</div>
                  </div>
                  <div>
                    <input
                      type="password"
                      className={styles.input}
                      placeholder="••••••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                  </div>
                </div>

                <div className={styles.cardFooterAction}>
                  <Button type="button" variant="secondary" size="sm" onClick={handleForgotPw}>
                    <span>✉️</span> Quên mật khẩu? Gửi link khôi phục
                  </Button>
                  <Button type="submit" variant="primary">
                    Cập nhật mật khẩu mới
                  </Button>
                </div>
              </form>
            </Card>
          </div>

          <div id="sec-2fa">
            <Card
              className={styles.sectionCard}
              title="Xác thực 2 yếu tố (TOTP 2FA)"
              caption="Bảo vệ tài khoản bằng Google Authenticator, Microsoft Authenticator hoặc Authy"
              action={<Badge variant="study">SECURITY BONUS</Badge>}
            >
              <div className={styles.formRow}>
                <div>
                  <div className={styles.labelTitle}>Trạng thái 2FA</div>
                  <div className={styles.labelDesc}>Bắt buộc nhập mã 6 số từ điện thoại khi đăng nhập</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <label className={styles.switch}>
                    <input
                      type="checkbox"
                      checked={is2FAEnabled || show2FASetup}
                      onChange={(e) => handleToggle2FA(e.target.checked)}
                    />
                    <span className={styles.slider} />
                  </label>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, marginLeft: 8 }}>
                    {is2FAEnabled ? 'ĐÃ BẬT (2FA ACTIVE)' : show2FASetup ? 'Đang thiết lập...' : 'Đang Tắt'}
                  </span>
                </div>
              </div>

              {show2FASetup && (
                <div>
                  <div className={styles.totpSetupCard}>
                    <div className={styles.qrBox}>
                      <svg width="60" height="60" viewBox="0 0 24 24" fill="var(--color-primary)">
                        <path d="M3 3h8v8H3V3zm2 2v4h4V5H5zm8-2h8v8h-8V3zm2 2v4h4V5h-4zM3 13h8v8H3v-8zm2 2v4h4v-4H5zm13-2h3v2h-3v-2zm-3 2h2v3h-2v-3zm3 3h3v3h-3v-3zm-5 1h2v2h-2v-2zm2 2h3v1h-3v-1z" />
                      </svg>
                      <span>SCAN TOTP</span>
                    </div>

                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: 700 }}>Bước 1: Quét mã QR bằng ứng dụng Authenticator</div>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '4px 0 8px 0' }}>Hoặc nhập thủ công khóa bí mật:</p>
                      <div className={styles.secretKeyBox}>OGK-SEC-2026-X992-KIDS</div>

                      <div style={{ marginTop: 12 }}>
                        <div style={{ fontSize: '0.8rem', fontWeight: 700, marginBottom: 4 }}>Bước 2: Nhập mã 6 chữ số để kích hoạt:</div>
                        <div style={{ display: 'flex', gap: 8 }}>
                          <input
                            type="text"
                            className={`${styles.input} ${styles.monoInput}`}
                            style={{ maxWidth: 140, textAlign: 'center' }}
                            maxLength={6}
                            placeholder="123456"
                            value={totpVerifyCode}
                            onChange={(e) => setTotpVerifyCode(e.target.value)}
                          />
                          <Button variant="primary" onClick={handleVerify2FA}>
                            Xác nhận & Bật
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className={styles.backupCodesBox}>
                    <div style={{ fontSize: '0.78rem', fontWeight: 700 }}>🔑 Mã dự phòng (Backup Codes) - Lưu trữ nơi an toàn:</div>
                    <div className={styles.backupGrid}>
                      <span>• 8492-1102</span>
                      <span>• 9941-8321</span>
                      <span>• 4402-9912</span>
                      <span>• 7120-4491</span>
                      <span>• 3391-0021</span>
                      <span>• 5591-3829</span>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          </div>

          <div id="sec-devices">
            <Card
              className={styles.sectionCard}
              title="Thiết bị máy tính của trẻ (F4 & F5)"
              caption="Quản lý các máy đang cài OGK-Agent, thu hồi token khi chuyển nhượng thiết bị"
            >
              <DeviceList />
            </Card>
          </div>

          <div id="sec-pause">
            <Card
              className={styles.sectionCard}
              title="Ngoại lệ & Gỡ cài đặt hợp pháp (F4)"
              caption="Hỗ trợ phụ huynh can thiệp tại chỗ mà không cần tắt phần mềm trái phép"
            >
              <div className={styles.formRow}>
                <div>
                  <div className={styles.labelTitle}>Chế độ "Tạm nghỉ" (Parent Pause)</div>
                  <div className={styles.labelDesc}>Tạm dừng toàn bộ quota và lọc DNS trong 2 giờ</div>
                </div>
                <div>
                  <Button
                    variant={isParentPaused ? 'danger' : 'secondary'}
                    onClick={handleToggleParentPause}
                  >
                    <span>{isParentPaused ? '⏸️' : '☕'}</span> {isParentPaused ? 'Tắt chế độ Tạm nghỉ ngay' : 'Kích hoạt Tạm nghỉ 2 giờ'}
                  </Button>
                  <span style={{ fontSize: '0.75rem', color: isParentPaused ? 'var(--color-danger)' : 'var(--text-sub)', display: 'block', marginTop: 4 }}>
                    {isParentPaused ? 'ĐANG TẠM NGHỈ: Còn lại 1 giờ 59 phút' : 'Hiện trạng thái: Kiểm soát bình thường'}
                  </span>
                </div>
              </div>

              <div className={styles.formRow}>
                <div>
                  <div className={styles.labelTitle}>Mật khẩu gỡ cài đặt trên máy trẻ</div>
                  <div className={styles.labelDesc}>Nhập trên máy Windows của con khi muốn gỡ bỏ hoàn toàn Agent</div>
                </div>
                <div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <input
                      type="password"
                      className={styles.input}
                      value={uninstallPassword}
                      onChange={(e) => setUninstallPassword(e.target.value)}
                    />
                    <Button variant="secondary" onClick={handleSaveUninstallPw}>
                      Lưu
                    </Button>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--color-primary)', marginTop: 4 }}>
                    ✓ Ngăn chặn học sinh tự ý gỡ bỏ phần mềm qua Control Panel
                  </div>
                </div>
              </div>

              <div className={styles.formRow}>
                <div>
                  <div className={styles.labelTitle}>Phiên đăng nhập Dashboard</div>
                  <div className={styles.labelDesc}>Cookie HttpOnly, Secure, SameSite=Lax (Hạn 12 giờ)</div>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Phiên của bạn sẽ hết hạn sau: <strong>11 giờ 42 phút</strong>. Mọi thao tác ghi đều được bảo vệ chống CSRF.
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}