"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

interface AuthUser {
  id: string;
  email: string;
  displayName: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isAuthEnabled: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const DEV_USER: AuthUser = { id: 'dev-user', email: 'dev@local', displayName: 'Developer' };

const AuthContext = createContext<AuthContextValue | null>(null);

// Restore token from localStorage synchronously during init (not in an effect)
function getInitialToken(isAuthEnabled: boolean): string | null {
  if (!isAuthEnabled) return null;
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('networksim_token');
}

function getInitialUser(isAuthEnabled: boolean, token: string | null): AuthUser | null {
  if (!isAuthEnabled) return DEV_USER;
  if (token) return { id: 'restored', email: '', displayName: 'User' };
  return null;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const isAuthEnabled = process.env.NEXT_PUBLIC_AUTH_ENABLED === 'true';

  const [token, setToken] = useState<string | null>(() => getInitialToken(isAuthEnabled));
  const [user, setUser] = useState<AuthUser | null>(() => getInitialUser(isAuthEnabled, token));

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error('Login failed');
    const data = await res.json();
    setToken(data.token);
    setUser(data.user);
    localStorage.setItem('networksim_token', data.token);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(isAuthEnabled ? null : DEV_USER);
    localStorage.removeItem('networksim_token');
  }, [isAuthEnabled]);

  return React.createElement(
    AuthContext.Provider,
    { value: { user, token, isAuthenticated: !!user, isAuthEnabled, login, logout } },
    children
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
