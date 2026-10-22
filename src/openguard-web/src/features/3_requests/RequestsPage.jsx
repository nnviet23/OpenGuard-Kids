import React, { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import styles from './RequestsPage.module.css';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import DecisionModal from './components/DecisionModal';
import { IconCheck, IconCross, IconClock, IconAlert } from '../../components/icons/PixelIcons';

const INITIAL_REQUESTS = [
  {
    id: 1,
    time: 'Hôm nay 16:25',
    childId: 'child_1',
    childName: 'Bé Nam Việt',
    device: 'Dell Inspiron 15',
    type: 'time',
    detail: '+30 phút',
    childMsg: 'Con đang làm dở bài tập Scratch nộp cho cô giáo ạ',
    status: 'pending',
    parentReply: null,
  },
  {
    id: 2,
    time: 'Hôm nay 15:40',
    childId: 'child_1',
    childName: 'Bé Nam Việt',
    device: 'Dell Inspiron 15',
    type: 'domain',
    detail: 'wikipedia.org',
    childMsg: 'Con tìm tư liệu Lịch sử lớp 5 bị chặn nhầm ba ơi',
    status: 'pending',
    parentReply: null,
  },
  {
    id: 3,
    time: 'Hôm qua 20:10',
    childId: 'child_2',
    childName: 'Bé Mai Anh',
    device: 'PC Học tập',
    type: 'time',
    detail: '+15 phút',
    childMsg: 'Con xem nốt bài cô hướng dẫn vẽ tranh',
    status: 'approved',
    parentReply: 'Ba cho thêm 15p thôi nhé, 20h30 đi ngủ.',
  },
  {
    id: 4,
    time: 'Hôm qua 19:30',
    childId: 'child_2',
    childName: 'Bé Mai Anh',
    device: 'PC Học tập',
    type: 'domain',
    detail: 'duolingo.com',
    childMsg: 'Con vào học tiếng Anh hằng ngày ạ',
    status: 'approved',
    parentReply: 'Đã thêm vào danh mục Học tập cho phép.',
  },
  {
    id: 5,
    time: '20/10 16:15',
    childId: 'child_1',
    childName: 'Bé Nam Việt',
    device: 'Dell Inspiron 15',
    type: 'domain',
    detail: 'discord.com',
    childMsg: 'Con vào nhóm chat trao đổi game với bạn',
    status: 'rejected',
    parentReply: 'Không mở ứng dụng chat trong giờ tự học.',
  },
];

export default function RequestsPage() {
  const { selectedChild } = useOutletContext();
  const [requests, setRequests] = useState(INITIAL_REQUESTS);
  const [activeTab, setActiveTab] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [filterChild, setFilterChild] = useState('all');
  const [activeModalData, setActiveModalData] = useState(null);

  const pendingCount = requests.filter((r) => r.status === 'pending').length;
  const approvedCount = requests.filter((r) => r.status === 'approved').length;
  const rejectedCount = requests.filter((r) => r.status === 'rejected').length;

  const handleOpenDecision = (req, action) => {
    setActiveModalData({
      id: req.id,
      childName: req.childName,
      device: req.device,
      type: req.type,
      detail: req.detail,
      action,
    });
  };

  const handleConfirmDecision = (id, action, replyNote) => {
    setRequests((prev) =>
      prev.map((r) => {
        if (r.id === id) {
          return {
            ...r,
            status: action === 'approve' ? 'approved' : 'rejected',
            parentReply: replyNote,
          };
        }
        return r;
      })
    );
    setActiveModalData(null);
    alert(`[WebSocket Notification Sent] Đã gửi quyết định ${action.toUpperCase()} tới Agent.`);
  };

  const filteredRequests = requests.filter((r) => {
    const matchTab = activeTab === 'all' || r.status === activeTab;
    const matchType = filterType === 'all' || r.type === filterType;
    const matchChild = filterChild === 'all' || r.childId === filterChild;
    return matchTab && matchType && matchChild;
  });

  return (
    <div>
      <div className={styles.pageHeader}>
        <h2 className={styles.heading}>Yêu cầu từ máy của con</h2>
        <p className={styles.subheading}>
          Hộp thư lắng nghe và phản hồi hai chiều theo triết lý đồng hành (NT3 & NT4). Quyết định sẽ đồng bộ về Tray UI của con[cite: 2, 54].
        </p>
      </div>

      <div className={styles.kpiRow}>
        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Đang chờ xử lý</span>
            <IconAlert color="var(--color-warning)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-warning)' }}>
            {pendingCount}
          </div>
          <div className={styles.kpiBottom}>Cần phản hồi cho bé</div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Đã đồng ý (Tháng này)</span>
            <IconCheck color="var(--color-success)" />
          </div>
          <div className={styles.kpiNum} style={{ color: 'var(--color-success)' }}>
            {approvedCount}
          </div>
          <div className={styles.kpiBottom}>Đã chấp thuận</div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Đã từ chối (Kèm giải thích)</span>
            <IconCross color="var(--color-danger)" />
          </div>
          <div className={styles.kpiNum}>{rejectedCount}</div>
          <div className={styles.kpiBottom}>Có lý do gửi về máy con</div>
        </Card>

        <Card>
          <div className={styles.kpiTop}>
            <span className={styles.kpiTitle}>Thời gian phản hồi TB</span>
            <IconClock color="var(--color-primary)" />
          </div>
          <div className={styles.kpiNum}>
            3.5 <span style={{ fontSize: '1rem', fontWeight: 600 }}>phút</span>
          </div>
          <div className={styles.kpiBottom}>Đồng bộ tức thì qua WebSocket</div>
        </Card>
      </div>

      <Card>
        <div className={styles.filterBar}>
          <div className={styles.tabGroup}>
            <button
              type="button"
              className={`${styles.tabBtn} ${activeTab === 'all' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('all')}
            >
              Tất cả <span className={styles.tabBadge}>{requests.length}</span>
            </button>
            <button
              type="button"
              className={`${styles.tabBtn} ${activeTab === 'pending' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('pending')}
            >
              Chờ duyệt <span className={styles.tabBadge}>{pendingCount}</span>
            </button>
            <button
              type="button"
              className={`${styles.tabBtn} ${activeTab === 'approved' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('approved')}
            >
              Đã đồng ý <span className={styles.tabBadge}>{approvedCount}</span>
            </button>
            <button
              type="button"
              className={`${styles.tabBtn} ${activeTab === 'rejected' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('rejected')}
            >
              Đã từ chối <span className={styles.tabBadge}>{rejectedCount}</span>
            </button>
          </div>

          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <select
              className={styles.select}
              value={filterChild}
              onChange={(e) => setFilterChild(e.target.value)}
            >
              <option value="all">Tất cả các bé</option>
              <option value="child_1">Bé Nam Việt (Dell Inspiron 15)</option>
              <option value="child_2">Bé Mai Anh (PC Học tập)</option>
            </select>

            <select
              className={styles.select}
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">Tất cả loại yêu cầu</option>
              <option value="time">Xin thêm giờ</option>
              <option value="domain">Gỡ chặn tên miền</option>
            </select>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table-box">
            <thead>
              <tr>
                <th style={{ width: 140 }}>Thời gian</th>
                <th style={{ width: 160 }}>Bé gửi</th>
                <th style={{ width: 150 }}>Loại yêu cầu</th>
                <th>Chi tiết & Lời nhắn của con</th>
                <th style={{ width: 120 }}>Trạng thái</th>
                <th style={{ width: 130, textAlign: 'center' }}>Quyết định</th>
              </tr>
            </thead>
            <tbody>
              {filteredRequests.map((req) => (
                <tr key={req.id}>
                  <td className={styles.timeCol}>{req.time}</td>
                  <td>
                    <strong>{req.childName}</strong>
                    <span className={styles.deviceSub}>{req.device}</span>
                  </td>
                  <td>
                    {req.type === 'time' ? (
                      <Badge variant="leisure">⏱️ Xin thêm giờ</Badge>
                    ) : (
                      <Badge variant="study">🌐 Gỡ chặn domain</Badge>
                    )}
                  </td>
                  <td>
                    <strong style={{ fontFamily: 'var(--font-mono)', color: req.type === 'time' ? 'var(--color-primary)' : 'inherit' }}>
                      {req.detail}
                    </strong>
                    <div className={styles.msgBubble}>"{req.childMsg}"</div>
                    {req.parentReply && (
                      <span className={styles.replyText}>
                        💬 Phụ huynh: "{req.parentReply}"
                      </span>
                    )}
                  </td>
                  <td>
                    {req.status === 'pending' && <Badge variant="leisure">Đang chờ</Badge>}
                    {req.status === 'approved' && <Badge variant="ok">Đã đồng ý</Badge>}
                    {req.status === 'rejected' && <Badge variant="block">Đã từ chối</Badge>}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    {req.status === 'pending' ? (
                      <div className={styles.actionBtnGroup}>
                        <button
                          type="button"
                          className={`${styles.btnDecision} ${styles.approve}`}
                          title="Đồng ý"
                          onClick={() => handleOpenDecision(req, 'approve')}
                        >
                          <IconCheck size={14} />
                        </button>
                        <button
                          type="button"
                          className={`${styles.btnDecision} ${styles.reject}`}
                          title="Từ chối"
                          onClick={() => handleOpenDecision(req, 'reject')}
                        >
                          <IconCross size={14} />
                        </button>
                      </div>
                    ) : (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Hoàn tất
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {activeModalData && (
        <DecisionModal
            key={`${activeModalData.id}-${activeModalData.action}`}
            isOpen={Boolean(activeModalData)}
            onClose={() => setActiveModalData(null)}
            data={activeModalData}
            onConfirm={handleConfirmDecision}
        />
        )}
    </div>
  );
}