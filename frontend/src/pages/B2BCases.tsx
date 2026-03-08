import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import B2BSidebar from '../components/B2BSidebar';

const API_URL = import.meta.env.VITE_BACKEND_URL || '';

interface CaseItem {
  case_id: string;
  client_name: string;
  visa_type: string;
  status: string;
  updated_at: string;
  deadline_next: string | null;
  deadline_days: number | null;
}

const STATUSES = [
  'all', 'intake', 'docs_pending', 'docs_review', 'forms_gen',
  'attorney_review', 'ready_to_file', 'filed',
  'rfe_received', 'rfe_response', 'approved', 'denied', 'withdrawn',
];

const STATUS_COLORS: Record<string, string> = {
  intake: '#6b7280', docs_pending: '#eab308', docs_review: '#f59e0b',
  forms_gen: '#8b5cf6', attorney_review: '#f97316', ready_to_file: '#3b82f6',
  filed: '#06b6d4', rfe_received: '#ef4444', rfe_response: '#f59e0b',
  approved: '#22c55e', denied: '#ef4444', withdrawn: '#6b7280',
};

export default function B2BCases() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [filter, setFilter] = useState('all');
  const [showModal, setShowModal] = useState(false);
  const [newCase, setNewCase] = useState({ client_name: '', visa_type: 'H-1B', notes: '' });
  const [creating, setCreating] = useState(false);

  const fetchCases = () => {
    if (!token) return;
    const params = filter !== 'all' ? `?status=${filter}` : '';
    fetch(`${API_URL}/api/cases${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then(setCases)
      .catch(() => {});
  };

  useEffect(fetchCases, [token, filter]);

  const createCase = async () => {
    setCreating(true);
    try {
      const res = await fetch(`${API_URL}/api/cases`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newCase),
      });
      if (res.ok) {
        setShowModal(false);
        setNewCase({ client_name: '', visa_type: 'H-1B', notes: '' });
        fetchCases();
      }
    } finally {
      setCreating(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '10px 12px',
    backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 8, color: '#e2e8f0', fontSize: 14, boxSizing: 'border-box',
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#060d14', color: '#e2e8f0' }}>
      <B2BSidebar />
      <main style={{ flex: 1, padding: '32px 40px', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 24, fontWeight: 500, color: '#fff', margin: 0 }}>
            Cases
          </h1>
          <button
            onClick={() => setShowModal(true)}
            style={{
              padding: '10px 20px', backgroundColor: '#C9A84C', color: '#060d14',
              border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer',
            }}
          >
            + New Case
          </button>
        </div>

        {/* Filter */}
        <div style={{ display: 'flex', gap: 6, marginBottom: 20, flexWrap: 'wrap' }}>
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              style={{
                padding: '6px 14px', borderRadius: 6, border: 'none', fontSize: 12, cursor: 'pointer',
                backgroundColor: filter === s ? 'rgba(201,168,76,0.2)' : 'rgba(255,255,255,0.04)',
                color: filter === s ? '#C9A84C' : 'rgba(255,255,255,0.4)',
              }}
            >
              {s === 'all' ? 'All' : s.replace(/_/g, ' ')}
            </button>
          ))}
        </div>

        {/* Table */}
        <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px solid rgba(255,255,255,0.06)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                {['Case ID', 'Client', 'Visa', 'Status', 'Updated', 'Deadline'].map((h) => (
                  <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 11, color: 'rgba(255,255,255,0.35)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {cases.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ padding: 40, textAlign: 'center', color: 'rgba(255,255,255,0.25)', fontSize: 14 }}>
                    No cases found. Click "+ New Case" to create one.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr
                    key={c.case_id}
                    onClick={() => navigate(`/app/chat?case=${c.case_id}`)}
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', cursor: 'pointer' }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.03)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <td style={{ padding: '12px 16px', fontSize: 13, fontFamily: 'monospace', color: 'rgba(255,255,255,0.5)' }}>{c.case_id}</td>
                    <td style={{ padding: '12px 16px', fontSize: 14, fontWeight: 500 }}>{c.client_name}</td>
                    <td style={{ padding: '12px 16px', fontSize: 13 }}>{c.visa_type}</td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{
                        display: 'inline-block', padding: '3px 10px', borderRadius: 12, fontSize: 11, fontWeight: 500,
                        backgroundColor: `${STATUS_COLORS[c.status] || '#6b7280'}22`,
                        color: STATUS_COLORS[c.status] || '#6b7280',
                        border: `1px solid ${STATUS_COLORS[c.status] || '#6b7280'}44`,
                      }}>
                        {c.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>
                      {c.updated_at ? new Date(c.updated_at).toLocaleDateString() : '-'}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: 12, color: c.deadline_days !== null && c.deadline_days <= 7 ? '#ef4444' : 'rgba(255,255,255,0.35)' }}>
                      {c.deadline_days !== null ? `${c.deadline_days}d` : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* New Case Modal */}
        {showModal && (
          <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
            <div style={{ backgroundColor: '#0f1a2e', border: '1px solid rgba(201,168,76,0.2)', borderRadius: 16, padding: '32px', width: '100%', maxWidth: 420 }}>
              <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, color: '#C9A84C', marginTop: 0, marginBottom: 20 }}>New Case</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div>
                  <label style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 4, display: 'block' }}>Client Name</label>
                  <input value={newCase.client_name} onChange={(e) => setNewCase({ ...newCase, client_name: e.target.value })} placeholder="Full name" style={inputStyle} />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 4, display: 'block' }}>Visa Type</label>
                  <select
                    value={newCase.visa_type}
                    onChange={(e) => setNewCase({ ...newCase, visa_type: e.target.value })}
                    style={{ ...inputStyle, appearance: 'auto' as any }}
                  >
                    {['H-1B', 'EB-1A', 'EB-2 NIW', 'F-1/OPT', 'B-2 Extension', 'I-130', 'I-765 EAD', 'O-1', 'L-1A', 'L-1B', 'E-2', 'TN', 'Other'].map((v) => (
                      <option key={v} value={v}>{v}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 4, display: 'block' }}>Notes (optional)</label>
                  <textarea value={newCase.notes} onChange={(e) => setNewCase({ ...newCase, notes: e.target.value })} placeholder="Initial notes..." rows={3} style={{ ...inputStyle, resize: 'vertical' }} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
                <button onClick={() => setShowModal(false)} style={{ flex: 1, padding: 12, border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, background: 'none', color: 'rgba(255,255,255,0.5)', fontSize: 14, cursor: 'pointer' }}>Cancel</button>
                <button onClick={createCase} disabled={creating || !newCase.client_name} style={{ flex: 1, padding: 12, backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                  {creating ? 'Creating...' : 'Create Case'}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap');
        input::placeholder, textarea::placeholder { color: rgba(255,255,255,0.25); }
        input:focus, textarea:focus, select:focus { outline: none; border-color: #C9A84C !important; }
      `}</style>
    </div>
  );
}
