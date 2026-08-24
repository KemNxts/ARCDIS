import React, { useEffect } from 'react';
import { AgentList } from '../components/agents/AgentList';
import { agentService } from '../services/agentService';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export const Agents = () => {
  const { data: agents, execute: fetchAgents, loading } = useApi(agentService.getAgents);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-text">Managed Agents</h1>
        <p className="text-sm text-text_muted mt-1">Monitor the status of your deployed ARCDIS agents.</p>
      </div>

      {loading && !agents ? (
        <LoadingSpinner />
      ) : (
        <AgentList agents={agents} />
      )}
    </div>
  );
};
