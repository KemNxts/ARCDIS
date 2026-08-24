import React from 'react';
import { Card, CardContent } from '../ui/Card';
import { ShieldAlert, Server, Activity, ShieldCheck } from 'lucide-react';
import { subDays, isAfter } from 'date-fns';

export const StatsCards = ({ agents = [], attacks = [] }) => {
  const totalAgents = agents.length;
  const activeAgents = agents.filter(a => a.status === 'online').length;
  const totalAttacks = attacks.length;
  
  const yesterday = subDays(new Date(), 1);
  const recentAttacks = attacks.filter(a => isAfter(new Date(a.timestamp), yesterday)).length;

  const stats = [
    {
      title: 'Total Agents',
      value: totalAgents,
      icon: Server,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Active Agents',
      value: activeAgents,
      icon: Activity,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      title: 'Attacks Blocked',
      value: totalAttacks,
      icon: ShieldCheck,
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-500/10',
    },
    {
      title: 'Attacks (24h)',
      value: recentAttacks,
      icon: ShieldAlert,
      color: 'text-danger',
      bgColor: 'bg-danger/10',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, idx) => (
        <Card key={idx}>
          <CardContent className="p-6 flex items-center">
            <div className={`p-3 rounded-xl ${stat.bgColor} mr-4`}>
              <stat.icon className={`h-6 w-6 ${stat.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-text_muted">{stat.title}</p>
              <h3 className="text-2xl font-bold text-text mt-1">{stat.value}</h3>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
