import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { formatDistanceToNow } from 'date-fns';
import { Shield } from 'lucide-react';

export const RecentAttacks = ({ attacks = [] }) => {
  const recent = attacks.slice(0, 5);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent Mitigations</CardTitle>
      </CardHeader>
      <CardContent>
        {recent.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-text_muted">
            <Shield className="h-8 w-8 mb-2 opacity-50" />
            <p>No recent attacks detected.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {recent.map((attack) => (
              <div key={attack.id} className="flex items-center justify-between p-3 rounded-lg bg-background border border-border">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-text">{attack.technique}</span>
                    <Badge type="severity" value={attack.severity}>{attack.severity.toUpperCase()}</Badge>
                  </div>
                  <p className="text-sm text-text_muted mt-1">{attack.title}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-text_muted">
                    {formatDistanceToNow(new Date(attack.timestamp), { addSuffix: true })}
                  </span>
                  <p className="text-xs text-primary mt-1">{attack.action_taken}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
