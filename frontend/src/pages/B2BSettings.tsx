import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import B2BSidebar from '../components/B2BSidebar';

const API_URL = import.meta.env.VITE_BACKEND_URL || '';

type Tab = 'office' | 'team' | 'whatsapp' | 'telegram';

interface UserItem {
  user_id: string;
  name: string;
  email: string;
  role: string;
  last_login: string | null;
  is_active: boolean;
}

interface WhatsAppEntry {
  phone: string;
  user_name: string;
  role: string;
  added_at: string;
}

interface TelegramEntry {
  chat_id: string;
  user_name: string;
  role: string;
  connected_at: string;
}

interface OfficeData {
  name: string;
  plan: string;
  trial_ends_at: string | null;
  whatsapp_numbers: WhatsAppEntry[];
  telegram_chat_ids: TelegramEntry[];
}

const PLAN_COLORS: Record<string, { bg: string; text: string }> = {
  trial: { bg: 'rgba(234,179,8,0.15)', text: '#eab308' },
  standard: { bg: 'rgba(59,130,246,0.15)', text: '#3b82f6' },
  professional: { bg: 'rgba(201,168,76,0.15)', text: '#C9A84C' },
};

export default function B2BSettings() {
  const { token, user } = useAuth();
  const [tab, setTab] = useState<Tab>('office');
  const [office, setOffice] = useState<OfficeData | null>(null);
  const [officeName, setOfficeName] = useState('');
  const [users, setUsers] = useState<UserItem[]>([]);
  const [saving, setSaving] = useState(false);

  // Invite state
  const [showInvite, setShowInvite] = useState(false);
  const [inviteData, setInviteData] = useState({ email: '', name: '', role: 'paralegal' });
  const [tempPassword, setTempPassword] = useState('');
  const [inviting, setInviting] = useState(false);

  // WhatsApp state
  const [waPhone, setWaPhone] = useState('');
  const [waName, setWaName] = useState('');
  const [waRole, setWaRole] = useState('attorney');
  const [addingWa, setAddingWa] = useState(false);

  // Telegram state
  const [telegramCode, setTelegramCode] = useState('');
  const [telegramExpiry, setTelegramExpiry] = useState('');
  const [generatingCode, setGeneratingCode] = useState(false);

  const headers = useCallback(
    () => ({ 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }),
    [token]
  );

  const fetchOffice = useCallback(() => {
    if (!token) return;
    fetch(`${API_URL}/api/settings/office`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => {
        setOffice(data);
        setOfficeName(data.name || '');
      })
      .catch(() => {});
  }, [token]);

  const fetchUsers = useCallback(() => {
    if (!token) return;
    fetch(`${API_URL}/api/settings/users`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => { if (Array.isArray(data)) setUsers(data); })
      .catch(() => {});
  }, [token]);

  useEffect(() => {
    fetchOffice();
    fetchUsers();
  }, [fetchOffice, fetchUsers]);

  const saveOfficeName = async () => {
    setSaving(true);
    try {
      await fetch(`${API_URL}/api/settings/office`, {
        method: 'PATCH',
        headers: headers(),
        body: JSON.stringify({ name: officeName }),
      });
      fetchOffice();
    } finally {
      setSaving(false);
    }
  };

  const inviteUser = async () => {
    setInviting(true);
    setTempPassword('');
    try {
      const res = await fetch(`${API_URL}/api/settings/users/invite`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(inviteData),
      });
      const data = await res.json();
      if (res.ok) {
        setTempPassword(data.temp_password);
        fetchUsers();
      }
    } finally {
      setInviting(false);
    }
  };

  const deactivateUser = async (userId: string) => {
    if (!confirm('Deactivate this user?')) return;
    await fetch(`${API_URL}/api/settings/users/${userId}`, {
      method: 'DELETE',
      headers: headers(),
    });
    fetchUsers();
  };

  const addWhatsApp = async () => {
    setAddingWa(true);
    try {
      await fetch(`${API_URL}/api/settings/whatsapp/add`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ phone: waPhone, user_name: waName, role: waRole }),
      });
      setWaPhone('');
      setWaName('');
      fetchOffice();
    } finally {
      setAddingWa(false);
    }
  };

  const removeWhatsApp = async (phone: string) => {
    await fetch(`${API_URL}/api/settings/whatsapp/${phone}`, {
      method: 'DELETE',
      headers: headers(),
    });
    fetchOffice();
  };

  const generateTelegramCode = async () => {
    setGeneratingCode(true);
    try {
      const res = await fetch(`${API_URL}/api/settings/telegram/invite-code`, {
        method: 'POST',
        headers: headers(),
      });
      const data = await res.json();
      if (res.ok) {
        setTelegramCode(data.code);
        setTelegramExpiry(data.expires_at);
        setTimeout(() => { setTelegramCode(''); setTelegramExpiry(''); }, 60000);
      }
    } finally {
      setGeneratingCode(false);
    }
  };

  const removeTelegram = async (chatId: string) => {
    await fetch(`${API_URL}/api/settings/telegram/${chatId}`, {
      method: 'DELETE',
      headers: headers(),
    });
    fetchOffice();
  };

  const isOwner = user?.role === 'owner';

  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '10px 12px',
    backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 8, color: '#e2e8f0', fontSize: 14, boxSizing: 'border-box',
  };

  const planColors = PLAN_COLORS[office?.plan || 'trial'] || PLAN_COLORS.trial;

  const tabs: { key: Tab; label: string }[] = [
    { key: 'office', label: 'Office' },
    { key: 'team', label: 'Team' },
    { key: 'whatsapp', label: 'WhatsApp' },
    { key: 'telegram', label: 'Telegram' },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#060d14', color: '#e2e8f0' }}>
      <B2BSidebar />
      <main style={{ flex: 1, padding: '32px 40px', overflowY: 'auto' }}>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 24, fontWeight: 500, color: '#fff', margin: 0, marginBottom: 24 }}>
          Settings
        </h1>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 0, marginBottom: 24, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          {tabs.map((t) => (
            <button key={t.key} onClick={() => setTab(t.key)} style={{
              padding: '10px 20px', background: 'none', border: 'none',
              borderBottom: tab === t.key ? '2px solid #C9A84C' : '2px solid transparent',
              color: tab === t.key ? '#C9A84C' : 'rgba(255,255,255,0.4)',
              fontSize: 14, fontWeight: 500, cursor: 'pointer',
            }}>
              {t.label}
            </button>
          ))}
        </div>

        {/* OFFICE TAB */}
        {tab === 'office' && office && (
          <div style={{ maxWidth: 500, display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div>
              <label style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 4, display: 'block' }}>Office Name</label>
              <div style={{ display: 'flex', gap: 8 }}>
                <input value={officeName} onChange={(e) => setOfficeName(e.target.value)} style={{ ...inputStyle, flex: 1 }} disabled={!isOwner} />
                {isOwner && (
                  <button onClick={saveOfficeName} disabled={saving} style={{ padding: '10px 20px', backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                    {saving ? '...' : 'Save'}
                  </button>
                )}
              </div>
            </div>

            <div>
              <label style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 4, display: 'block' }}>Plan</label>
              <span style={{ display: 'inline-block', padding: '4px 14px', borderRadius: 12, fontSize: 12, fontWeight: 600, backgroundColor: planColors.bg, color: planColors.text, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                {office.plan}
              </span>
              {office.trial_ends_at && (
                <span style={{ marginLeft: 10, fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
                  Trial ends {new Date(office.trial_ends_at).toLocaleDateString()}
                </span>
              )}
            </div>

            <button style={{ alignSelf: 'flex-start', padding: '10px 20px', border: '1px solid rgba(201,168,76,0.3)', borderRadius: 8, background: 'none', color: '#C9A84C', fontSize: 14, cursor: 'pointer' }}>
              Upgrade Plan
            </button>
          </div>
        )}

        {/* TEAM TAB */}
        {tab === 'team' && (
          <div style={{ maxWidth: 700 }}>
            {isOwner && (
              <button onClick={() => { setShowInvite(true); setTempPassword(''); setInviteData({ email: '', name: '', role: 'paralegal' }); }} style={{ marginBottom: 16, padding: '10px 20px', backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                + Invite Member
              </button>
            )}

            <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px solid rgba(255,255,255,0.06)', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                    {['Name', 'Email', 'Role', 'Last Login', 'Actions'].map((h) => (
                      <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 11, color: 'rgba(255,255,255,0.35)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: 0.5 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.user_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', opacity: u.is_active ? 1 : 0.4 }}>
                      <td style={{ padding: '12px 16px', fontSize: 14, fontWeight: 500 }}>{u.name}</td>
                      <td style={{ padding: '12px 16px', fontSize: 13, color: 'rgba(255,255,255,0.5)' }}>{u.email}</td>
                      <td style={{ padding: '12px 16px', fontSize: 13, textTransform: 'capitalize' }}>{u.role}</td>
                      <td style={{ padding: '12px 16px', fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>
                        {u.last_login ? new Date(u.last_login).toLocaleDateString() : 'Never'}
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        {isOwner && u.is_active && u.user_id !== user?.user_id && (
                          <button onClick={() => deactivateUser(u.user_id)} style={{ padding: '4px 10px', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 6, background: 'none', color: '#ef4444', fontSize: 11, cursor: 'pointer' }}>
                            Deactivate
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Invite Modal */}
            {showInvite && (
              <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                <div style={{ backgroundColor: '#0f1a2e', border: '1px solid rgba(201,168,76,0.2)', borderRadius: 16, padding: '32px', width: '100%', maxWidth: 420 }}>
                  <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, color: '#C9A84C', marginTop: 0, marginBottom: 20 }}>Invite Member</h2>

                  {tempPassword ? (
                    <div>
                      <div style={{ padding: 16, backgroundColor: 'rgba(201,168,76,0.1)', border: '1px solid rgba(201,168,76,0.3)', borderRadius: 12, marginBottom: 16 }}>
                        <div style={{ fontSize: 12, color: '#C9A84C', marginBottom: 6, fontWeight: 600 }}>Temporary Password</div>
                        <div style={{ fontSize: 20, fontFamily: 'monospace', color: '#C9A84C', fontWeight: 700 }}>{tempPassword}</div>
                      </div>
                      <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', margin: '0 0 16px' }}>
                        Share this temporary password with the user. It will not be shown again.
                      </p>
                      <button onClick={() => setShowInvite(false)} style={{ width: '100%', padding: 12, backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>Done</button>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                      <div>
                        <label style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 4, display: 'block' }}>Name</label>
                        <input value={inviteData.name} onChange={(e) => setInviteData({ ...inviteData, name: e.target.value })} style={inputStyle} />
                      </div>
                      <div>
                        <label style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 4, display: 'block' }}>Email</label>
                        <input value={inviteData.email} onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })} type="email" style={inputStyle} />
                      </div>
                      <div>
                        <label style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 4, display: 'block' }}>Role</label>
                        <select value={inviteData.role} onChange={(e) => setInviteData({ ...inviteData, role: e.target.value })} style={{ ...inputStyle, appearance: 'auto' as any }}>
                          <option value="attorney">Attorney</option>
                          <option value="paralegal">Paralegal</option>
                        </select>
                      </div>
                      <div style={{ display: 'flex', gap: 10, marginTop: 6 }}>
                        <button onClick={() => setShowInvite(false)} style={{ flex: 1, padding: 12, border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, background: 'none', color: 'rgba(255,255,255,0.5)', fontSize: 14, cursor: 'pointer' }}>Cancel</button>
                        <button onClick={inviteUser} disabled={inviting || !inviteData.email || !inviteData.name} style={{ flex: 1, padding: 12, backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                          {inviting ? 'Inviting...' : 'Invite'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* WHATSAPP TAB */}
        {tab === 'whatsapp' && (
          <div style={{ maxWidth: 600 }}>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', marginTop: 0, marginBottom: 20 }}>
              Add phone numbers of attorneys and paralegals who will interact via WhatsApp.
            </p>

            {/* Add form */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
              <input value={waPhone} onChange={(e) => setWaPhone(e.target.value)} placeholder="+1 555 0000000" style={{ ...inputStyle, flex: '1 1 180px' }} />
              <input value={waName} onChange={(e) => setWaName(e.target.value)} placeholder="Name" style={{ ...inputStyle, flex: '1 1 140px' }} />
              <select value={waRole} onChange={(e) => setWaRole(e.target.value)} style={{ ...inputStyle, flex: '0 0 120px', appearance: 'auto' as any }}>
                <option value="attorney">Attorney</option>
                <option value="paralegal">Paralegal</option>
              </select>
              <button onClick={addWhatsApp} disabled={addingWa || !waPhone || !waName} style={{ padding: '10px 20px', backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer', flex: '0 0 auto' }}>
                {addingWa ? '...' : 'Add'}
              </button>
            </div>

            {/* List */}
            {(office?.whatsapp_numbers || []).length === 0 ? (
              <div style={{ color: 'rgba(255,255,255,0.25)', fontSize: 13 }}>No WhatsApp numbers registered.</div>
            ) : (
              <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px solid rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                      {['Phone', 'Name', 'Role', ''].map((h) => (
                        <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, color: 'rgba(255,255,255,0.35)', fontWeight: 500, textTransform: 'uppercase' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(office?.whatsapp_numbers || []).map((w: WhatsAppEntry) => (
                      <tr key={w.phone} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '10px 16px', fontSize: 13, fontFamily: 'monospace' }}>{w.phone}</td>
                        <td style={{ padding: '10px 16px', fontSize: 13 }}>{w.user_name}</td>
                        <td style={{ padding: '10px 16px', fontSize: 13, textTransform: 'capitalize' }}>{w.role}</td>
                        <td style={{ padding: '10px 16px' }}>
                          <button onClick={() => removeWhatsApp(w.phone)} style={{ padding: '3px 8px', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 6, background: 'none', color: '#ef4444', fontSize: 11, cursor: 'pointer' }}>Remove</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TELEGRAM TAB */}
        {tab === 'telegram' && (
          <div style={{ maxWidth: 600 }}>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', marginTop: 0, marginBottom: 20 }}>
              Connect team members via Telegram bot.
            </p>

            <button onClick={generateTelegramCode} disabled={generatingCode} style={{ padding: '10px 20px', backgroundColor: '#C9A84C', color: '#060d14', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: 'pointer', marginBottom: 16 }}>
              {generatingCode ? 'Generating...' : 'Generate Access Code'}
            </button>

            {telegramCode && (
              <div style={{ padding: 16, backgroundColor: 'rgba(201,168,76,0.1)', border: '1px solid rgba(201,168,76,0.3)', borderRadius: 12, marginBottom: 20 }}>
                <div style={{ fontSize: 28, fontFamily: 'monospace', color: '#C9A84C', fontWeight: 700, letterSpacing: 4, marginBottom: 8 }}>{telegramCode}</div>
                <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', margin: 0 }}>
                  Send this code to <strong style={{ color: '#C9A84C' }}>@imigrai_bot</strong> on Telegram. Valid for 1 hour.
                </p>
              </div>
            )}

            {/* Connections */}
            <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 10, color: 'rgba(255,255,255,0.5)' }}>Active Connections</div>
            {(office?.telegram_chat_ids || []).length === 0 ? (
              <div style={{ color: 'rgba(255,255,255,0.25)', fontSize: 13 }}>No Telegram connections.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {(office?.telegram_chat_ids || []).map((t: TelegramEntry) => (
                  <div key={t.chat_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 8, border: '1px solid rgba(255,255,255,0.04)' }}>
                    <div>
                      <span style={{ fontSize: 13, fontWeight: 500 }}>{t.user_name || t.chat_id}</span>
                      <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginLeft: 10, textTransform: 'capitalize' }}>{t.role}</span>
                    </div>
                    <button onClick={() => removeTelegram(t.chat_id)} style={{ padding: '3px 8px', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 6, background: 'none', color: '#ef4444', fontSize: 11, cursor: 'pointer' }}>Disconnect</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap');
        input::placeholder { color: rgba(255,255,255,0.25); }
        input:focus, select:focus { outline: none; border-color: #C9A84C !important; }
      `}</style>
    </div>
  );
}
