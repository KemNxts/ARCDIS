import React from 'react';
import { Input } from '../ui/Input';

export const AttackFilters = ({ filters, onFilterChange }) => {
  return (
    <div className="flex flex-wrap gap-4 mb-6 p-4 bg-surface border border-border rounded-lg">
      <div className="flex-1 min-w-[200px]">
        <Input 
          placeholder="Filter by Technique (e.g. T1059)" 
          value={filters.technique || ''}
          onChange={(e) => onFilterChange({ ...filters, technique: e.target.value })}
        />
      </div>
      <div className="flex-1 min-w-[200px]">
        <Input 
          placeholder="Filter by Agent ID" 
          value={filters.agent_id || ''}
          onChange={(e) => onFilterChange({ ...filters, agent_id: e.target.value })}
        />
      </div>
    </div>
  );
};
