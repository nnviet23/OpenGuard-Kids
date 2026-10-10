import { useState, useRef } from 'react';
import AuthLayout from '../auth-layout';
import { Button } from '../../../shared';
import styles from './otp.module.css';

export default function OtpPage() {
  const [digits, setDigits] = useState(['', '', '', '', '', '']);
  const inputRefs = useRef([]);

  const handleChange = (index, value) => {
    if (!/^[0-9]?$/.test(value)) return;
    const newDigits = [...digits];
    newDigits[index] = value;
    setDigits(newDigits);

    // Tự động focus sang ô tiếp theo khi nhập số
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    // Nhấn Backspace khi ô rỗng -> quay lại ô trước
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const code = digits.join('');
    alert(`Xác thực mã OTP 2FA: ${code}`);
  };

  return (
    <AuthLayout
      title="Two-factor Authentication"
      description="Please enter the authentication code. We have sent the authentication code to your email."
    >
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.otpRow}>
          {/* Cặp 1 */}
          <div className={styles.otpGroup}>
            {[0, 1].map((idx) => (
              <input
                key={idx}
                ref={(el) => (inputRefs.current[idx] = el)}
                type="text"
                maxLength={1}
                className={styles.otpInput}
                value={digits[idx]}
                onChange={(e) => handleChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
              />
            ))}
          </div>

          <span className={styles.hyphen}>—</span>

          {/* Cặp 2 */}
          <div className={styles.otpGroup}>
            {[2, 3].map((idx) => (
              <input
                key={idx}
                ref={(el) => (inputRefs.current[idx] = el)}
                type="text"
                maxLength={1}
                className={styles.otpInput}
                value={digits[idx]}
                onChange={(e) => handleChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
              />
            ))}
          </div>

          <span className={styles.hyphen}>—</span>

          {/* Cặp 3 */}
          <div className={styles.otpGroup}>
            {[4, 5].map((idx) => (
              <input
                key={idx}
                ref={(el) => (inputRefs.current[idx] = el)}
                type="text"
                maxLength={1}
                className={styles.otpInput}
                value={digits[idx]}
                onChange={(e) => handleChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
              />
            ))}
          </div>
        </div>

        <Button type="submit" variant="primary" fullWidth>
          Verify
        </Button>

        <p className={styles.resendNote}>
          Haven't received it?{' '}
          <button type="button" className={styles.resendLink} onClick={() => alert("Đã gửi lại mã!")}>
            Resend a new code..
          </button>
        </p>
      </form>
    </AuthLayout>
  );
}
