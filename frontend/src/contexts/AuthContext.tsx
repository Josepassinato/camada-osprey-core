import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const API_URL = import.meta.env.VITE_BACKEND_URL || '';

interface User {
  user_id: string;
  office_id: string;
  email: string;
  name: string;
  role: string;
  firm_name: string;
  plan: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (firm_name: string, owner_name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function decodeJwtPayload(token: string): Record<string, any> | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(payload);
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem('imigrai_token');
    setUser(null);
    setToken(null);
  }, []);

  // Validate token and fetch user data on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('imigrai_token');
    if (!savedToken) {
      setIsLoading(false);
      return;
    }

    const payload = decodeJwtPayload(savedToken);
    if (!payload || (payload.exp && payload.exp * 1000 < Date.now())) {
      logout();
      setIsLoading(false);
      return;
    }

    setToken(savedToken);

    fetch(`${API_URL}/api/auth/b2b/me`, {
      headers: { Authorization: `Bearer ${savedToken}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error('Invalid token');
        return res.json();
      })
      .then((data) => {
        setUser({
          user_id: data.user_id,
          office_id: data.office_id,
          email: data.email,
          name: data.name,
          role: data.role,
          firm_name: data.firm_name,
          plan: data.plan,
        });
      })
      .catch(() => {
        logout();
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [logout]);

  const login = async (email: string, password: string) => {
    const res = await fetch(`${API_URL}/api/auth/b2b/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');

    localStorage.setItem('imigrai_token', data.token);
    setToken(data.token);
    setUser(data.user);
  };

  const register = async (firm_name: string, owner_name: string, email: string, password: string) => {
    const res = await fetch(`${API_URL}/api/auth/b2b/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ firm_name, owner_name, email, password }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');

    localStorage.setItem('imigrai_token', data.token);
    setToken(data.token);
    setUser(data.user);
  };

  const getToken = () => token;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        register,
        logout,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
