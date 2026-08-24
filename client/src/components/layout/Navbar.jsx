import React from 'react';
import { LogOut, User } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <div className="sticky top-0 z-10 flex h-16 flex-shrink-0 bg-surface border-b border-border shadow-sm">
      <div className="flex flex-1 items-center justify-between px-6">
        <div className="flex flex-1">
          {/* Breadcrumbs or search could go here */}
        </div>
        <div className="ml-4 flex items-center md:ml-6 space-x-4">
          <div className="flex items-center space-x-2 bg-background px-3 py-1.5 rounded-full border border-border">
            <User className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-text">{user?.full_name || 'Admin'}</span>
          </div>
          <button
            onClick={logout}
            className="rounded-full p-2 text-text_muted hover:bg-danger/10 hover:text-danger transition-colors focus:outline-none"
            title="Sign out"
          >
            <LogOut className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
};
