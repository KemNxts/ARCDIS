import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ShieldAlert, Server, Download, Activity } from 'lucide-react';
import { cn } from '../../utils/cn';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Attacks', href: '/attacks', icon: ShieldAlert },
  { name: 'Agents', href: '/agents', icon: Server },
  { name: 'Deploy Agent', href: '/download-agent', icon: Download },
];

export const Sidebar = () => {
  return (
    <div className="flex h-full w-64 flex-col bg-surface border-r border-border">
      <div className="flex h-16 items-center px-6 border-b border-border">
        <Activity className="h-8 w-8 text-primary mr-3" />
        <span className="text-xl font-bold text-text tracking-wide">ARCDIS</span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'group flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-text_muted hover:bg-border/50 hover:text-text'
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  className={cn(
                    'mr-3 h-5 w-5 flex-shrink-0 transition-colors',
                    isActive ? 'text-primary' : 'text-text_muted group-hover:text-text'
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </>
            )}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-border">
        <div className="rounded-md bg-background p-3">
          <p className="text-xs text-text_muted text-center">
            ARCDIS Core v1.0.0
          </p>
        </div>
      </div>
    </div>
  );
};
