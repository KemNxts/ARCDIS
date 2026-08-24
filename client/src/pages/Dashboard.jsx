import React, { useEffect, useState } from 'react';
import { StatsCards } from '../components/dashboard/StatsCards';
import { AttackChart } from '../components/dashboard/AttackChart';
import { RecentAttacks } from '../components/dashboard/RecentAttacks';
import { agentService } from '../services/agentService';
import { attackService } from '../services/attackService';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export const Dashboard = () => {
  const { data: agents, execute: fetchAgents, loading: loadingAgents } = useApi(agentService.getAgents);
  const { data: attacks, execute: fetchAttacks, loading: loadingAttacks } = useApi(attackService.getAttacks);

  useEffect(() => {
    fetchAgents();
    fetchAttacks();
  }, [fetchAgents, fetchAttacks]);

  const isLoading = loadingAgents || loadingAttacks;

  if (isLoading && (!agents || !attacks)) {
    return <LoadingSpinner size={40} />;
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-text">SOC Overview</h1>
        <p className="text-sm text-text_muted mt-1">Real-time threat monitoring and system status.</p>
      </div>

      <StatsCards agents={agents || []} attacks={attacks || []} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 h-[400px]">
          <AttackChart attacks={attacks || []} />
        </div>
        <div className="h-[400px]">
          <RecentAttacks attacks={attacks || []} />
        </div>
      </div>
    </div>
  );
};
