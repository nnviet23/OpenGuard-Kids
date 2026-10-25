export const DAYS = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN'];

export function fmtMinutes(min) {
  const m = Math.max(0, Math.round(min || 0));
  return m >= 60 ? `${Math.floor(m / 60)} giờ ${m % 60} phút` : `${m} phút`;
}
export const fmtSeconds = (s) => fmtMinutes((s || 0) / 60);

export function fmtDateTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('vi-VN', { hour12: false, timeZone: 'Asia/Ho_Chi_Minh' });
}

export const ACTION_LABELS = {
  policy_updated: 'Đổi quy tắc', override_granted: 'Cho thêm giờ', lock_now: 'Khóa máy ngay', unlock_now: 'Mở khóa',
  request_decided: 'Trả lời yêu cầu', child_created: 'Tạo hồ sơ trẻ', enroll_code_created: 'Tạo mã cài đặt',
  device_enrolled: 'Cài OpenGuard trên máy', device_revoked: 'Gỡ máy', data_erased: 'Xóa dữ liệu',
  agent_uninstalled: 'Agent tự gỡ khỏi máy', clock_tamper_detected: 'Phát hiện chỉnh đồng hồ máy', viewer_created: 'Tạo tài khoản xem cho trẻ',
};

export const CATEGORY_LABELS = {
  education: 'Giáo dục', entertainment: 'Giải trí', social: 'Mạng xã hội', games: 'Trò chơi',
  inappropriate: 'Không phù hợp lứa tuổi', uncategorized: 'Chưa phân loại',
};
export const ACTION_CHOICES = { allow: 'Cho phép', limit: 'Cho phép có giới hạn', block: 'Chặn', log: 'Cho phép + ghi nhận' };
