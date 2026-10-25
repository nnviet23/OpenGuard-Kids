import { useEffect, useState } from 'react';
import { KeyRound, Plus, Trash2, UserPlus } from 'lucide-react';
import api, { errorText } from '../../core/api-client';
import { useChild } from '../../core/ChildContext';
import useLoad from '../../core/useLoad';
import { fmtDateTime } from '../../core/format';
import { Badge, Button, Card, CardHeader, CardTitle } from '../../shared';

function EnrollPanel({ childId, onDone }) {
  const [consent, setConsent] = useState({ parent: false, child: false });
  const [code, setCode] = useState(null);
  const [left, setLeft] = useState(0);
  const [err, setErr] = useState('');
  useEffect(() => {
    if (!code) return undefined;
    const t = setInterval(() => setLeft((l) => Math.max(0, l - 1)), 1000);
    return () => clearInterval(t);
  }, [code]);
  const make = async () => {
    setErr('');
    try {
      const { data } = await api.post(`/children/${childId}/enroll-code`, { parent_consent: consent.parent, child_informed: consent.child });
      setCode(data.code); setLeft(data.expires_in);
    } catch (e) { setErr(errorText(e)); }
  };
  return (
    <div className="stack" style={{ marginTop: '.75rem' }}>
      {!code ? (<>
        <label className="row" style={{ gap: '.5rem', alignItems: 'flex-start' }}><input type="checkbox" checked={consent.parent} onChange={(e) => setConsent({ ...consent, parent: e.target.checked })} />
          <span>Tôi là cha/mẹ hoặc người giám hộ hợp pháp của trẻ và <b>đồng ý</b> cho OpenGuard Kids ghi nhận tên ứng dụng, tên miền, thời lượng sử dụng của máy này.</span></label>
        <label className="row" style={{ gap: '.5rem', alignItems: 'flex-start' }}><input type="checkbox" checked={consent.child} onChange={(e) => setConsent({ ...consent, child: e.target.checked })} />
          <span>Tôi đã giải thích cho con về việc này. Con sẽ thấy biểu tượng OpenGuard ở khay hệ thống và xem được mọi dữ liệu được ghi.</span></label>
        {err && <div className="notice err">{err}</div>}
        <div><Button disabled={!consent.parent || !consent.child} onClick={make}><KeyRound size={16} /> Tạo mã cài đặt</Button></div>
      </>) : (<>
        <div className="code-box" aria-live="polite">{code}</div>
        <p className="sub">{left > 0 ? `Mã dùng một lần, còn hiệu lực ${Math.floor(left / 60)}:${String(left % 60).padStart(2, '0')}.` : 'Mã đã hết hạn — hãy tạo mã mới.'}</p>
        <div className="notice">Trên máy Windows của trẻ, chạy:<br /><span className="mono">python main_service.py enroll --code {code} --server https://&lt;địa-chỉ-máy-chủ&gt;/api/v1</span></div>
        <div><Button variant="outline" onClick={() => { setCode(null); setConsent({ parent: false, child: false }); onDone(); }}>Xong</Button></div>
      </>)}
    </div>
  );
}

export default function FamilyPage() {
  const { children, reload: reloadChildren, select } = useChild();
  const devices = useLoad(() => api.get('/devices').then((r) => r.data), []);
  const [name, setName] = useState('');
  const [age, setAge] = useState('6-11');
  const [open, setOpen] = useState(null);
  const [viewer, setViewer] = useState({ id: null, email: '', password: '' });
  const [msg, setMsg] = useState(null);

  const run = async (fn, ok) => { setMsg(null); try { await fn(); if (ok) setMsg({ ok: true, text: ok }); reloadChildren(); devices.reload(); } catch (e) { setMsg({ ok: false, text: errorText(e) }); } };

  return (
    <div className="page">
      <h1>Gia đình & Thiết bị</h1>
      <p className="sub">1 phụ huynh – nhiều trẻ – nhiều thiết bị. Mỗi thiết bị chỉ được cài khi có mã do bạn tạo (bằng chứng bạn đồng ý).</p>
      {msg && <div className={`notice ${msg.ok ? 'ok' : 'err'}`}>{msg.text}</div>}

      <Card><CardHeader><CardTitle>Thêm trẻ</CardTitle></CardHeader>
        <form className="row" onSubmit={(e) => { e.preventDefault(); run(async () => { await api.post('/children', { name, age_group: age }); setName(''); }, 'Đã thêm hồ sơ trẻ'); }}>
          <input className="txt" style={{ maxWidth: '16rem' }} required maxLength={100} placeholder="Tên của con" value={name} onChange={(e) => setName(e.target.value)} aria-label="Tên của con" />
          <select className="sel" style={{ width: 'auto' }} value={age} onChange={(e) => setAge(e.target.value)} aria-label="Nhóm tuổi"><option value="6-11">6–11 tuổi</option><option value="12-15">12–15 tuổi</option><option value="16-17">16–17 tuổi</option></select>
          <Button type="submit"><Plus size={16} /> Thêm</Button></form></Card>

      {children.length === 0 && <div className="empty">Chưa có trẻ nào.</div>}
      {children.map((c) => {
        const devs = (devices.data || []).filter((d) => d.child_id === c.id && d.status === 'active');
        return (
          <Card key={c.id}>
            <CardHeader><CardTitle>{c.name} <span className="chip">{c.age_group} tuổi</span></CardTitle>
              <div className="row"><Button variant="outline" onClick={() => select(c.id)}>Chọn</Button>
                <Button variant="outline" onClick={() => setOpen(open === c.id ? null : c.id)}><KeyRound size={16} /> Thêm thiết bị</Button>
                <Button variant="outline" onClick={() => setViewer({ id: viewer.id === c.id ? null : c.id, email: '', password: '' })}><UserPlus size={16} /> Tài khoản xem cho trẻ</Button></div></CardHeader>
            {devs.length === 0 ? <div className="empty">Chưa có thiết bị</div> : (
              <div className="table-wrap"><table className="tbl"><thead><tr><th>Thiết bị</th><th>Trạng thái</th><th>Lần cuối</th><th>Phiên bản</th><th /></tr></thead><tbody>{devs.map((d) => (
                <tr key={d.id}><td>{d.name}</td><td><Badge status={d.online ? 'online' : 'offline'}>{d.online ? 'Đang kết nối' : 'Ngoại tuyến'}</Badge></td>
                  <td>{fmtDateTime(d.last_seen_at)}</td><td>{d.agent_version || '—'}</td>
                  <td style={{ textAlign: 'right' }}><button className="link-btn" onClick={() => window.confirm(`Gỡ ${d.name}? Máy sẽ không còn bị quản lý.`) && run(() => api.delete(`/devices/${d.id}`), 'Đã gỡ thiết bị')}>Gỡ</button></td></tr>))}</tbody></table></div>)}
            {open === c.id && <EnrollPanel childId={c.id} onDone={() => { setOpen(null); devices.reload(); }} />}
            {viewer.id === c.id && (
              <form className="row" style={{ marginTop: '.75rem' }} onSubmit={(e) => { e.preventDefault(); run(async () => { await api.post(`/children/${c.id}/viewer`, { email: viewer.email, password: viewer.password }); setViewer({ id: null, email: '', password: '' }); }, 'Đã tạo tài khoản xem cho trẻ'); }}>
                <input className="txt" style={{ maxWidth: '15rem' }} type="email" required placeholder="Email của con" value={viewer.email} onChange={(e) => setViewer({ ...viewer, email: e.target.value })} aria-label="Email của con" />
                <input className="txt" style={{ maxWidth: '15rem' }} type="password" required minLength={10} placeholder="Mật khẩu (≥10 ký tự)" value={viewer.password} onChange={(e) => setViewer({ ...viewer, password: e.target.value })} aria-label="Mật khẩu của con" />
                <Button type="submit">Tạo</Button>
                <span className="sub">Con chỉ xem được dữ liệu của chính mình, gửi yêu cầu, và xem nhật ký đổi quy tắc.</span></form>)}
            <div style={{ marginTop: '.75rem' }}><button className="link-btn" style={{ color: 'var(--cisco-danger)' }}
              onClick={() => window.confirm(`Xóa hồ sơ ${c.name} và toàn bộ dữ liệu?`) && run(() => api.delete(`/children/${c.id}`), 'Đã xóa hồ sơ')}><Trash2 size={13} /> Xóa hồ sơ và dữ liệu</button></div>
          </Card>);
      })}
    </div>
  );
}
