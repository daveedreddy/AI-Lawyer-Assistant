import React from 'react';
import { HelpCircle, BookOpen, AlertTriangle, Compass } from 'lucide-react';

const Help: React.FC = () => {
  const codeTranslations = [
    { old: 'Indian Penal Code (IPC), 1860', new: 'Bharatiya Nyaya Sanhita (BNS), 2023', focus: 'Substantive offenses, criminal liabilities, and punishments' },
    { old: 'Code of Criminal Procedure (CrPC), 1973', new: 'Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023', focus: 'Police investigations, arrest rules, bail procedures, and trials' },
    { old: 'Indian Evidence Act, 1872', new: 'Bharatiya Sakshya Adhiniyam (BSA), 2023', focus: 'Rules of evidence admissibility, digital document verification' }
  ];

  const faqs = [
    {
      q: 'How does Nyaya AI handle citations?',
      a: 'Nyaya AI automatically identifies legal names (e.g. BNS Section 103, IPC 302, bail cases) and extracts them into active citations. You can click on any citation in the chat bubble to review the detailed legal summary on the right-hand panel.'
    },
    {
      q: 'Is my client data confidential?',
      a: 'Yes, absolutely. The frontend operates with mock API structures locally. If connected to a backend, all document parsing and messages are secured using tokenized HTTPS requests, ensuring compliance with professional client privilege guidelines.'
    },
    {
      q: 'What should I do if a citation seems outdated?',
      a: 'This assistant references published legal gazettes as of July 2024. For latest Supreme Court orders or custom state high court rulings, please consult the Integrated Case Management System (ICMIS) or your local bar database.'
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Help & Documentation</h1>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          Access the guide to help you utilize the Indian Legal AI suite.
        </p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Core Code Translations */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-3xl p-5 shadow-sm md:col-span-3 space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-gray-150 dark:border-gray-800">
            <BookOpen className="text-brand-500" size={18} />
            <h3 className="font-bold text-sm">Indian Judicial Code Equivalents (2023-2024 Update)</h3>
          </div>

          <p className="text-xs text-gray-500 dark:text-gray-400 leading-normal">
            As of July 1, 2024, the old colonial penal system is officially replaced by the new criminal codes. Refer to the translation mapper below when drafting claims:
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="bg-gray-50 dark:bg-gray-950 text-gray-400 font-semibold border-b border-gray-150 dark:border-gray-800">
                  <th className="p-3">Legacy Act (Repealed)</th>
                  <th className="p-3 text-brand-500">New Enforced Act</th>
                  <th className="p-3">Primary Focus</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800/80">
                {codeTranslations.map((item, idx) => (
                  <tr key={idx} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/10">
                    <td className="p-3 font-medium text-gray-500">{item.old}</td>
                    <td className="p-3 font-bold text-brand-600 dark:text-brand-400">{item.new}</td>
                    <td className="p-3 text-gray-500">{item.focus}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* FAQs */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-3xl p-5 shadow-sm md:col-span-2 space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-gray-150 dark:border-gray-800">
            <HelpCircle className="text-brand-500" size={18} />
            <h3 className="font-bold text-sm">Frequently Asked Questions</h3>
          </div>

          <div className="space-y-4 divide-y divide-gray-100 dark:divide-gray-800/80">
            {faqs.map((faq, idx) => (
              <div key={idx} className={`space-y-1.5 ${idx > 0 ? 'pt-3' : ''}`}>
                <h4 className="text-xs font-bold text-gray-900 dark:text-white flex items-start">
                  <span className="text-brand-500 mr-1.5 shrink-0">Q.</span>
                  <span>{faq.q}</span>
                </h4>
                <p className="text-xs text-gray-500 dark:text-gray-400 leading-normal pl-4">
                  {faq.a}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Tips */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-3xl p-5 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-gray-150 dark:border-gray-800">
            <Compass className="text-brand-500" size={18} />
            <h3 className="font-bold text-sm">Usage Shortcuts</h3>
          </div>

          <ul className="text-xs space-y-3 text-gray-500 dark:text-gray-400">
            <li>
              💡 **Keyword Queries**: Type simple matching terms like `bns`, `bail`, or `contract` to review custom-tailored database answers with interactive panels.
            </li>
            <li>
              📎 **Mock Lease Analysis**: Try uploading any doc file named `lease.docx` to trigger the specialized rent and arbitration analyzer.
            </li>
            <li>
              📎 **Mock FIR Analysis**: Try uploading a file named `FIR.pdf` to trigger the Bandra PS accident case review and bail ground prompts.
            </li>
          </ul>
        </div>

      </div>

    </div>
  );
};

export default Help;
