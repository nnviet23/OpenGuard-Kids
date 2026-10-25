import { useState } from 'react';
import { Plus, Save, Trash2 } from 'lucide-react';
import api, { errorText } from '../../core/api-client';
import { useChild } from '../../core/ChildContext';
import useLoad from '../../core/useLoad';
import { ACTION_CHOICES, CATEGORY_LABELS } from '../../core/format';
import { Button, Card, CardHeader, CardTitle } from '../../shared';

export default function RulesPage() {
  const { child, childId } = useChild();
  const { data: policy, error, reload } = useLoad(() => (childId ? api.get(`/children/${childId}/policy`).then((r) => r.data) : null), [childId]);
  if (!child) return <div className="notice">Hãy chọn hoặc thêm một trẻ trước.</div>;
  if (!policy) return error ? <div className="notice err">{error}</div> : <div className="empty">Đang tải…</div>;
  return <Editor key={`${childId}-${policy.version}`} child={child} childId={childId} policy={policy} reload={reload} />;
}

function Editor({ child, childId, policy, reload }) {
  const [f, setF] = useState(() => ({ cats: { ...policy.category_actions }, overrides: { ...policy.domain_overrides },
    apps: policy.app_rules.map((a) => ({ ...a })), safesearch: policy.safesearch }));
  const [tab, setTab] = useState('cat');
  const [msg, setMsg] = useState(null);
  const [dom, setDom] = useState({ domain: '', action: 'block' });
  const [app, setApp] = useState({ name: '', sha256: '', action: 'block', group: '' });
  const [probe, setProbe] = useState({ q: '', res: null });

  const save = async () => {
    setMsg(null);
    try {
      await api.put(`/children/${childId}/policy`, { expected_version: policy.version, category_actions: f.cats, domain_overrides: f.overrides, app_rules: f.apps, safesearch: f.safesearch });
      setMsg({ ok: true, text: 'Đã lưu và gửi tới máy của trẻ.' }); reload();
    } catch (e) { setMsg({ ok: false, text: errorText(e) }); }
  };
  const addDomain = () => {
    const d = dom.domain.trim().toLowerCase().replace(/^https?:\/\//, '').split('/')[0];
    if (!d) return;
    setF({ ...f, overrides: { ...f.overrides, [d]: dom.action } }); setDom({ ...dom, domain: '' });
  };
  const addApp = () => {
    if (!app.name.trim() && !app.sha256.trim()) return;
    const rule = { name: app.name.trim(), action: app.action };
    if (app.sha256.trim()) rule.sha256 = app.sha256.trim().toLowerCase();
    if (app.group) rule.group = app.group;
    setF({ ...f, apps: [...f.apps, rule] }); setApp({ name: '', sha256: '', action: 'block', group: '' });
  };
  const check = async () => {
    try { const { data } = await api.get('/meta/classify', { params: { domain: probe.q } }); setProbe({ ...probe, res: data }); }
    catch (e) { setProbe({ ...probe, res: { error: errorText(e) } }); }
  };

  return (
    <div className="page">
      <div className="row between"><div><h1>Ứng dụng & Website — {child.name}</h1><p className="sub">Mặc định đã áp dụng chính sách cho trẻ 6–11 tuổi.</p></div>
        <Button onClick={save}><Save size={16} /> Lưu thay đổi</Button></div>
      {msg && <div className={`notice ${msg.ok ? 'ok' : 'err'}`}>{msg.text}</div>}
      <div className="tabs" role="tablist">{[['cat', 'Theo nhóm'], ['dom', 'Tên miền riêng'], ['app', 'Ứng dụng'], ['safe', 'An toàn']].map(([k, l]) =>
        <button key={k} className={tab === k ? 'on' : ''} onClick={() => setTab(k)} role="tab">{l}</button>)}</div>

      {tab === 'cat' && <Card><CardHeader><CardTitle>6 nhóm nội dung</CardTitle></CardHeader>
        <table className="tbl"><tbody>{Object.keys(CATEGORY_LABELS).map((c) => (
          <tr key={c}><td>{CATEGORY_LABELS[c]}</td><td style={{ width: '14rem' }}>
            <select className="sel" value={f.cats[c] || 'log'} onChange={(e) => setF({ ...f, cats: { ...f.cats, [c]: e.target.value } })} aria-label={CATEGORY_LABELS[c]}>
              {Object.entries(ACTION_CHOICES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></td></tr>))}</tbody></table>
        <div className="row" style={{ marginTop: '.75rem' }}>
          <input className="txt" style={{ maxWidth: '16rem' }} placeholder="Thử một tên miền, ví dụ roblox.com" value={probe.q} onChange={(e) => setProbe({ q: e.target.value, res: null })} />
          <Button variant="outline" onClick={check}>Kiểm tra</Button>
          {probe.res && (probe.res.error ? <span className="chip red">{probe.res.error}</span> : <span className="chip">{CATEGORY_LABELS[probe.res.category]}{probe.res.whitelisted ? ' • luôn được phép (danh sách an toàn)' : ''}</span>)}</div>
      </Card>}

      {tab === 'dom' && <Card><CardHeader><CardTitle>Tên miền chặn/cho phép riêng</CardTitle></CardHeader>
        <div className="row" style={{ marginBottom: '.75rem' }}>
          <input className="txt" style={{ maxWidth: '18rem' }} placeholder="example.com (chặn cả tên miền con)" value={dom.domain}
            onChange={(e) => setDom({ ...dom, domain: e.target.value })} aria-label="Tên miền" />
          <select className="sel" style={{ width: 'auto' }} value={dom.action} onChange={(e) => setDom({ ...dom, action: e.target.value })} aria-label="Hành động">
            <option value="block">Chặn</option><option value="allow">Cho phép</option></select>
          <Button variant="outline" onClick={addDomain}><Plus size={16} /> Thêm</Button></div>
        {Object.keys(f.overrides).length === 0 ? <div className="empty">Chưa có tên miền riêng</div> :
          <table className="tbl"><tbody>{Object.entries(f.overrides).map(([d, a]) => (
            <tr key={d}><td>{d}</td><td><span className={`chip ${a === 'block' ? 'red' : 'green'}`}>{a === 'block' ? 'Chặn' : 'Cho phép'}</span></td>
              <td style={{ textAlign: 'right' }}><button className="link-btn" aria-label={`Xóa ${d}`} onClick={() => { const o = { ...f.overrides }; delete o[d]; setF({ ...f, overrides: o }); }}><Trash2 size={14} /></button></td></tr>))}</tbody></table>}
        <p className="sub" style={{ marginTop: '.5rem' }}>Chỉ nhập tên miền. Trang của trường (edu.vn), cổng dịch vụ công (gov.vn) và tổng đài 111 luôn được phép, không thể chặn.</p>
      </Card>}

      {tab === 'app' && <Card><CardHeader><CardTitle>Quy tắc ứng dụng (theo tên tệp hoặc SHA-256)</CardTitle></CardHeader>
        <div className="grid grid-4" style={{ marginBottom: '.75rem' }}>
          <div className="field"><label htmlFor="an">Tên tệp</label><input id="an" placeholder="game.exe" value={app.name} onChange={(e) => setApp({ ...app, name: e.target.value })} /></div>
          <div className="field"><label htmlFor="as">SHA-256 (tùy chọn)</label><input id="as" placeholder="64 ký tự hex" value={app.sha256} onChange={(e) => setApp({ ...app, sha256: e.target.value })} /></div>
          <div className="field"><label htmlFor="aa">Hành động</label><select id="aa" value={app.action} onChange={(e) => setApp({ ...app, action: e.target.value })}>
            <option value="block">Chặn</option><option value="limit">Tính vào ngân sách nhóm</option><option value="allow">Cho phép</option></select></div>
          <div className="field"><label htmlFor="ag">Nhóm</label><select id="ag" value={app.group} onChange={(e) => setApp({ ...app, group: e.target.value })}>
            <option value="">—</option>{['games', 'entertainment', 'social', 'education'].map((g) => <option key={g} value={g}>{CATEGORY_LABELS[g]}</option>)}</select></div>
        </div>
        <Button variant="outline" onClick={addApp}><Plus size={16} /> Thêm quy tắc</Button>
        {f.apps.length === 0 ? <div className="empty">Chưa có quy tắc ứng dụng</div> :
          <div className="table-wrap"><table className="tbl"><thead><tr><th>Tên</th><th>SHA-256</th><th>Hành động</th><th>Nhóm</th><th /></tr></thead><tbody>{f.apps.map((a, i) => (
            <tr key={i}><td>{a.name}</td><td className="mono">{a.sha256 ? `${a.sha256.slice(0, 12)}…` : '—'}</td><td>{a.action}</td><td>{CATEGORY_LABELS[a.group] || '—'}</td>
              <td style={{ textAlign: 'right' }}><button className="link-btn" aria-label="Xóa quy tắc" onClick={() => setF({ ...f, apps: f.apps.filter((_, j) => j !== i) })}><Trash2 size={14} /></button></td></tr>))}</tbody></table></div>}
        <p className="sub" style={{ marginTop: '.5rem' }}>Ứng dụng bị chặn khi trùng tên HOẶC trùng mã SHA-256 (đổi tên tệp vẫn bị nhận ra). Con sẽ thấy cửa sổ giải thích vì sao bị chặn và ai đặt quy tắc.</p>
      </Card>}

      {tab === 'safe' && <Card><CardHeader><CardTitle>Tìm kiếm an toàn & danh sách luôn cho phép</CardTitle></CardHeader>
        <label className="row" style={{ gap: '.5rem' }}><input type="checkbox" checked={f.safesearch} onChange={(e) => setF({ ...f, safesearch: e.target.checked })} /> Bật SafeSearch (Google, Bing, YouTube, DuckDuckGo) bằng DNS</label>
        <h2 style={{ marginTop: '1rem' }}>Danh sách an toàn vĩnh viễn (không chỉnh sửa được)</h2>
        <div className="row">{policy.safety_whitelist.map((d) => <span key={d} className="chip green">{d}</span>)}</div>
        <p className="sub" style={{ marginTop: '.5rem' }}>Cổng trường học, tổng đài bảo vệ trẻ em 111 và dịch vụ khẩn cấp không bao giờ bị chặn — kể cả khi hết giờ — để trẻ luôn tìm được sự giúp đỡ.</p>
      </Card>}
    </div>
  );
}
