import React from 'react';
import { Badge } from '../ui/Badge';
import { format } from 'date-fns';
import { Eye } from 'lucide-react';

export const AttackTable = ({ attacks, onRowClick }) => {
  if (!attacks || attacks.length === 0) {
    return (
      <div className="text-center py-10 bg-surface border border-border rounded-lg">
        <p className="text-text_muted">No attacks found matching your criteria.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-surface">
      <table className="w-full text-left text-sm text-text">
        <thead className="bg-background border-b border-border text-text_muted uppercase text-xs">
          <tr>
            <th className="px-4 py-3 font-medium">Timestamp</th>
            <th className="px-4 py-3 font-medium">Technique</th>
            <th className="px-4 py-3 font-medium">Agent</th>
            <th className="px-4 py-3 font-medium">Severity</th>
            <th className="px-4 py-3 font-medium">Action Taken</th>
            <th className="px-4 py-3 font-medium text-right">Details</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {attacks.map((attack) => (
            <tr 
              key={attack.id} 
              className="hover:bg-background/50 transition-colors cursor-pointer group"
              onClick={() => onRowClick(attack)}
            >
              <td className="px-4 py-3 whitespace-nowrap">
                {format(new Date(attack.timestamp), 'yyyy-MM-dd HH:mm:ss')}
              </td>
              <td className="px-4 py-3 font-medium">
                <span className="text-accent">{attack.technique}</span>
              </td>
              <td className="px-4 py-3 font-mono text-xs">{attack.agent_id.slice(0,8)}...</td>
              <td className="px-4 py-3">
                <Badge type="severity" value={attack.severity}>{attack.severity}</Badge>
              </td>
              <td className="px-4 py-3 text-primary">{attack.action_taken}</td>
              <td className="px-4 py-3 text-right">
                <button className="text-text_muted group-hover:text-primary transition-colors">
                  <Eye className="h-4 w-4 inline-block" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
