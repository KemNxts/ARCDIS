import React from 'react';
import { Badge } from '../ui/Badge';
import { format } from 'date-fns';

export const AttackDetail = ({ attack }) => {
  if (!attack) return null;

  return (
    <div className="space-y-6 text-sm">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h3 className="text-lg font-bold text-text">{attack.technique} - {attack.title}</h3>
          <p className="text-text_muted mt-1">{format(new Date(attack.timestamp), 'PPpp')}</p>
        </div>
        <Badge type="severity" value={attack.severity} className="text-sm px-3 py-1">
          {attack.severity.toUpperCase()}
        </Badge>
      </div>

      <div>
        <h4 className="font-semibold text-text mb-2 text-xs uppercase tracking-wider text-text_muted">Description</h4>
        <p className="text-text leading-relaxed bg-background p-3 rounded-md border border-border">
          {attack.description}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="font-semibold text-text mb-2 text-xs uppercase tracking-wider text-text_muted">Agent ID</h4>
          <p className="font-mono text-accent">{attack.agent_id}</p>
        </div>
        <div>
          <h4 className="font-semibold text-text mb-2 text-xs uppercase tracking-wider text-text_muted">Action Taken</h4>
          <p className="text-primary font-medium">{attack.action_taken}</p>
        </div>
      </div>

      <div>
        <h4 className="font-semibold text-text mb-2 text-xs uppercase tracking-wider text-text_muted">Extracted Features</h4>
        <div className="bg-background rounded-md border border-border overflow-hidden">
          <table className="w-full text-left">
            <tbody className="divide-y divide-border">
              {Object.entries(attack.features).map(([key, value]) => (
                <tr key={key}>
                  <td className="px-3 py-2 font-mono text-text_muted w-1/3">{key}</td>
                  <td className="px-3 py-2 font-mono text-text break-all">
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {attack.raw_summary && (
        <div>
          <h4 className="font-semibold text-text mb-2 text-xs uppercase tracking-wider text-text_muted">Raw Summary</h4>
          <pre className="bg-background p-3 rounded-md border border-border font-mono text-xs text-text_muted whitespace-pre-wrap overflow-x-auto">
            {attack.raw_summary}
          </pre>
        </div>
      )}
    </div>
  );
};
