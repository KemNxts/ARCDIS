import api from '../api/axios';

export const attackService = {
  getAttacks: async (params = {}) => {
    const response = await api.get('/attacks', { params });
    return response.data;
  },
  
  getAttack: async (attackId) => {
    const response = await api.get(`/attacks/${attackId}`);
    return response.data;
  }
};
