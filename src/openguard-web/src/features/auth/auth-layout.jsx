import { ShieldCheck } from 'lucide-react';
import styles from './auth-layout.module.css';

export default function AuthLayout({ children, title, description, footerNote }) {
  return (
    <div className={styles.container}>
      {/* Brand Header chuẩn Shadcn (Nằm trên Card) */}
      <div className={styles.brandHeader}>
        <ShieldCheck className={styles.brandIcon} />
        <span>OpenGuard Kids</span>
      </div>

      {/* Main Card */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h1 className={styles.title}>{title}</h1>
          {description && <div className={styles.description}>{description}</div>}
        </div>

        {children}

        {footerNote && (
          <div className={styles.footerNotes}>
            {footerNote}
          </div>
        )}
      </div>
    </div>
  );
}
