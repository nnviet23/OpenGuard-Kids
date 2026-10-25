import { useState } from 'react';
import { Check, Send, X } from 'lucide-react';
import api, { errorText } from '../../core/api-client';
import { useAuth } from '../../core/AuthContext';
import { useChild } from '../../core/ChildContext';
import useLoad from '../../core/useLoad';
import { fmtDateTime } from '../../core/format';
import { Button, Card, CardHeader, CardTitle } from '../../shared';

const STATUS = { pending: ['Đang chờ', 'amber'], approved: ['Đã đồng ý', 'green'], denied: ['Chưa đồng ý', 'red'] };

export default function RequestsPage() {
  const { isChildView } = useAuth();
  const { childId, children } = useChild();
  const [filter, setFilter] = useState('pending');
  const [msg, setMsg] = useState(null);
  const [notes, setNotes] = useState({});
  const [mins, setMins] = useState({});
  const [form, setForm] = useState({ kind: 'more_time', minutes: 15, subject: '', message: '' });
  const list = useLoad(() => api.get('/requests', { params: isChildView || filter === 'all' ? {} : { status: filter } }).then((r) => r.data), [filter, isChildView]);
  const nameOf = (id) => children.find((c) => c.id === id)?.name || '';

  const decide = async (r, approve) => {
    setMsg(null);
    try {
      await api.post(`/requests/${r.id}/decide`, { approve, note: notes[r.id] || '', minutes: r.kind === 'more_time' ? Number(mins[r.id] || r.minutes || 15) : null });
      setMsg({ ok: true, text: approve ? 'Đã đồng ý và áp dụng cho máy của trẻ.' : 'Đã từ chối.' });
      list.reload();
    } catch (e) { setMsg({ ok: false, text: errorText(e) }); }
  };
  const send = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      await api.post('/requests', { child_id: childId, kind: form.kind, minutes: form.kind === 'more_time' ? Number(form.minutes) : 0, subject: form.subject, message: form.message });
      setMsg({ ok: true, text: 'Đã gửi cho ba/mẹ.' }); setForm({ ...form, subject: '', message: '' }); list.reload();
    } catch (er) { setMsg({ ok: false, text: errorText(er) }); }
  };

  return (
    <div className="page">
      <h1>{isChildView ? 'Xin thêm giờ / báo chặn nhầm' : 'Yêu cầu từ trẻ'}</h1>
      {msg && <div className={`notice ${msg.ok ? 'ok' : 'err'}`}>{msg.text}</div>}

      {isChildView && <Card><CardHeader><CardTitle>Gửi yêu cầu cho ba/mẹ</CardTitle></CardHeader>
        <form className="stack" onSubmit={send}>
          <div className="field"><label htmlFor="k">Con muốn…</label><select id="k" value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}>
            <option value="more_time">Xin thêm giờ</option><option value="unblock">Báo trang web bị chặn nhầm</option></select></div>
          {form.kind === 'more_time'
            ? <div className="field"><label htmlFor="m">Thêm bao nhiêu phút</label><input id="m" type="number" min={5} max={120} step={5} value={form.minutes} onChange={(e) => setForm({ ...form, minutes: e.target.value })} /></div>
            : <div className="field"><label htmlFor="s">Tên trang web (ví dụ example.com)</label><input id="s" required value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} /></div>}
          <div className="field"><label htmlFor="msg">Lời nhắn</label><input id="msg" maxLength={500} value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} placeholder="Vì sao con cần? (không bắt buộc)" /></div>
          <div><Button type="submit"><Send size={16} /> Gửi</Button></div>
        </form></Card>}

      {!isChildView && <div className="tabs">{[['pending', 'Đang chờ'], ['all', 'Tất cả']].map(([k, l]) => <button key={k} className={filter === k ? 'on' : ''} onClick={() => setFilter(k)}>{l}</button>)}</div>}

      <Card>
        {list.error && <div className="notice err">{list.error}</div>}
        {(list.data || []).length === 0 ? <div className="empty">Không có yêu cầu nào</div> : (
          <div className="stack">{list.data.map((r) => (
            <div key={r.id} className="stack" style={{ padding: '.75rem', border: '1px solid var(--border-subtle)', borderRadius: '.5rem' }}>
              <div className="row between"><b>{!isChildView && `${nameOf(r.child_id)} — `}{r.kind === 'more_time' ? `Xin thêm ${r.minutes} phút` : `Báo chặn nhầm: ${r.subject}`}</b>
                <span className={`chip ${STATUS[r.status][1]}`}>{STATUS[r.status][0]}</span></div>
              <span className="sub">{fmtDateTime(r.created_at)}{r.message ? ` — “${r.message}”` : ''}</span>
              {r.response_note && <span className="sub">Ba/mẹ trả lời: {r.response_note}</span>}
              {!isChildView && r.status === 'pending' && (
                <div className="row">
                  {r.kind === 'more_time' && <input className="txt" style={{ width: '6rem' }} type="number" min={5} max={240} step={5} defaultValue={r.minutes || 15} onChange={(e) => setMins({ ...mins, [r.id]: e.target.value })} aria-label="Số phút cho thêm" />}
                  <input className="txt" style={{ flex: 1, minWidth: '10rem' }} placeholder="Lời nhắn lại (tùy chọn)" onChange={(e) => setNotes({ ...notes, [r.id]: e.target.value })} />
                  <Button onClick={() => decide(r, true)}><Check size={16} /> Đồng ý</Button>
                  <Button variant="outline" onClick={() => decide(r, false)}><X size={16} /> Từ chối</Button>
                </div>)}
            </div>))}</div>)}
      </Card>
    </div>
  );
}
