import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Scale } from 'lucide-react';
import { useAuth } from '../context/useAuth';

const SplashScreen: React.FC = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading) {
      const timer = setTimeout(() => {
        navigate(user ? '/chat' : '/login');
      }, 1600);
      return () => clearTimeout(timer);
    }
  }, [user, loading, navigate]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-950 transition-colors duration-300 relative overflow-hidden">
      <div className="absolute inset-0 auth-backdrop-pattern opacity-50" />
      <div className="auth-rail absolute left-0 right-0 top-1/3 h-px" />
      <div className="auth-rail absolute left-0 right-0 bottom-1/3 h-px animation-delay-700" />

      <div className="flex flex-col items-center text-center animate-fade-in relative z-10 px-6">
        <div className="p-6 bg-white dark:bg-gray-900 text-brand-500 rounded-lg shadow-2xl border border-gray-200/50 dark:border-gray-800/50 mb-6 scale-95 animate-pulse">
          <Scale size={72} strokeWidth={1.5} />
        </div>

        <h1 className="text-4xl font-extrabold tracking-tight font-sans text-gray-900 dark:text-white mb-2">
          Nyaya <span className="text-brand-500">Samrakshan</span>
        </h1>
        <p className="text-gray-500 dark:text-gray-400 font-medium text-xs tracking-widest uppercase mb-8">
          Legal help for everyone
        </p>

        <div className="flex items-center space-x-1.5" aria-label="Loading">
          <div className="w-2.5 h-2.5 rounded-full bg-brand-500 animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2.5 h-2.5 rounded-full bg-brand-500 animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2.5 h-2.5 rounded-full bg-brand-500 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>

      <div className="absolute bottom-6 text-xs text-gray-400 dark:text-gray-600">
        Version 1.0.0 - Public legal help
      </div>
    </div>
  );
};

export default SplashScreen;
