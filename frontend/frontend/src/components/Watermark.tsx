import React from 'react';

const Watermark: React.FC = () => {
  return (
    <div className="fixed inset-0 flex items-center justify-center pointer-events-none select-none z-0 overflow-hidden">
      <img
        src="/justice-watermark.png"
        alt=""
        aria-hidden="true"
        className="justice-watermark w-[58vw] max-w-[520px] min-w-[280px] opacity-[0.055] dark:opacity-[0.04]"
        draggable={false}
      />
    </div>
  );
};

export default Watermark;
