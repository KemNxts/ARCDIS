import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 24, className }) => {
  return (
    <div className="flex h-full w-full items-center justify-center p-8">
      <Loader2 
        size={size} 
        className={`animate-spin text-primary ${className || ''}`} 
      />
    </div>
  );
};
