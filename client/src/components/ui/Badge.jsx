import React from 'react';
import { cn } from '../../utils/cn';
import { SEVERITY_COLORS, STATUS_COLORS } from '../../utils/constants';

export const Badge = ({ children, variant = 'default', className, type, value, ...props }) => {
  let colorClass = 'bg-surface border-border text-text_muted';
  
  if (type === 'severity' && value) {
    colorClass = SEVERITY_COLORS[value.toLowerCase()] || colorClass;
  } else if (type === 'status' && value) {
    colorClass = STATUS_COLORS[value.toLowerCase()] || colorClass;
  }

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        colorClass,
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
