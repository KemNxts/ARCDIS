import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Download, Copy, Terminal } from 'lucide-react';
import toast from 'react-hot-toast';

export const DownloadAgent = () => {
  const [generatedId, setGeneratedId] = useState(null);

  const handleGenerate = () => {
    // In a real app, this might call an API to pre-register an agent and get a token/ID
    const randomId = 'agt_' + Math.random().toString(36).substring(2, 15);
    setGeneratedId(randomId);
    toast.success('Agent ID generated!');
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  return (
    <div className="max-w-4xl space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-text">Deploy Agent</h1>
        <p className="text-sm text-text_muted mt-1">Download and install the ARCDIS agent on your Ubuntu machines.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>1. Generate Agent Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-text_muted mb-4">
            Generate a unique Agent ID to link your new machine to this dashboard.
          </p>
          {!generatedId ? (
            <Button onClick={handleGenerate}>
              <Download className="h-4 w-4 mr-2" />
              Generate Configuration
            </Button>
          ) : (
            <div className="p-4 bg-background border border-primary/50 rounded-lg flex justify-between items-center">
              <div>
                <p className="text-xs text-text_muted mb-1">Your Unique Agent ID</p>
                <p className="font-mono text-primary font-bold">{generatedId}</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => copyToClipboard(generatedId)}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>2. Installation Instructions (Ubuntu)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-text_muted">
            Run the following commands on your target Ubuntu machine to install the ARCDIS agent.
          </p>
          
          <div className="relative">
            <pre className="bg-background p-4 rounded-lg border border-border text-sm font-mono text-text overflow-x-auto">
              <code>
<span className="text-accent">wget</span> https://arcdis.local/releases/agent_install.sh{'\n'}
<span className="text-accent">chmod</span> +x agent_install.sh{'\n'}
<span className="text-accent">sudo</span> ./agent_install.sh --id={generatedId || '&lt;YOUR_AGENT_ID&gt;'}
              </code>
            </pre>
            <Button 
              variant="ghost" 
              size="icon" 
              className="absolute top-2 right-2 bg-surface/80"
              onClick={() => copyToClipboard(`wget https://arcdis.local/releases/agent_install.sh\nchmod +x agent_install.sh\nsudo ./agent_install.sh --id=${generatedId || '<YOUR_AGENT_ID>'}`)}
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex items-center text-sm text-warning mt-4 bg-warning/10 p-3 rounded border border-warning/20">
            <Terminal className="h-5 w-5 mr-2 flex-shrink-0" />
            <p>The agent runs as a systemd service and requires root privileges to monitor system events and enforce mitigations.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
