import { useState } from 'react';
import { Download, ShieldAlert } from 'lucide-react';
import api, { errorText } from '../../core/api-client';
import { useAuth } from '../../core/AuthContext';
import { useChild } from '../../core/ChildContext';
import { Button, Card, CardHeader, CardTitle } from '../../shared';

export default function SettingsPage() {
  const { account, isParent, reload } = useAuth();
  const { child, childId, reload: reloadChildren } = useChild();
  const [pw, setPw] = useState({ current: '', next: '' });
  const [totp, setTotp] = useState({ secret: null, uri: '', code: '', password: '' });
  const [confirm, setConfirm] = useState('');
  const [msg, setMsg] = useState(null);
  const run = async (fn, ok) => { setMsg(null); try { const r = await fn(); if (ok) setMsg({ ok: true, text: ok }); return r; } catch (e) { setMsg({ ok: false, text: errorText(e) }); return null; } };

  const exportData = async () => {
    const r = await run(() => api.get(`/children/${childId}/export`));
    if (!r) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(r.data, null, 2)], { type: 'application/json' }));
    const a = document.createElement('a'); a.href = url; a.download = `openguard-${child.name}.json`; a.click(); URL.revokeObjectURL(url);
  };

  return (
    <div className="page">
      <h1>Cài đặt & Quyền riêng tư</h1>
      {msg && <div className={`notice ${msg.ok ? 'ok' : 'err'}`}>{msg.text}</div>}
      <Card><CardHeader><CardTitle>Đổi mật khẩu</CardTitle></CardHeader>
        <form className="grid grid-3" onSubmit={async (e) => { e.preventDefault(); if (await run(() => api.post('/auth/password', { current_password: pw.current, new_password: pw.next }), 'Đã đổi mật khẩu; các phiên khác đã bị đăng xuất.')) setPw({ current: '', next: '' }); }}>
          <div className="field"><label htmlFor="p1">Mật khẩu hiện tại</label><input id="p1" type="password" autoComplete="current-password" required value={pw.current} onChange={(e) => setPw({ ...pw, current: e.target.value })} /></div>
          <div className="field"><label htmlFor="p2">Mật khẩu mới (≥10 ký tự)</label><input id="p2" type="password" autoComplete="new-password" required minLength={10} value={pw.next} onChange={(e) => setPw({ ...pw, next: e.target.value })} /></div>
          <div className="field" style={{ justifyContent: 'flex-end' }}><Button type="submit">Đổi mật khẩu</Button></div>
        </form></Card>

      <Card><CardHeader><CardTitle>Xác thực hai lớp (TOTP)</CardTitle><span className={`chip ${account.totp_enabled ? 'green' : 'amber'}`}>{account.totp_enabled ? 'Đang bật' : 'Chưa bật'}</span></CardHeader>
        {!account.totp_enabled ? (totp.secret ? (
          <div className="stack">
            <div className="notice">Thêm khóa này vào ứng dụng xác thực (Google Authenticator, Authy…):<br /><span className="mono">{totp.secret}</span></div>
            <div className="row"><input className="txt" style={{ maxWidth: '10rem' }} inputMode="numeric" maxLength={6} placeholder="Mã 6 số" value={totp.code} onChange={(e) => setTotp({ ...totp, code: e.target.value })} aria-label="Mã 6 số" />
              <Button onClick={async () => { if (await run(() => api.post('/auth/totp/enable', { code: totp.code }), 'Đã bật xác thực hai lớp')) { setTotp({ secret: null, uri: '', code: '', password: '' }); reload(); } }}>Bật</Button></div>
          </div>) : <Button variant="outline" onClick={async () => { const r = await run(() => api.post('/auth/totp/setup')); if (r) setTotp({ ...totp, secret: r.data.secret, uri: r.data.otpauth_uri }); }}>Thiết lập</Button>)
          : <div className="row"><input className="txt" style={{ maxWidth: '14rem' }} type="password" placeholder="Nhập mật khẩu để tắt" value={totp.password} onChange={(e) => setTotp({ ...totp, password: e.target.value })} aria-label="Mật khẩu" />
            <Button variant="outline" onClick={async () => { if (await run(() => api.post('/auth/totp/disable', { code: '', password: totp.password }), 'Đã tắt xác thực hai lớp')) reload(); }}>Tắt</Button></div>}
      </Card>

      {isParent && child && <Card><CardHeader><CardTitle>Dữ liệu của {child.name}</CardTitle></CardHeader>
        <div className="stack">
          <p className="sub" style={{ margin: 0 }}>Chỉ lưu: tên ứng dụng, tên miền, thời lượng, thời điểm. Tự xóa sau 90 ngày. Xem chi tiết trong PRIVACY.md.</p>
          <div><Button variant="outline" onClick={exportData}><Download size={16} /> Tải toàn bộ dữ liệu (JSON)</Button></div>
          <div className="notice err" style={{ display: 'flex', flexDirection: 'column', gap: '.5rem' }}>
            <b><ShieldAlert size={14} /> Xóa toàn bộ dữ liệu của con tôi</b>
            <span>Xóa sự kiện, mức dùng, yêu cầu trên máy chủ và ra lệnh cho các máy xóa bộ nhớ đệm cục bộ. Không thể hoàn tác. Nhật ký thay đổi quy tắc được giữ lại để minh bạch (không chứa dữ liệu sử dụng).</span>
            <div className="row"><input className="txt" style={{ maxWidth: '14rem' }} placeholder="Gõ: XOA DU LIEU" value={confirm} onChange={(e) => setConfirm(e.target.value)} aria-label="Xác nhận xóa" />
              <Button variant="danger" disabled={confirm !== 'XOA DU LIEU'} onClick={async () => { if (await run(() => api.request({ method: 'DELETE', url: `/children/${childId}/data`, data: { confirm } }), 'Đã xóa dữ liệu và gửi lệnh xóa cache tới các máy.')) { setConfirm(''); reloadChildren(); } }}>Xóa vĩnh viễn</Button></div>
          </div>
        </div></Card>}
    </div>
  );
}
