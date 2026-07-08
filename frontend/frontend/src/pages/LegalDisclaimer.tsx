import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

const LegalDisclaimer: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in relative z-10">
      <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-6 md:p-8 shadow-sm space-y-6">
        <div className="flex items-center space-x-3.5 pb-4 border-b border-gray-150 dark:border-gray-800">
          <div className="p-3 bg-amber-500/10 text-amber-500 rounded-2xl">
            <AlertTriangle size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-gray-900 dark:text-white">Important Legal Note</h1>
            <p className="text-xs text-gray-400">Please read this before relying on any answer.</p>
          </div>
        </div>

        <div className="space-y-4 text-xs text-gray-500 dark:text-gray-400 leading-relaxed font-sans">
          <h3 className="font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider text-[10px]">
            1. Informational Help
          </h3>
          <p>
            Nyaya AI provides general legal information, document summaries, and preparation help. It does not guarantee that every answer is complete, current, or correct for your exact facts.
          </p>

          <h3 className="font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider text-[10px]">
            2. Not Legal Advice
          </h3>
          <p>
            Using this app does not create a lawyer-client relationship. The output should not be treated as a final legal opinion or a substitute for advice from a qualified professional.
          </p>

          <h3 className="font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider text-[10px]">
            3. Verify Important Details
          </h3>
          <p>
            Laws, deadlines, court procedures, and official forms can change. Before acting on an answer, verify important points with official sources or a qualified professional.
          </p>

          <h3 className="font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider text-[10px]">
            4. Urgent Situations
          </h3>
          <p>
            If you are facing arrest, violence, eviction, a court deadline, police action, or major financial loss, seek immediate help from the proper authority or a qualified professional.
          </p>
        </div>

        <div className="p-4 bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-850 rounded-2xl flex items-start space-x-3">
          <ShieldCheck size={18} className="text-emerald-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold text-gray-900 dark:text-white">Use It As A Starting Point</h4>
            <p className="text-[10px] text-gray-400 leading-normal">
              Nyaya AI can help you understand a problem and prepare better questions. Final decisions should be based on verified information and your specific situation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegalDisclaimer;
