import React from 'react';

const Watermark: React.FC = () => {
  return (
    <div className="fixed inset-0 flex items-center justify-center pointer-events-none select-none z-0 overflow-hidden">
      <svg
        className="w-[60vw] h-[60vw] max-w-[500px] max-h-[500px] text-gray-300/15 dark:text-gray-100/3.5 transition-colors duration-200"
        viewBox="0 0 100 100"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Scales of Justice */}
        {/* Base */}
        <path d="M35 85 H65" strokeWidth="2.5" />
        <path d="M42 85 L44 80 H56 L58 85 Z" fill="currentColor" fillOpacity="0.05" />
        
        {/* Main Column */}
        <line x1="50" y1="15" x2="50" y2="80" strokeWidth="2" />
        <circle cx="50" cy="13" r="3" fill="currentColor" />
        <path d="M47 30 H53" strokeWidth="1.5" />
        
        {/* Crossbeam (slightly stylized) */}
        <path d="M20 22 C30 25, 40 25, 50 22 C60 25, 70 25, 80 22" strokeWidth="2" />
        
        {/* Left Scale Pan Assembly */}
        <line x1="20" y1="22" x2="20" y2="48" />
        <path d="M12 48 C12 55, 28 55, 28 48 Z" fill="currentColor" fillOpacity="0.05" />
        {/* Hanging lines details */}
        <line x1="20" y1="22" x2="12" y2="48" strokeWidth="0.8" />
        <line x1="20" y1="22" x2="28" y2="48" strokeWidth="0.8" />
        
        {/* Right Scale Pan Assembly */}
        <line x1="80" y1="22" x2="80" y2="48" />
        <path d="M72 48 C72 55, 88 55, 88 48 Z" fill="currentColor" fillOpacity="0.05" />
        {/* Hanging lines details */}
        <line x1="80" y1="22" x2="72" y2="48" strokeWidth="0.8" />
        <line x1="80" y1="22" x2="88" y2="48" strokeWidth="0.8" />

        {/* Center Pivot Indicator */}
        <polygon points="50,22 48,17 52,17" fill="currentColor" />
        
        {/* Gavel Backdrop (Crossed in background, low stroke-width/opacity) */}
        <path
          d="M32 60 L68 35"
          strokeWidth="0.8"
          strokeDasharray="2 2"
          className="text-gray-300/10 dark:text-gray-100/2.5"
        />
        {/* Gavel Head */}
        <path
          d="M62 30 L72 38 M64 28 L60 32 M70 36 L66 40"
          strokeWidth="1.2"
          className="text-gray-300/10 dark:text-gray-100/2.5"
        />
      </svg>
    </div>
  );
};

export default Watermark;
