export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const SEVERITY_COLORS = {
  high: 'text-danger bg-danger/10 border-danger/20',
  medium: 'text-warning bg-warning/10 border-warning/20',
  low: 'text-accent bg-accent/10 border-accent/20',
};

export const STATUS_COLORS = {
  online: 'text-primary bg-primary/10 border-primary/20',
  offline: 'text-text_muted bg-surface border-border',
};
