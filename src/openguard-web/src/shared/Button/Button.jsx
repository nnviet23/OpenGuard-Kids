import styles from './Button.module.css';

export default function Button({
  children,
  variant = 'primary',
  fullWidth = false,
  disabled = false,
  type = 'button',
  onClick,
  className = '',
  ...props
}) {
  const combinedClassName = [
    styles.button,
    styles[variant] || styles.primary,
    fullWidth ? styles.fullWidth : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={combinedClassName}
      {...props}
    >
      {children}
    </button>
  );
}
