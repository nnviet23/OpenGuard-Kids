import React from 'react';
import styles from './Badge.module.css';

export default function Badge({ children, variant = 'ok', className = '' }) {
  const variantClass = styles[variant] || styles.ok;

  return (
    <span className={`${styles.badge} ${variantClass} ${className}`}>
      {children}
    </span>
  );
}