import React from 'react';
import { AgentCard } from './AgentCard';

export const AgentList = ({ agents }) => {
  if (!agents || agents.length === 0) {
    return (
      <div className="text-center py-12 bg-surface border border-border rounded-lg">
        <p className="text-text_muted">No agents registered yet.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {agents.map((agent) => (
        <AgentCard key={agent.id} agent={agent} />
      ))}
    </div>
  );
};
