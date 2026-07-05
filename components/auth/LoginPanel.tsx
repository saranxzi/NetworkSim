"use client";

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { Lock, Mail, ArrowRight, AlertCircle } from 'lucide-react';

export default function LoginPanel() {
  const { login, isAuthEnabled, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!isAuthEnabled || isAuthenticated) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      await login(email, password);
    } catch {
      setError('Invalid credentials or network error.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-[400px] rounded-xl border border-white/10 bg-black/80 shadow-2xl overflow-hidden p-6 flex flex-col gap-6">
        <div className="flex flex-col items-center justify-center space-y-2 text-center">
          <div className="h-12 w-12 rounded-full bg-emerald-500/10 flex items-center justify-center mb-2 border border-emerald-500/20">
            <Lock className="text-emerald-400" size={24} />
          </div>
          <h2 className="text-xl font-bold tracking-tight text-gray-100">Authentication Required</h2>
          <p className="text-sm text-gray-400">Sign in to access NetworkSim</p>
        </div>

        {error && (
          <div className="rounded-md bg-red-500/10 border border-red-500/20 p-3 flex items-start gap-2">
            <AlertCircle className="text-red-400 mt-0.5" size={16} />
            <span className="text-xs text-red-300">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="space-y-1">
            <label className="text-xs font-medium text-gray-400 pl-1">Email</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <Mail className="h-4 w-4 text-gray-500" />
              </div>
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-gray-900/50 border border-white/10 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                placeholder="developer@local"
              />
            </div>
          </div>
          
          <div className="space-y-1">
            <label className="text-xs font-medium text-gray-400 pl-1">Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <Lock className="h-4 w-4 text-gray-500" />
              </div>
              <input 
                type="password" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-gray-900/50 border border-white/10 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button 
            type="submit"
            disabled={isLoading}
            className="mt-2 w-full flex items-center justify-center gap-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 rounded-lg py-2.5 text-sm font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Authenticating...' : 'Sign In'}
            {!isLoading && <ArrowRight size={16} />}
          </button>
        </form>
      </div>
    </div>
  );
}
