import styles from './Badge.module.css';

export default function Badge({ children, status = 'online', showDot = true, className = '' }) {
  const statusClass = styles[status] || styles.online;

  return (
    <span className={`${styles.badge} ${statusClass} ${className}`}>
      {showDot && <span className={styles.dot} />}
      {children}
    </span>
  );
}
