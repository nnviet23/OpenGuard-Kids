import api from '../../core/api-client';
import { useChild } from '../../core/ChildContext';
import useLoad from '../../core/useLoad';
import { CATEGORY_LABELS, ACTION_CHOICES, fmtDateTime, fmtMinutes } from '../../core/format';
import { Card, CardHeader, CardTitle } from '../../shared';

export default function TodayPage() {
  const { child, childId } = useChild();
  const { data: t, error } = useLoad(() => (childId ? api.get(`/children/${childId}/today`).then((r) => r.data) : null), [childId]);
  if (!child) return <div className="notice">Chưa có hồ sơ trẻ.</div>;
  if (error) return <div className="notice err">{error}</div>;
  if (!t) return <div className="empty">Đang tải…</div>;
  const pct = t.limit_minutes ? Math.min(100, Math.round((t.used_minutes / t.limit_minutes) * 100)) : 0;
  return (
    <div className="page">
      <div><h1>Hôm nay em đã dùng gì?</h1><p className="sub">Đây là đúng những gì ba/mẹ nhìn thấy — không hơn, không kém. ({t.date})</p></div>
      <Card><div className="stack"><div className="row between"><b>Xin chào {t.child_name}!</b><span>{fmtMinutes(t.used_minutes)} / {fmtMinutes(t.limit_minutes)}</span></div>
        <div className={`progress ${pct >= 100 ? 'danger' : pct >= 80 ? 'warn' : ''}`}><span style={{ width: `${pct}%` }} /></div>
        <span className="sub">Còn lại {fmtMinutes(t.remaining_minutes)}{t.bonus_minutes ? ` (đã có +${t.bonus_minutes} phút thưởng)` : ''}</span></div></Card>
      <div className="grid grid-2">
        <Card><CardHeader><CardTitle>Ứng dụng đã mở</CardTitle></CardHeader>{t.apps.length ? <table className="tbl"><tbody>{t.apps.map((a) => <tr key={a.name}><td>{a.name}</td><td style={{ textAlign: 'right' }}>{a.minutes} phút</td></tr>)}</tbody></table> : <div className="empty">Chưa có</div>}</Card>
        <Card><CardHeader><CardTitle>Trang web (chỉ tên miền)</CardTitle></CardHeader>{t.sites.length ? <table className="tbl"><tbody>{t.sites.map((s) => <tr key={s.domain}><td>{s.domain}</td><td style={{ textAlign: 'right' }}>{s.count} lần</td></tr>)}</tbody></table> : <div className="empty">Chưa có</div>}</Card>
      </div>
      <Card><CardHeader><CardTitle>Những lần bị chặn hôm nay</CardTitle></CardHeader>
        {t.blocks.length ? <div className="stack">{t.blocks.map((b, i) => (
          <div key={i} style={{ padding: '.6rem', background: '#fff7ed', borderRadius: '.5rem' }}><b>{b.subject}</b> — {b.why}.<br /><span className="sub">Quy tắc do {b.rule_set_by} đặt{b.rule_set_at ? ` lúc ${fmtDateTime(b.rule_set_at)}` : ''} (phiên bản {b.policy_version}). Nghĩ bị chặn nhầm? Vào “Xin thêm giờ / báo chặn nhầm”.</span></div>))}</div> : <div className="empty">Hôm nay chưa có gì bị chặn</div>}</Card>
      <Card><CardHeader><CardTitle>Quy tắc đang áp dụng</CardTitle></CardHeader>
        <dl className="kv">
          <dt>Ngày thường / cuối tuần</dt><dd>{fmtMinutes(t.rules.weekday_limit_minutes)} / {fmtMinutes(t.rules.weekend_limit_minutes)}</dd>
          <dt>Tìm kiếm an toàn</dt><dd>{t.rules.safesearch ? 'Bật' : 'Tắt'}</dd>
          {Object.entries(t.rules.category_actions).map(([c, a]) => (<><dt key={`k${c}`}>{CATEGORY_LABELS[c]}</dt><dd key={`v${c}`}>{ACTION_CHOICES[a]}</dd></>))}
          <dt>Luôn được phép</dt><dd>{t.rules.safety_whitelist.join(', ')} (trường học, tổng đài 111, khẩn cấp)</dd>
        </dl></Card>
      <Card><CardHeader><CardTitle>OpenGuard KHÔNG ghi lại</CardTitle></CardHeader>
        <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>{t.not_collected.map((x) => <li key={x}>{x}</li>)}</ul>
        <p className="sub" style={{ marginTop: '.5rem' }}>Dữ liệu tự xóa sau 90 ngày. Ba/mẹ có thể xóa toàn bộ dữ liệu của con bất cứ lúc nào.</p></Card>
    </div>
  );
}
