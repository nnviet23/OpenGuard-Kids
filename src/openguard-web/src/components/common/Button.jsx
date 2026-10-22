import React from 'react';
import styles from './Button.module.css';

export default function Button({ 
  children, 
  variant = 'secondary', 
  size = 'md', 
  icon, 
  onClick, 
  className = '', 
  ...props 
}) {
  const variantClass = styles[variant] || styles.secondary;
  const sizeClass = size === 'sm' ? styles.sm : '';

  return (
    <button 
      className={`${styles.btn} ${variantClass} ${sizeClass} ${className}`} 
      onClick={onClick}
      {...props}
    >
      {icon}
      {children}
    </button>
  );
}