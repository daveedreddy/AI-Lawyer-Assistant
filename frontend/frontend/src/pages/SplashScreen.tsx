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
        if (user) {
          navigate('/chat');
        } else {
          navigate('/login');
        }
      }, 2000); // 2 second delay for splash aesthetics
      return () => clearTimeout(timer);
    }
  }, [user, loading, navigate]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-tr from-gray-100 to-gray-200 dark:from-gray-950 dark:to-gray-900 transition-colors duration-300 relative overflow-hidden">
      {/* Decorative Blur Orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-brand-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-brand-600/5 rounded-full blur-3xl animate-pulse-slow"></div>

      <div className="flex flex-col items-center text-center animate-fade-in relative z-10">
        {/* Animated Scales Symbol */}
        <div className="p-6 bg-white dark:bg-gray-900 text-brand-500 rounded-3xl shadow-2xl border border-gray-200/50 dark:border-gray-800/50 mb-6 scale-95 animate-pulse">
          <Scale size={72} strokeWidth={1.5} />
        </div>

        {/* Brand Name */}
        <h1 className="text-4xl font-extrabold tracking-tight font-sans text-gray-900 dark:text-white mb-2">
          NYAYA <span className="text-brand-500">AI</span>
        </h1>
        <p className="text-gray-500 dark:text-gray-400 font-medium text-xs tracking-widest uppercase mb-8">
          AI lawyer assistant
        </p>

        {/* Minimal Loader */}
        <div className="flex items-center space-x-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-brand-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2.5 h-2.5 rounded-full bg-brand-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2.5 h-2.5 rounded-full bg-brand-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>

      <div className="absolute bottom-6 text-xs text-gray-400 dark:text-gray-600">
        Version 1.0.0 • Adv. Assistant Suite
      </div>
    </div>
  );
};

export default SplashScreen;
