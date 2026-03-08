import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const NAV_ITEMS = [
  { path: '/app/dashboard', label: 'Dashboard', icon: '\u2302' },
  { path: '/app/cases', label: 'Cases', icon: '\u2630' },
  { path: '/app/chat', label: 'Chat', icon: '\u2709' },
];

export default function B2BSidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  return (
    <aside style={styles.sidebar}>
      <div>
        <div style={styles.logoArea} onClick={() => navigate('/app/dashboard')}>
          <div style={styles.logoIcon}>I</div>
          <div>
            <div style={styles.logoText}>Imigrai</div>
            <div style={styles.firmName}>{user?.firm_name || 'Law Firm'}</div>
          </div>
        </div>

        <nav style={styles.nav}>
          {NAV_ITEMS.map((item) => {
            const active = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                style={{
                  ...styles.navItem,
                  ...(active ? styles.navActive : {}),
                }}
              >
                <span style={{ fontSize: 16 }}>{item.icon}</span>
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      <div style={styles.bottomSection}>
        <div style={styles.userInfo}>
          <div style={styles.avatar}>{(user?.name || 'U')[0].toUpperCase()}</div>
          <div>
            <div style={styles.userName}>{user?.name}</div>
            <div style={styles.userRole}>{user?.role}</div>
          </div>
        </div>
        <button
          onClick={() => {
            logout();
            navigate('/login');
          }}
          style={styles.logoutBtn}
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}

const styles: Record<string, React.CSSProperties> = {
  sidebar: {
    width: 240,
    minHeight: '100vh',
    backgroundColor: '#0a1220',
    borderRight: '1px solid rgba(201,168,76,0.1)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    padding: '20px 12px',
    boxSizing: 'border-box',
    flexShrink: 0,
  },
  logoArea: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '8px 10px',
    cursor: 'pointer',
    marginBottom: 28,
  },
  logoIcon: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: '#C9A84C',
    color: '#060d14',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 20,
    fontWeight: 700,
    fontFamily: "'Playfair Display', serif",
  },
  logoText: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 18,
    fontWeight: 600,
    color: '#C9A84C',
  },
  firmName: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.35)',
    marginTop: -2,
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '10px 14px',
    borderRadius: 8,
    border: 'none',
    background: 'none',
    color: 'rgba(255,255,255,0.55)',
    fontSize: 14,
    cursor: 'pointer',
    textAlign: 'left' as const,
    width: '100%',
    transition: 'all 0.15s',
  },
  navActive: {
    backgroundColor: 'rgba(201,168,76,0.12)',
    color: '#C9A84C',
  },
  bottomSection: {
    borderTop: '1px solid rgba(255,255,255,0.06)',
    paddingTop: 14,
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '6px 10px',
    marginBottom: 8,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    backgroundColor: 'rgba(201,168,76,0.2)',
    color: '#C9A84C',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 14,
    fontWeight: 600,
  },
  userName: {
    fontSize: 13,
    color: '#e2e8f0',
    fontWeight: 500,
  },
  userRole: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'capitalize' as const,
  },
  logoutBtn: {
    width: '100%',
    padding: '8px 14px',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 6,
    background: 'none',
    color: 'rgba(255,255,255,0.4)',
    fontSize: 12,
    cursor: 'pointer',
    textAlign: 'center' as const,
  },
};
