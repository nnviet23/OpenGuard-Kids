import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Lock, LockOpen, PlusCircle, RefreshCw } from 'lucide-react';
import api, { errorText } from '../../core/api-client';
import { useChild } from '../../core/ChildContext';
import useLoad from '../../core/useLoad';
import { fmtDateTime, fmtMinutes, fmtSeconds } from '../../core/format';
import { Badge, Button, Card, CardHeader, CardTitle } from '../../shared';

export default function DashboardPage() {
  const { child, childId, loading: childLoading } = useChild();
  const [days, setDays] = useState(7);
  const [msg, setMsg] = useState(null);
  const today = useLoad(() => (childId ? api.get(`/children/${childId}/today`).then((r) => r.data) : null), [childId]);
  const report = useLoad(() => (childId ? api.get(`/children/${childId}/report`, { params: { days } }).then((r) => r.data) : null), [childId, days]);
  const devices = useLoad(() => api.get('/devices').then((r) => r.data), [childId]);
  const reloadAll = () => { today.reload(); report.reload(); devices.reload(); };

  const act = async (fn, okText) => {
    setMsg(null);
    try { await fn(); setMsg({ ok: true, text: okText }); reloadAll(); } catch (e) { setMsg({ ok: false, text: errorText(e) }); }
  };

  if (childLoading) return <div className="empty">Đang tải…</div>;
  if (!child) {
    return (
      <div className="page"><div className="notice">Chưa có hồ sơ trẻ nào. <Link to="/family">Thêm trẻ và cài đặt thiết bị</Link> để bắt đầu.</div></div>
    );
  }
  const t = today.data;
  const pct = t && t.limit_minutes ? Math.min(100, Math.round((t.used_minutes / t.limit_minutes) * 100)) : 0;
  const myDevices = (devices.data || []).filter((d) => d.child_id === childId && d.status === 'active');
  const chart = (report.data?.days || []).map((d) => ({ date: d.date.slice(5), phut: Math.round(d.used_seconds / 60) }));

  return (
    <div className="page">
      <div className="row between">
        <div><h1>Tổng quan của {child.name}</h1><p className="sub">Hôm nay {t?.date} • quy tắc phiên bản {t?.policy_version}</p></div>
        <div className="row">
          <Button variant="outline" onClick={reloadAll}><RefreshCw size={16} /> Làm mới</Button>
          <Button variant="outline" onClick={() => act(() => api.post(`/children/${childId}/grant-time`, { minutes: 15 }), 'Đã cho thêm 15 phút')}><PlusCircle size={16} /> +15 phút</Button>
          <Button variant="danger" onClick={() => act(() => api.post(`/children/${childId}/lock`, { lock: true }), 'Đã gửi lệnh khóa (máy khóa trong vài giây)')}><Lock size={16} /> Khóa ngay</Button>
          <Button variant="outline" onClick={() => act(() => api.post(`/children/${childId}/lock`, { lock: false }), 'Đã mở khóa')}><LockOpen size={16} /> Mở khóa</Button>
        </div>
      </div>
      {msg && <div className={`notice ${msg.ok ? 'ok' : 'err'}`}>{msg.text}</div>}
      {today.error && <div className="notice err">{today.error}</div>}

      <div className="grid grid-4">
        <Card><div className="card-pad stat"><span className="lbl">Đã dùng hôm nay</span><span className="big">{fmtMinutes(t?.used_minutes)}</span>
          <div className={`progress ${pct >= 100 ? 'danger' : pct >= 80 ? 'warn' : ''}`}><span style={{ width: `${pct}%` }} /></div>
          <span className="sub">trên {fmtMinutes(t?.limit_minutes)}{t?.bonus_minutes ? ` (đã gồm +${t.bonus_minutes} phút thưởng)` : ''}</span></div></Card>
        <Card><div className="card-pad stat"><span className="lbl">Còn lại</span><span className="big">{fmtMinutes(t?.remaining_minutes)}</span></div></Card>
        <Card><div className="card-pad stat"><span className="lbl">Lần bị chặn ({days} ngày)</span><span className="big">{report.data?.blocked_total ?? '—'}</span></div></Card>
        <Card><div className="card-pad stat"><span className="lbl">Thiết bị</span>
          {myDevices.length === 0 ? <span className="sub">Chưa có — <Link to="/family">cài đặt</Link></span>
            : myDevices.map((d) => <span key={d.id} className="row" style={{ gap: '.4rem' }}><Badge status={d.online ? 'online' : 'offline'}>{d.name}</Badge></span>)}</div></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Thời gian dùng máy theo ngày (phút)</CardTitle>
          <select className="sel" style={{ width: 'auto' }} value={days} onChange={(e) => setDays(Number(e.target.value))} aria-label="Khoảng thời gian">
            <option value={7}>7 ngày</option><option value={14}>14 ngày</option><option value={30}>30 ngày</option>
          </select></CardHeader>
        <div className="card-pad" style={{ height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chart}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="date" fontSize={12} /><YAxis fontSize={12} width={32} />
              <Tooltip formatter={(v) => [`${v} phút`, 'Đã dùng']} />
              {t && <ReferenceLine y={t.limit_minutes} stroke="#fb3c49" strokeDasharray="4 4" label={{ value: 'Hạn mức hôm nay', fontSize: 11, fill: '#fb3c49', position: 'insideTopRight' }} />}
              <Bar dataKey="phut" fill="#054b85" radius={[4, 4, 0, 0]} isAnimationActive={false} /></BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <div className="grid grid-2">
        <Card><CardHeader><CardTitle>Top 10 ứng dụng</CardTitle></CardHeader><div className="card-pad">
          {report.data?.top_apps?.length ? <table className="tbl"><tbody>{report.data.top_apps.map((a) => (
            <tr key={a.name}><td>{a.name}</td><td style={{ textAlign: 'right' }}>{fmtSeconds(a.seconds)}</td></tr>))}</tbody></table> : <div className="empty">Chưa có dữ liệu</div>}</div></Card>
        <Card><CardHeader><CardTitle>Top 10 tên miền</CardTitle></CardHeader><div className="card-pad">
          {report.data?.top_domains?.length ? <table className="tbl"><tbody>{report.data.top_domains.map((d) => (
            <tr key={d.domain}><td>{d.domain}</td><td style={{ textAlign: 'right' }}>{d.count} lần</td></tr>))}</tbody></table> : <div className="empty">Chưa có dữ liệu</div>}
          <p className="sub" style={{ marginTop: '.5rem' }}>Chỉ lưu tên miền, không lưu địa chỉ đầy đủ.</p></div></Card>
      </div>

      <Card><CardHeader><CardTitle>Những lần bị chặn gần đây</CardTitle></CardHeader><div className="card-pad table-wrap">
        {report.data?.blocks?.length ? (
          <table className="tbl"><thead><tr><th>Lúc</th><th>Mục bị chặn</th><th>Vì sao</th><th>Ai đặt quy tắc</th></tr></thead><tbody>
            {report.data.blocks.slice(0, 15).map((b, i) => (
              <tr key={i}><td>{fmtDateTime(b.ts)}</td><td><b>{b.subject}</b></td><td>{b.why}</td><td>{b.rule_set_by} (v{b.policy_version})</td></tr>))}</tbody></table>
        ) : <div className="empty">Chưa có lần chặn nào 🎉</div>}</div></Card>
    </div>
  );
}
