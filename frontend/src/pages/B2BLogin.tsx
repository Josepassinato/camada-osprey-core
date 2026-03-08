import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function B2BLogin() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login(email, password);
      navigate('/app/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.logoSection}>
          <div style={styles.logo}>I</div>
          <h1 style={styles.brand}>Imigrai</h1>
          <p style={styles.subtitle}>Chief of Staff for Immigration Law</p>
        </div>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@lawfirm.com"
              required
              disabled={isLoading}
              style={styles.input}
            />
          </div>

          <div style={styles.fieldGroup}>
            <label style={styles.label}>Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Your password"
                required
                disabled={isLoading}
                style={styles.input}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={styles.togglePw}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <button type="submit" disabled={isLoading} style={styles.button}>
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={styles.footer}>
          <Link to="/register" style={styles.link}>
            Create your firm's account
          </Link>
        </div>
      </div>

      <p style={styles.copyright}>
        Imigrai &middot; B2B Immigration AI
      </p>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap');
        body { margin: 0; }
        input::placeholder { color: rgba(255,255,255,0.25); }
        input:focus { outline: none; border-color: #C9A84C !important; }
        button:hover:not(:disabled) { opacity: 0.9; }
      `}</style>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#060d14',
    padding: '20px',
  },
  card: {
    width: '100%',
    maxWidth: 400,
    backgroundColor: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(201,168,76,0.15)',
    borderRadius: 16,
    padding: '40px 32px',
  },
  logoSection: {
    textAlign: 'center' as const,
    marginBottom: 32,
  },
  logo: {
    width: 56,
    height: 56,
    borderRadius: 14,
    backgroundColor: '#C9A84C',
    color: '#060d14',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 28,
    fontWeight: 700,
    fontFamily: "'Playfair Display', serif",
    marginBottom: 12,
  },
  brand: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 28,
    fontWeight: 600,
    color: '#C9A84C',
    margin: '0 0 4px',
  },
  subtitle: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.4)',
    margin: 0,
  },
  error: {
    backgroundColor: 'rgba(220,38,38,0.15)',
    border: '1px solid rgba(220,38,38,0.3)',
    color: '#fca5a5',
    borderRadius: 8,
    padding: '10px 14px',
    fontSize: 13,
    marginBottom: 16,
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 18,
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 6,
  },
  label: {
    fontSize: 12,
    fontWeight: 500,
    color: 'rgba(255,255,255,0.6)',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
  },
  input: {
    width: '100%',
    padding: '12px 14px',
    backgroundColor: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 8,
    color: '#e2e8f0',
    fontSize: 14,
    boxSizing: 'border-box' as const,
  },
  togglePw: {
    position: 'absolute' as const,
    right: 12,
    top: '50%',
    transform: 'translateY(-50%)',
    background: 'none',
    border: 'none',
    color: 'rgba(255,255,255,0.4)',
    fontSize: 12,
    cursor: 'pointer',
  },
  button: {
    width: '100%',
    padding: '14px',
    backgroundColor: '#C9A84C',
    color: '#060d14',
    border: 'none',
    borderRadius: 8,
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    marginTop: 4,
  },
  footer: {
    textAlign: 'center' as const,
    marginTop: 20,
  },
  link: {
    color: '#C9A84C',
    fontSize: 13,
    textDecoration: 'none',
  },
  copyright: {
    color: 'rgba(255,255,255,0.2)',
    fontSize: 11,
    marginTop: 24,
  },
};
