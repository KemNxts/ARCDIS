import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';

export const NotFound = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-9xl font-bold text-border">404</h1>
      <h2 className="mt-4 text-2xl font-bold text-text">Page not found</h2>
      <p className="mt-2 text-text_muted">The page you are looking for doesn't exist or has been moved.</p>
      <Link to="/" className="mt-8">
        <Button>Return to Dashboard</Button>
      </Link>
    </div>
  );
};
