import React, { useEffect, useState } from 'react';
import { AttackTable } from '../components/attacks/AttackTable';
import { AttackFilters } from '../components/attacks/AttackFilters';
import { Modal } from '../components/ui/Modal';
import { AttackDetail } from '../components/attacks/AttackDetail';
import { attackService } from '../services/attackService';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export const Attacks = () => {
  const { data: attacks, execute: fetchAttacks, loading } = useApi(attackService.getAttacks);
  const [filters, setFilters] = useState({ technique: '', agent_id: '' });
  const [selectedAttack, setSelectedAttack] = useState(null);

  useEffect(() => {
    fetchAttacks();
  }, [fetchAttacks]);

  const filteredAttacks = attacks?.filter((attack) => {
    const matchTechnique = attack.technique.toLowerCase().includes((filters.technique || '').toLowerCase());
    const matchAgent = attack.agent_id.toLowerCase().includes((filters.agent_id || '').toLowerCase());
    return matchTechnique && matchAgent;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-text">Attack Telemetry</h1>
        <p className="text-sm text-text_muted mt-1">View and filter mitigated threat events.</p>
      </div>

      <AttackFilters filters={filters} onFilterChange={setFilters} />

      {loading && !attacks ? (
        <LoadingSpinner />
      ) : (
        <AttackTable attacks={filteredAttacks} onRowClick={setSelectedAttack} />
      )}

      <Modal
        isOpen={!!selectedAttack}
        onClose={() => setSelectedAttack(null)}
        title="Attack Details"
      >
        <AttackDetail attack={selectedAttack} />
      </Modal>
    </div>
  );
};
