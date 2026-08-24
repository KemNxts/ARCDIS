import api from '../api/axios';

export const agentService = {
  getAgents: async () => {
    const response = await api.get('/agents');
    return response.data;
  },
  
  getAgent: async (agentId) => {
    const response = await api.get(`/agents/${agentId}`);
    return response.data;
  }
};
