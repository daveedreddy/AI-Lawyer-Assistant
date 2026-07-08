import React from 'react';
import { HelpCircle, BookOpen, Compass } from 'lucide-react';

const Help: React.FC = () => {
  const codeTranslations = [
    { old: 'Indian Penal Code (IPC), 1860', new: 'Bharatiya Nyaya Sanhita (BNS), 2023', focus: 'Offences, responsibility, and punishments' },
    { old: 'Code of Criminal Procedure (CrPC), 1973', new: 'Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023', focus: 'Police process, arrest, bail, and trials' },
    { old: 'Indian Evidence Act, 1872', new: 'Bharatiya Sakshya Adhiniyam (BSA), 2023', focus: 'Evidence, documents, witnesses, and digital records' },
  ];

  const faqs = [
    {
      q: 'Can I ask in simple words?',
      a: 'Yes. Describe what happened, what document you received, or what you are worried about. Nyaya AI will try to explain the issue in plain language and may ask quick follow-up questions.',
    },
    {
      q: 'How are sources shown?',
      a: 'When the answer uses a law, section, or public source, you may see source chips below the message. Select a chip to read a short explanation and verify important points.',
    },
    {
      q: 'Is this a replacement for a lawyer?',
      a: 'No. This app is for information, preparation, and understanding possible next steps. For urgent matters, court deadlines, arrests, notices, or major financial risk, speak with a qualified professional.',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Help & FAQ</h1>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          A quick guide for asking better questions and reading answers safely.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-5 shadow-sm md:col-span-3 space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-gray-150 dark:border-gray-800">
            <BookOpen className="text-brand-500" size={18} />
            <h3 className="font-bold text-sm">Common Indian Law Names</h3>
          </div>

          <p className="text-xs text-gray-500 dark:text-gray-400 leading-normal">
            Some criminal laws were renamed from July 1, 2024. This table helps you recognize older and newer names when reading notices, news, or police papers.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="bg-gray-50 dark:bg-gray-950 text-gray-400 font-semibold border-b border-gray-150 dark:border-gray-800">
                  <th className="p-3">Older Name</th>
                  <th className="p-3 text-brand-500">Current Name</th>
                  <th className="p-3">What It Covers</th>
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

        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-5 shadow-sm md:col-span-2 space-y-4">
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

        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-5 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-gray-150 dark:border-gray-800">
            <Compass className="text-brand-500" size={18} />
            <h3 className="font-bold text-sm">Better Questions</h3>
          </div>

          <ul className="text-xs space-y-3 text-gray-500 dark:text-gray-400">
            <li>Include the city or state when local rules may matter.</li>
            <li>Mention deadlines, notice dates, or hearing dates if you know them.</li>
            <li>Upload a readable PDF, DOCX, TXT, PNG, or JPG when you want a document summary.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Help;
