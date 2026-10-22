import React from 'react';
import styles from './Card.module.css';

export default function Card({ title, caption, action, children, className = '' }) {
  return (
    <div className={`${styles.card} ${className}`}>
      {(title || action) && (
        <div className={styles.header}>
          <div>
            {title && <h3 className={styles.title}>{title}</h3>}
            {caption && <span className={styles.caption}>{caption}</span>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
}