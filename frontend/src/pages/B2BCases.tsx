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

interface LetterItem {
  letter_id: string;
  letter_type: string;
  created_at: string;
  preview: string;
}

const LETTER_TYPES = [
  { value: 'initial_filing', label: 'Initial Filing' },
  { value: 'rfe_response', label: 'RFE Response' },
  { value: 'appeal', label: 'Appeal' },
  { value: 'withdrawal', label: 'Withdrawal' },
  { value: 'status_inquiry', label: 'Status Inquiry' },
];

export default function B2BCases() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [filter, setFilter] = useState('all');
  const [showModal, setShowModal] = useState(false);
  const [newCase, setNewCase] = useState({ client_name: '', visa_type: 'H-1B', notes: '' });
  const [creating, setCreating] = useState(false);

  // Case detail / letters state
  const [selectedCase, setSelectedCase] = useState<CaseItem | null>(null);
  const [detailTab, setDetailTab] = useState<'info' | 'letters'>('info');
  const [letters, setLetters] = useState<LetterItem[]>([]);
  const [letterContent, setLetterContent] = useState('');
  const [generatingLetter, setGeneratingLetter] = useState(false);
  const [letterType, setLetterType] = useState('initial_filing');
  const [specialInstructions, setSpecialInstructions] = useState('');
  const [loadingLetters, setLoadingLetters] = useState(false);

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

  const openCaseDetail = (c: CaseItem) => {
    setSelectedCase(c);
    setDetailTab('info');
    setLetterContent('');
    setLetters([]);
    fetchLetters(c.case_id);
  };

  const fetchLetters = (caseId: string) => {
    if (!token) return;
    setLoadingLetters(true);
    fetch(`${API_URL}/api/letters/${caseId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => { if (Array.isArray(data)) setLetters(data); })
      .catch(() => {})
      .finally(() => setLoadingLetters(false));
  };

  const generateLetter = async () => {
    if (!selectedCase || !token) return;
    setGeneratingLetter(true);
    setLetterContent('');
    try {
      const res = await fetch(`${API_URL}/api/letters/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ case_id: selectedCase.case_id, letter_type: letterType, special_instructions: specialInstructions || undefined }),
      });
      const data = await res.json();
      if (res.ok && data.content) {
        setLetterContent(data.content);
        fetchLetters(selectedCase.case_id);
      } else {
        setLetterContent(`Error: ${data.detail || 'Failed to generate letter'}`);
      }
    } catch {
      setLetterContent('Error: Failed to connect to server');
    } finally {
      setGeneratingLetter(false);
    }
  };

  const viewLetter = async (letterId: string) => {
    if (!token) return;
    try {
      const res = await fetch(`${API_URL}/api/letters/content/${letterId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) setLetterContent(data.content);
    } catch {}
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(letterContent);
  };

  const downloadTxt = () => {
    const blob = new Blob([letterContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cover-letter-${selectedCase?.case_id || 'letter'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
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
                    onClick={() => openCaseDetail(c)}
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

        {/* Case Detail Modal */}
        {selectedCase && (
          <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
            <div style={{ backgroundColor: '#0f1a2e', border: '1px solid rgba(201,168,76,0.2)', borderRadius: 16, padding: '32px', width: '100%', maxWidth: 700, maxHeight: '85vh', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, color: '#C9A84C', margin: 0 }}>
                  {selectedCase.client_name} — {selectedCase.visa_type}
                </h2>
                <button onClick={() => setSelectedCase(null)} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.5)', fontSize: 20, cursor: 'pointer' }}>✕</button>
              </div>

              {/* Tabs */}
              <div style={{ display: 'flex', gap: 0, marginBottom: 20, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                {(['info', 'letters'] as const).map((tab) => (
                  <button key={tab} onClick={() => setDetailTab(tab)} style={{
                    padding: '10px 20px', background: 'none', border: 'none', borderBottom: detailTab === tab ? '2px solid #C9A84C' : '2px solid transparent',
                    color: detailTab === tab ? '#C9A84C' : 'rgba(255,255,255,0.4)', fontSize: 14, fontWeight: 500, cursor: 'pointer',
                  }}>
                    {tab === 'info' ? 'Case Info' : 'Letters'}
                  </button>
                ))}
              </div>

              {detailTab === 'info' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <div><span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>Case ID</span><br /><span style={{ fontFamily: 'monospace', fontSize: 13 }}>{selectedCase.case_id}</span></div>
                  <div><span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>Status</span><br />
                    <span style={{ display: 'inline-block', padding: '3px 10px', borderRadius: 12, fontSize: 11, fontWeight: 500, backgroundColor: `${STATUS_COLORS[selectedCase.status] || '#6b7280'}22`, color: STATUS_COLORS[selectedCase.status] || '#6b7280', border: `1px solid ${STATUS_COLORS[selectedCase.status] || '#6b7280'}44` }}>
                      {selectedCase.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div><span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>Updated</span><br /><span style={{ fontSize: 13 }}>{selectedCase.updated_at ? new Date(selectedCase.updated_at).toLocaleDateString() : '-'}</span></div>
                  <button onClick={() => navigate(`/app/chat?case=${selectedCase.case_id}`)} style={{ marginTop: 10, padding: '10px 20px', backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer', alignSelf: 'flex-start' }}>
                    Open in Chat
                  </button>
                </div>
              )}

              {detailTab === 'letters' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  {/* Generate */}
                  <div style={{ padding: 16, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 12, border: '1px solid rgba(255,255,255,0.06)' }}>
                    <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 12, color: '#C9A84C' }}>Generate Cover Letter</div>
                    <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
                      <select value={letterType} onChange={(e) => setLetterType(e.target.value)} style={{ ...inputStyle, flex: 1, appearance: 'auto' as any }}>
                        {LETTER_TYPES.map((lt) => <option key={lt.value} value={lt.value}>{lt.label}</option>)}
                      </select>
                    </div>
                    <textarea value={specialInstructions} onChange={(e) => setSpecialInstructions(e.target.value)} placeholder="Special instructions (optional)..." rows={2} style={{ ...inputStyle, resize: 'vertical', marginBottom: 10 }} />
                    <button onClick={generateLetter} disabled={generatingLetter} style={{ padding: '10px 20px', backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer', opacity: generatingLetter ? 0.6 : 1 }}>
                      {generatingLetter ? 'Generating...' : 'Generate Cover Letter'}
                    </button>
                  </div>

                  {/* Generated content */}
                  {letterContent && (
                    <div style={{ padding: 16, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 12, border: '1px solid rgba(255,255,255,0.06)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                        <span style={{ fontSize: 14, fontWeight: 500, color: '#C9A84C' }}>Letter Content</span>
                        <div style={{ display: 'flex', gap: 8 }}>
                          <button onClick={copyToClipboard} style={{ padding: '6px 14px', backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 6, color: '#e2e8f0', fontSize: 12, cursor: 'pointer' }}>Copy</button>
                          <button onClick={downloadTxt} style={{ padding: '6px 14px', backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 6, color: '#e2e8f0', fontSize: 12, cursor: 'pointer' }}>Download .txt</button>
                        </div>
                      </div>
                      <textarea value={letterContent} onChange={(e) => setLetterContent(e.target.value)} rows={15} style={{ ...inputStyle, fontFamily: 'monospace', fontSize: 12, lineHeight: 1.6, resize: 'vertical' }} />
                    </div>
                  )}

                  {/* Previous letters */}
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 10, color: 'rgba(255,255,255,0.5)' }}>Previous Letters</div>
                    {loadingLetters ? (
                      <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 13 }}>Loading...</div>
                    ) : letters.length === 0 ? (
                      <div style={{ color: 'rgba(255,255,255,0.25)', fontSize: 13 }}>No letters generated yet.</div>
                    ) : (
                      letters.map((lt) => (
                        <div key={lt.letter_id} onClick={() => viewLetter(lt.letter_id)} style={{ padding: '10px 14px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 8, border: '1px solid rgba(255,255,255,0.04)', marginBottom: 6, cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)')}
                          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.02)')}
                        >
                          <div>
                            <span style={{ fontSize: 13, fontWeight: 500 }}>{lt.letter_type.replace(/_/g, ' ')}</span>
                            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginLeft: 10 }}>{new Date(lt.created_at).toLocaleDateString()}</span>
                          </div>
                          <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.25)' }}>{lt.letter_id}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

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
