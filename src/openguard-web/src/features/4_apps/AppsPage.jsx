import { useState } from 'react';
import styles from './AppsPage.module.css';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import AddRuleModal from './components/AddRuleModal';
import CategoryModal from './components/CategoryModal';
import { IconApps, IconAlert, IconCheck, IconSearch, IconPlus } from '../../components/icons/PixelIcons';

const INITIAL_RULES = [
  {
    id: 1,
    type: 'dns',
    target: 'tongdai111.vn',
    category: 'education',
    hash: null,
    scope: 'global',
    action: 'allow',
    isPermanent: true,
  },
  {
    id: 2,
    type: 'dns',
    target: '*.khanacademy.org',
    category: 'education',
    hash: 'Wildcard Subdomain',
    scope: 'global',
    action: 'allow',
    isPermanent: false,
  },
  {
    id: 3,
    type: 'app',
    target: 'Code.exe',
    subLabel: 'Visual Studio Code',
    category: 'education',
    hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    scope: 'child_1',
    action: 'allow',
    isPermanent: false,
  },
  {
    id: 4,
    type: 'dns',
    target: 'youtube.com',
    subLabel: 'Cưỡng chế SafeSearch CNAME',
    category: 'leisure',
    hash: null,
    scope: 'global',
    action: 'allow',
    isPermanent: false,
  },
  {
    id: 5,
    type: 'dns',
    target: '*.tiktok.com',
    category: 'social',
    hash: 'Wildcard Subdomain',
    scope: 'global',
    action: 'block',
    isPermanent: false,
  },
  {
    id: 6,
    type: 'app',
    target: 'RobloxPlayerBeta.exe',
    subLabel: 'Roblox Game Client',
    category: 'games',
    hash: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
    scope: 'global',
    action: 'block',
    isPermanent: false,
  },
  {
    id: 7,
    type: 'dns',
    target: 'roblox.com',
    category: 'games',
    hash: null,
    scope: 'child_1',
    action: 'block',
    isPermanent: false,
  },
];

const CATEGORY_NAMES = {
  education: 'Giáo dục',
  leisure: 'Giải trí',
  social: 'Mạng xã hội',
  games: 'Trò chơi',
  inappropriate: 'Không phù hợp',
};

export default function AppsPage() {
  const [rules, setRules] = useState(INITIAL_RULES);
  const [scopeFilter, setScopeFilter] = useState('global');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  const [isAddRuleOpen, setIsAddRuleOpen] = useState(false);
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);

  const totalRulesCount = rules.length;
  const blockedRulesCount = rules.filter((r) => r.action === 'block').length;

  const handleToggleRule = (id) => {
    setRules((prev) =>
      prev.map((r) => {
        if (r.id === id && !r.isPermanent) {
          const nextAction = r.action === 'allow' ? 'block' : 'allow';
          return { ...r, action: nextAction };
        }
        return r;
      })
    );
  };

  const handleDeleteRule = (id, target) => {
    if (window.confirm(`Bạn có chắc muốn xóa quy tắc kiểm soát '${target}' không?`)) {
      setRules((prev) => prev.filter((r) => r.id !== id));
    }
  };

  const handleAddRule = (newRule) => {
    setRules((prev) => [newRule, ...prev]);
  };

  const filteredRules = rules.filter((r) => {
    const matchScope = scopeFilter === 'global' ? r.scope === 'global' : (r.scope === 'global' || r.scope === scopeFilter);
    const matchCat = categoryFilter === 'all' || r.category === categoryFilter;
    const matchSearch = !searchQuery || 
      r.target.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (r.hash && r.hash.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchScope && matchCat && matchSearch;
  });

  return (
    <div>
      <div 
        className={styles.scopeBanner} 
        style={{ borderLeftColor: scopeFilter === 'global' ? 'var(--color-secondary)' : 'var(--color-primary)' }}
      >
        <div>
          <span 
            className={styles.scopeIndicator} 
            style={{ color: scopeFilter === 'global' ? 'var(--color-secondary)' : 'var(--color-primary)' }}
          >
            {scopeFilter === 'global' ? '[Chế độ Toàn cục]' : '[Chính sách riêng của máy]'}
          </span>
          <span style={{ marginLeft: 6 }}>
            {scopeFilter === 'global'
              ? 'Mọi thay đổi quy tắc ở đây sẽ áp dụng cho tất cả thiết bị của trẻ.'
              : 'Hiển thị các quy tắc toàn cục kế thừa kèm theo quy tắc cấu hình riêng.'}
          </span>
        </div>
        <Badge variant="ok">POLICY VERSION: v1.5</Badge>
      </div>

      <div className={styles.pageHeader}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 className={styles.heading}>Kiểm soát Ứng dụng & Lọc Tên miền Web</h2>
            <p className={styles.subheading}>
              Chặn website bằng DNS Proxy cục bộ (cấp 2 & wildcard), đối chiếu ứng dụng Windows qua process + SHA-256.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button variant="secondary" onClick={() => setIsCategoryOpen(true)}>
              Quản lý Loại ứng dụng
            </Button>
            <Button variant="primary" icon={<IconPlus />} onClick={() => setIsAddRuleOpen(true)}>
              Thêm tên miền / Ứng dụng
            </Button>
          </div>
        </div>
      </div>

      <div className={styles.kpiRow}>
        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Tổng số quy tắc</span>
            <IconApps color="var(--color-primary)" />
          </div>
          <div className={styles.kpiNum}>{totalRulesCount} mục</div>
          <div className={styles.kpiBottom}>Bao gồm cả DNS và Process Windows</div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Quy tắc đang chặn</span>
            <IconAlert color="var(--color-danger)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-danger)' }}>
            {blockedRulesCount} mục
          </div>
          <div className={styles.kpiBottom}>Trả NXDOMAIN hoặc ngắt tiến trình</div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Cưỡng chế SafeSearch & DoH</span>
            <IconCheck color="var(--color-success)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-success)', fontSize: '1.35rem' }}>
            BẮT BUỘC BẬT
          </div>
          <div className={styles.kpiBottom}>Ánh xạ forcesafesearch & Chặn DoH</div>
        </Card>
      </div>

      <Card>
        <div className={styles.toolbar}>
          <div className={styles.chipsWrap}>
            <button
              type="button"
              className={`${styles.chip} ${categoryFilter === 'all' ? styles.activeChip : ''}`}
              onClick={() => setCategoryFilter('all')}
            >
              Tất cả (6 nhóm)
            </button>
            <button
              type="button"
              className={`${styles.chip} ${categoryFilter === 'education' ? styles.activeChip : ''}`}
              onClick={() => setCategoryFilter('education')}
            >
              Giáo dục
            </button>
            <button
              type="button"
              className={`${styles.chip} ${categoryFilter === 'leisure' ? styles.activeChip : ''}`}
              onClick={() => setCategoryFilter('leisure')}
            >
              Giải trí
            </button>
            <button
              type="button"
              className={`${styles.chip} ${categoryFilter === 'social' ? styles.activeChip : ''}`}
              onClick={() => setCategoryFilter('social')}
            >
              Mạng xã hội
            </button>
            <button
              type="button"
              className={`${styles.chip} ${categoryFilter === 'games' ? styles.activeChip : ''}`}
              onClick={() => setCategoryFilter('games')}
            >
              Trò chơi
            </button>
            <button
              type="button"
              className={`${styles.chip} ${categoryFilter === 'inappropriate' ? styles.activeChip : ''}`}
              onClick={() => setCategoryFilter('inappropriate')}
            >
              Không phù hợp
            </button>
          </div>

          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <select
              value={scopeFilter}
              onChange={(e) => setScopeFilter(e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                background: 'var(--bg-subtle)',
                fontSize: '0.8rem',
                fontWeight: 600,
                outline: 'none',
              }}
            >
              <option value="global">🌐 Toàn bộ trẻ</option>
              <option value="child_1">👤 Bé Nam Việt</option>
              <option value="child_2">👤 Bé Mai Anh</option>
            </select>

            <div className={styles.searchWrap}>
              <IconSearch color="var(--text-muted)" />
              <input
                type="text"
                className={styles.searchInput}
                placeholder="Tìm domain, tiến trình, hash..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table-box">
            <thead>
              <tr>
                <th style={{ width: 110 }}>Loại hình</th>
                <th>Tên miền / Tệp thực thi (Target)</th>
                <th style={{ width: 140 }}>Danh mục</th>
                <th style={{ width: 180 }}>Đối chiếu SHA-256 (App)</th>
                <th style={{ width: 150 }}>Phạm vi</th>
                <th style={{ width: 110 }}>Chính sách</th>
                <th style={{ width: 90, textAlign: 'center' }}>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {filteredRules.map((rule) => (
                <tr key={rule.id}>
                  <td>
                    {rule.type === 'dns' ? (
                      <Badge variant={rule.action === 'allow' ? 'ok' : 'block'}>🌐 DNS</Badge>
                    ) : (
                      <Badge variant={rule.action === 'allow' ? 'study' : 'block'}>💻 App</Badge>
                    )}
                  </td>
                  <td>
                    <strong style={{ fontFamily: 'var(--font-mono)', color: rule.action === 'block' ? 'var(--color-danger)' : 'inherit' }}>
                      {rule.target}
                    </strong>
                    {rule.isPermanent && (
                      <Badge variant="study" style={{ marginLeft: 6, fontSize: '0.65rem' }}>
                        NT6 BẢO VỆ KHẨN CẤP
                      </Badge>
                    )}
                    {rule.subLabel && (
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block' }}>
                        {rule.subLabel}
                      </span>
                    )}
                  </td>
                  <td>
                    <Badge variant={rule.action === 'allow' ? 'study' : 'block'}>
                      {CATEGORY_NAMES[rule.category] || rule.category}
                    </Badge>
                  </td>
                  <td>
                    {rule.hash ? (
                      <span className={styles.sha256Code} title={rule.hash}>
                        {rule.hash.length > 20 ? `${rule.hash.slice(0, 16)}...` : rule.hash}
                      </span>
                    ) : (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-sub)' }}>
                        {rule.type === 'dns' ? '[Hạ tầng DNS]' : 'Chưa có hash'}
                      </span>
                    )}
                  </td>
                  <td>
                    {rule.scope === 'global' ? (
                      <Badge variant="ok">Toàn bộ</Badge>
                    ) : (
                      <Badge variant="leisure">
                        {rule.scope === 'child_1' ? 'Bé Nam Việt' : 'Bé Mai Anh'}
                      </Badge>
                    )}
                  </td>
                  <td>
                    {rule.isPermanent ? (
                      <Badge variant="ok">Miễn chặn vĩnh viễn</Badge>
                    ) : (
                      <label className={styles.switch}>
                        <input
                          type="checkbox"
                          checked={rule.action === 'allow'}
                          onChange={() => handleToggleRule(rule.id)}
                        />
                        <span className={styles.slider} />
                      </label>
                    )}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    {rule.isPermanent ? (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-sub)' }}>Cố định</span>
                    ) : (
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteRule(rule.id, rule.target)}
                      >
                        Xóa
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <AddRuleModal
        isOpen={isAddRuleOpen}
        onClose={() => setIsAddRuleOpen(false)}
        onAddRule={handleAddRule}
      />

      <CategoryModal
        isOpen={isCategoryOpen}
        onClose={() => setIsCategoryOpen(false)}
      />
    </div>
  );
}