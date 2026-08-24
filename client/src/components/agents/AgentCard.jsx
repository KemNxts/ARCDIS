import React from 'react';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Server, Terminal, Clock, Activity } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export const AgentCard = ({ agent }) => {
  return (
    <Card className="hover:border-primary/50 transition-colors">
      <CardContent className="p-5">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-background rounded-lg border border-border">
              <Server className="h-5 w-5 text-accent" />
            </div>
            <div>
              <h3 className="font-semibold text-text">{agent.hostname}</h3>
              <p className="text-xs font-mono text-text_muted mt-0.5">{agent.agent_id.slice(0, 12)}...</p>
            </div>
          </div>
          <Badge type="status" value={agent.status}>{agent.status.toUpperCase()}</Badge>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex items-center text-text_muted">
            <Terminal className="h-4 w-4 mr-2" />
            <span>{agent.os_info}</span>
          </div>
          <div className="flex items-center text-text_muted">
            <Activity className="h-4 w-4 mr-2" />
            <span>v{agent.version}</span>
          </div>
          <div className="flex items-center text-text_muted">
            <Clock className="h-4 w-4 mr-2" />
            <span>Seen {formatDistanceToNow(new Date(agent.last_seen), { addSuffix: true })}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
