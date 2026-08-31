import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Download, Copy, Terminal, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useApi } from '../hooks/useApi';

export const DownloadAgent = () => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [generatedId, setGeneratedId] = useState(null);
  const api = useApi();

  const handleGenerate = () => {
    // Generate a secure agent ID format
    const randomId = 'agt_' + Math.random().toString(36).substring(2, 15);
    setGeneratedId(randomId);
    toast.success('Agent ID generated!');
  };

  const handleDownload = async () => {
    if (!generatedId) return;
    
    try {
      setIsDownloading(true);
      const token = localStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
      
      const response = await fetch(`${baseUrl}/agents/download?agent_id=${generatedId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to download agent');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'arcdis_agent.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Agent package downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download agent package');
    } finally {
      setIsDownloading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const installCode = `unzip arcdis_agent.zip
cd arcdis_agent
sudo bash install.sh`;

  return (
    <div className="max-w-4xl space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-text">Deploy Agent</h1>
        <p className="text-sm text-text_muted mt-1">Configure and download your pre-configured ARCDIS agent.</p>
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
            <div className="p-4 bg-background border border-primary/50 rounded-lg flex justify-between items-center mb-4">
              <div>
                <p className="text-xs text-text_muted mb-1">Your Unique Agent ID</p>
                <p className="font-mono text-primary font-bold">{generatedId}</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => copyToClipboard(generatedId)}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          )}
          
          {generatedId && (
            <Button onClick={handleDownload} disabled={isDownloading} className="w-full sm:w-auto">
              {isDownloading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
              {isDownloading ? 'Generating Package...' : 'Download ARCDIS Agent'}
            </Button>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>2. Installation Instructions (Ubuntu)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-text_muted">
            Transfer the downloaded <code>arcdis_agent.zip</code> to your target Linux machine and run the following commands:
          </p>
          
          <div className="relative">
            <pre className="bg-background p-4 rounded-lg border border-border text-sm font-mono text-text overflow-x-auto">
              <code>
<span className="text-accent">unzip</span> arcdis_agent.zip{'\n'}
<span className="text-accent">cd</span> arcdis_agent{'\n'}
<span className="text-accent">sudo bash</span> install.sh
              </code>
            </pre>
            <Button 
              variant="ghost" 
              size="icon" 
              className="absolute top-2 right-2 bg-surface/80 hover:bg-surface"
              onClick={() => copyToClipboard(installCode)}
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex items-center text-sm text-primary mt-4 bg-primary/10 p-3 rounded border border-primary/20">
            <Terminal className="h-5 w-5 mr-2 flex-shrink-0" />
            <p>The agent will run continuously in the background as a systemd service and autonomously report to this dashboard.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
