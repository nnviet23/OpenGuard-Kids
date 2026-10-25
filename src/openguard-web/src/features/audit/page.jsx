import { useState } from 'react';
import { Download } from 'lucide-react';
import api from '../../core/api-client';
import { useChild } from '../../core/ChildContext';
import useLoad from '../../core/useLoad';
import { ACTION_LABELS, fmtDateTime } from '../../core/format';
import { Card, CardHeader, CardTitle } from '../../shared';

const TYPES = ['', 'app_start', 'app_stop', 'domain_query', 'blocked_app', 'blocked_domain', 'quota_warning', 'locked', 'unlock_request', 'override_granted'];

function Diff({ oldV, newV }) {
  let o = {}; let n = {};
  try { o = oldV ? JSON.parse(oldV) : {}; n = newV ? JSON.parse(newV) : {}; } catch { /* giữ rỗng */ }
  const keys = Object.keys(n).filter((k) => k !== 'version' && k !== 'seed');
  if (!keys.length) return <span className="sub">—</span>;
  return <div className="stack" style={{ gap: '.15rem' }}>{keys.map((k) => (
    <div key={k} className="mono"><b>{k}</b>: {JSON.stringify(o[k] ?? null).slice(0, 80)} → {JSON.stringify(n[k]).slice(0, 120)}</div>))}</div>;
}

export default function AuditPage() {
  const { child, childId } = useChild();
  const [tab, setTab] = useState('rules');
  const [type, setType] = useState('');
  const rules = useLoad(() => (childId ? api.get(`/children/${childId}/rule-log`).then((r) => r.data) : []), [childId]);
  const events = useLoad(() => (childId && tab === 'events' ? api.get(`/children/${childId}/events`, { params: { limit: 200, type: type || undefined } }).then((r) => r.data) : []), [childId, tab, type]);
  if (!child) return <div className="notice">Chưa có hồ sơ trẻ.</div>;
  return (
    <div className="page">
      <h1>Nhật ký — {child.name}</h1>
      <p className="sub">Ai đổi quy tắc, khi nào, từ địa chỉ IP nào, giá trị cũ → mới. Trẻ cũng xem được nhật ký này. Nhật ký có chuỗi băm chống sửa/xóa lén.</p>
      <div className="tabs"><button className={tab === 'rules' ? 'on' : ''} onClick={() => setTab('rules')}>Thay đổi quy tắc</button><button className={tab === 'events' ? 'on' : ''} onClick={() => setTab('events')}>Sự kiện sử dụng</button></div>
      {tab === 'rules' && <Card><div className="table-wrap">{rules.error && <div className="notice err">{rules.error}</div>}
        {(rules.data || []).length === 0 ? <div className="empty">Chưa có thay đổi</div> : (
          <table className="tbl"><thead><tr><th>Lúc</th><th>Ai</th><th>Hành động</th><th>IP</th><th>Chi tiết (cũ → mới)</th></tr></thead><tbody>{rules.data.map((r) => (
            <tr key={r.id}><td>{fmtDateTime(r.ts)}</td><td>{r.actor}</td><td>{ACTION_LABELS[r.action] || r.action}</td><td className="mono">{r.ip || '—'}</td><td><Diff oldV={r.old} newV={r.new} /></td></tr>))}</tbody></table>)}</div></Card>}
      {tab === 'events' && <Card><CardHeader><CardTitle>Sự kiện (tối đa 200 gần nhất)</CardTitle>
        <div className="row"><select className="sel" style={{ width: 'auto' }} value={type} onChange={(e) => setType(e.target.value)} aria-label="Lọc loại sự kiện">{TYPES.map((t) => <option key={t} value={t}>{t || 'Tất cả loại'}</option>)}</select>
          <a className="link-btn" href={`/api/v1/children/${childId}/events.csv`}><Download size={14} /> Xuất CSV</a></div></CardHeader>
        <div className="table-wrap">{(events.data || []).length === 0 ? <div className="empty">Chưa có sự kiện</div> : (
          <table className="tbl"><thead><tr><th>Lúc</th><th>Loại</th><th>Đối tượng</th><th>Thời lượng</th><th>Quy tắc</th></tr></thead><tbody>{events.data.map((e) => (
            <tr key={e.event_id}><td>{fmtDateTime(e.ts)}</td><td><span className={`chip ${e.type.startsWith('blocked') ? 'red' : ''}`}>{e.type}</span></td><td>{e.subject}</td><td>{e.duration_sec ? `${Math.round(e.duration_sec / 60)} phút` : '—'}</td><td className="mono">{e.policy_id}</td></tr>))}</tbody></table>)}</div></Card>}
    </div>
  );
}
