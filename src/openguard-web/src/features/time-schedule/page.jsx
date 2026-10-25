import { useEffect, useRef, useState } from 'react';
import { Save } from 'lucide-react';
import api, { errorText } from '../../core/api-client';
import { useChild } from '../../core/ChildContext';
import useLoad from '../../core/useLoad';
import { CATEGORY_LABELS, DAYS, fmtDateTime } from '../../core/format';
import { Button, Card, CardHeader, CardTitle } from '../../shared';

const allow = (from, to) => Array.from({ length: 48 }, (_, s) => s >= from * 2 && s < to * 2);
const PRESETS = {
  'Mỗi ngày 06:00–21:00': () => Array.from({ length: 7 }, () => allow(6, 21)),
  'Ngày học 18:00–21:00, cuối tuần 08:00–21:00': () => Array.from({ length: 7 }, (_, d) => (d < 5 ? allow(18, 21) : allow(8, 21))),
  'Cho phép cả ngày': () => Array.from({ length: 7 }, () => Array(48).fill(true)),
  'Chặn cả tuần': () => Array.from({ length: 7 }, () => Array(48).fill(false)),
};
const slotLabel = (s) => `${String(Math.floor(s / 2)).padStart(2, '0')}:${s % 2 ? '30' : '00'}`;

export default function TimeSchedulePage() {
  const { child, childId } = useChild();
  const { data: policy, error, reload } = useLoad(() => (childId ? api.get(`/children/${childId}/policy`).then((r) => r.data) : null), [childId]);
  if (!child) return <div className="notice">Hãy chọn hoặc thêm một trẻ trước.</div>;
  if (!policy) return error ? <div className="notice err">{error}</div> : <div className="empty">Đang tải…</div>;
  return <Editor key={`${childId}-${policy.version}`} child={child} childId={childId} policy={policy} reload={reload} />;
}

function Editor({ child, childId, policy, reload }) {
  const [f, setF] = useState(() => ({ enabled: policy.enabled, weekday: policy.weekday_limit_minutes, weekend: policy.weekend_limit_minutes,
    schedule: policy.schedule.map((d) => [...d]), budgets: { ...policy.group_budgets } }));
  const [msg, setMsg] = useState(null);
  const paint = useRef(null);

  useEffect(() => {
    const up = () => { paint.current = null; };
    window.addEventListener('pointerup', up);
    return () => window.removeEventListener('pointerup', up);
  }, []);

  const setCell = (d, s, v) => setF((cur) => {
    if (cur.schedule[d][s] === v) return cur;
    const schedule = cur.schedule.map((row) => [...row]);
    schedule[d][s] = v;
    return { ...cur, schedule };
  });
  const onDown = (d, s) => (e) => { e.preventDefault(); paint.current = !f.schedule[d][s]; setCell(d, s, paint.current); };
  const onMove = (e) => {
    if (paint.current === null) return;
    const el = document.elementFromPoint(e.clientX, e.clientY);
    if (el?.dataset?.d !== undefined) setCell(Number(el.dataset.d), Number(el.dataset.s), paint.current);
  };

  const save = async () => {
    setMsg(null);
    const group_budgets = Object.fromEntries(Object.entries(f.budgets).filter(([, v]) => v !== '' && v != null).map(([k, v]) => [k, Number(v)]));
    try {
      await api.put(`/children/${childId}/policy`, { expected_version: policy.version, enabled: f.enabled, weekday_limit_minutes: Number(f.weekday),
        weekend_limit_minutes: Number(f.weekend), schedule: f.schedule, group_budgets });
      setMsg({ ok: true, text: 'Đã lưu. Máy của trẻ nhận quy tắc mới trong tối đa 60 giây (thường vài giây).' });
      reload();
    } catch (e) { setMsg({ ok: false, text: errorText(e) }); }
  };

  return (
    <div className="page">
      <div className="row between"><div><h1>Thời gian sử dụng — {child.name}</h1>
        <p className="sub">Phiên bản {policy.version} • sửa lần cuối {fmtDateTime(policy.updated_at)}</p></div>
        <Button onClick={save}><Save size={16} /> Lưu thay đổi</Button></div>
      {msg && <div className={`notice ${msg.ok ? 'ok' : 'err'}`}>{msg.text}</div>}

      <Card><CardHeader><CardTitle>Hạn mức mỗi ngày</CardTitle>
        <label className="row" style={{ gap: '.4rem', fontSize: '.85rem' }}><input type="checkbox" checked={f.enabled} onChange={(e) => setF({ ...f, enabled: e.target.checked })} /> Bật giới hạn</label></CardHeader>
        <div className="grid grid-2">
          <div className="field"><label htmlFor="wd">Ngày thường (phút)</label><input id="wd" type="number" min={0} max={1440} step={5} value={f.weekday} onChange={(e) => setF({ ...f, weekday: e.target.value })} /></div>
          <div className="field"><label htmlFor="we">Cuối tuần (phút)</label><input id="we" type="number" min={0} max={1440} step={5} value={f.weekend} onChange={(e) => setF({ ...f, weekend: e.target.value })} /></div>
        </div>
        <p className="sub" style={{ marginTop: '.5rem' }}>Chỉ tính thời gian thật sự dùng máy — không tính lúc khóa màn hình hoặc không thao tác quá 5 phút. Cảnh báo trước 10, 5, 1 phút; còn 60 giây ân hạn để lưu bài.</p>
      </Card>

      <Card><CardHeader><CardTitle>Khung giờ được phép (mỗi ô 30 phút)</CardTitle></CardHeader>
        <div className="row" style={{ marginBottom: '.75rem' }}>
          {Object.entries(PRESETS).map(([name, fn]) => <Button key={name} variant="outline" onClick={() => setF({ ...f, schedule: fn() })}>{name}</Button>)}
        </div>
        <div className="sched-scroll"><div className="sched" onPointerMove={onMove} role="grid" aria-label="Lịch tuần">
          <div />{Array.from({ length: 24 }, (_, h) => <div key={h} className="hlabel">{h % 3 === 0 ? String(h).padStart(2, '0') : ''}</div>)}
          {f.schedule.map((row, d) => [
            <div key={`l${d}`} className="dlabel">{DAYS[d]}</div>,
            ...row.map((on, s) => <div key={`${d}-${s}`} data-d={d} data-s={s} className={`cell ${on ? 'on' : ''}`}
              title={`${DAYS[d]} ${slotLabel(s)} — ${on ? 'được phép' : 'bị khóa'}`} onPointerDown={onDown(d, s)} />),
          ])}
        </div></div>
        <div className="row" style={{ marginTop: '.5rem' }}><span className="legend"><i style={{ background: 'var(--cisco-success)' }} /> Được phép</span><span className="legend"><i style={{ background: '#e5e7eb' }} /> Bị khóa (máy khóa trong vòng 5 giây khi hết khung)</span>
          <span className="sub">Bấm hoặc kéo ngón tay/chuột để tô.</span></div>
      </Card>

      <Card><CardHeader><CardTitle>Ngân sách theo nhóm ứng dụng (tùy chọn)</CardTitle></CardHeader>
        <div className="grid grid-3">
          {['games', 'entertainment', 'social'].map((g) => (
            <div className="field" key={g}><label htmlFor={`b-${g}`}>{CATEGORY_LABELS[g]} (phút/ngày)</label>
              <input id={`b-${g}`} type="number" min={0} max={1440} placeholder="Không giới hạn riêng" value={f.budgets[g] ?? ''}
                onChange={(e) => setF({ ...f, budgets: { ...f.budgets, [g]: e.target.value } })} /></div>))}
        </div>
        <p className="sub" style={{ marginTop: '.5rem' }}>Áp dụng cho ứng dụng gán nhóm ở mục “Ứng dụng & Website”. Hết ngân sách nhóm → ứng dụng/trang thuộc nhóm đó bị chặn, phần còn lại vẫn dùng được.</p>
      </Card>
    </div>
  );
}
