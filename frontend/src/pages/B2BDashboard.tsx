import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import B2BSidebar from '../components/B2BSidebar';

const API_URL = import.meta.env.VITE_BACKEND_URL || '';

interface Stats {
  total: number;
  active: number;
  critical: number;
  pending_review: number;
}

interface CaseItem {
  case_id: string;
  client_name: string;
  visa_type: string;
  status: string;
  deadline_next: string | null;
  deadline_days: number | null;
  updated_at: string;
}

export default function B2BDashboard() {
  const { user, token } = useAuth();
  const [stats, setStats] = useState<Stats>({ total: 0, active: 0, critical: 0, pending_review: 0 });
  const [recentCases, setRecentCases] = useState<CaseItem[]>([]);

  useEffect(() => {
    if (!token) return;
    const headers = { Authorization: `Bearer ${token}` };

    fetch(`${API_URL}/api/cases/stats`, { headers })
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});

    fetch(`${API_URL}/api/cases?limit=5`, { headers })
      .then((r) => r.json())
      .then(setRecentCases)
      .catch(() => {});
  }, [token]);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const metricCards = [
    { label: 'Total Cases', value: stats.total, color: '#C9A84C' },
    { label: 'Active', value: stats.active, color: '#3b82f6' },
    { label: 'Critical', value: stats.critical, color: '#ef4444' },
    { label: 'Pending Review', value: stats.pending_review, color: '#f59e0b' },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#060d14', color: '#e2e8f0' }}>
      <B2BSidebar />
      <main style={{ flex: 1, padding: '32px 40px', overflowY: 'auto' }}>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 26, fontWeight: 500, marginBottom: 8, color: '#fff' }}>
          {greeting()}, {user?.name?.split(' ')[0] || 'there'}
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 14, marginBottom: 32 }}>
          {user?.firm_name} &middot; {user?.plan === 'trial' ? '14-day trial' : user?.plan}
        </p>

        {/* Metric Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 40 }}>
          {metricCards.map((m) => (
            <div
              key={m.label}
              style={{
                backgroundColor: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: 12,
                padding: '20px 24px',
              }}
            >
              <div style={{ fontSize: 32, fontWeight: 700, color: m.color, marginBottom: 4 }}>{m.value}</div>
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)' }}>{m.label}</div>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        <h2 style={{ fontSize: 16, fontWeight: 600, color: 'rgba(255,255,255,0.7)', marginBottom: 16 }}>
          Recent Cases
        </h2>
        {recentCases.length === 0 ? (
          <div
            style={{
              backgroundColor: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: 12,
              padding: '40px',
              textAlign: 'center',
            }}
          >
            <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: 14 }}>
              No cases yet. Go to Cases to create your first one.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recentCases.map((c) => (
              <div
                key={c.case_id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  backgroundColor: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  borderRadius: 10,
                  padding: '14px 20px',
                }}
              >
                <div>
                  <div style={{ fontSize: 14, fontWeight: 500 }}>{c.client_name}</div>
                  <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', marginTop: 2 }}>
                    {c.case_id} &middot; {c.visa_type}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <StatusBadge status={c.status} />
                  {c.deadline_days !== null && c.deadline_days <= 7 && (
                    <div style={{ fontSize: 11, color: '#ef4444', marginTop: 4 }}>
                      {c.deadline_days}d until deadline
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap');
      `}</style>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    intake: '#6b7280',
    docs_pending: '#eab308',
    docs_review: '#f59e0b',
    forms_gen: '#8b5cf6',
    attorney_review: '#f97316',
    ready_to_file: '#3b82f6',
    filed: '#06b6d4',
    rfe_received: '#ef4444',
    rfe_response: '#f59e0b',
    approved: '#22c55e',
    denied: '#ef4444',
    withdrawn: '#6b7280',
  };

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '3px 10px',
        borderRadius: 12,
        fontSize: 11,
        fontWeight: 500,
        backgroundColor: `${colors[status] || '#6b7280'}22`,
        color: colors[status] || '#6b7280',
        border: `1px solid ${colors[status] || '#6b7280'}44`,
      }}
    >
      {status.replace(/_/g, ' ')}
    </span>
  );
}
