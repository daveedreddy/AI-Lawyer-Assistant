import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Scale,
  MessageSquare,
  FileText,
  BookOpen,
  ArrowRight,
  Plus,
  Calendar,
  Compass,
} from 'lucide-react';
import { useAuth } from '../context/useAuth';
import { profileService } from '../services/profile.service';
import { historyService } from '../services/history.service';
import { ChatSession } from '../types';

interface StatsShape {
  total_chats: number;
  documents_analyzed: number;
  drafts_generated: number;
  saved_citations: number;
}

const HomeDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<StatsShape | null>(null);
  const [recentChats, setRecentChats] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsData, sessions] = await Promise.all([
          profileService.getUserStats(),
          historyService.getSessions(),
        ]);
        setStats(statsData);
        setRecentChats(sessions.slice(0, 3));
      } catch {
        // Silently fail — show zeros
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  const quickPrompts = [
    {
      title: 'BNS Murder Provisions',
      desc: 'Analyze Section 103 of BNS (Murder) & compare with IPC 302.',
      prompt: 'Compare Section 103 BNS (Murder) with legacy IPC 302.',
      category: 'Criminal Law',
    },
    {
      title: 'Anticipatory Bail Grounds',
      desc: 'Check guidelines and grounds for bail under CrPC 438/BNSS 482.',
      prompt: 'What are the main grounds for anticipatory bail under BNSS 482?',
      category: 'Procedural Law',
    },
    {
      title: 'Lease Dispute Resolution',
      desc: 'Formulate arbitration and Force Majeure clauses for tenancy.',
      prompt: 'Draft an arbitration and Force Majeure clause for a tenancy lease.',
      category: 'Contract Law',
    },
  ];

  const handleQuickStart = async (promptText: string) => {
    const newSession = await historyService.createSession('New Consultation');
    navigate(`/chat/${newSession.id}`, { state: { initialPrompt: promptText } });
  };

  const handleNewChat = async () => {
    const newSession = await historyService.createSession('New Consultation');
    navigate(`/chat/${newSession.id}`);
  };

  const formattedDate = new Date().toLocaleDateString('en-IN', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in relative z-10">

      {/* Welcome Banner */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-3xl p-6 md:p-8 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-brand-500 mb-1.5">
            <Calendar size={14} />
            <span>{formattedDate}</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Namaste, {user?.fullName || 'Counsel'}
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Access your secure Indian Legal AI workspace. Ask queries or upload legal case documents.
          </p>
        </div>
        <button
          onClick={handleNewChat}
          className="flex items-center space-x-2 bg-brand-500 hover:bg-brand-600 text-white py-3 px-5 rounded-2xl shadow-lg shadow-brand-500/15 transition-all duration-200 text-sm font-semibold active:scale-[0.98]"
        >
          <Plus size={18} />
          <span>New Case Consult</span>
        </button>
      </div>

      {/* Analytics widgets */}
      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-200 dark:bg-gray-800 animate-pulse rounded-2xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-4 shadow-sm">
            <div className="p-2 bg-blue-500/10 text-blue-500 w-fit rounded-xl mb-3"><FileText size={18} /></div>
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400">Documents Analyzed</p>
            <h3 className="text-xl font-bold mt-0.5">{stats?.documents_analyzed ?? 0}</h3>
          </div>
          <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-4 shadow-sm">
            <div className="p-2 bg-indigo-500/10 text-indigo-500 w-fit rounded-xl mb-3"><MessageSquare size={18} /></div>
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400">Total Consultations</p>
            <h3 className="text-xl font-bold mt-0.5">{stats?.total_chats ?? 0}</h3>
          </div>
          <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-4 shadow-sm">
            <div className="p-2 bg-emerald-500/10 text-emerald-500 w-fit rounded-xl mb-3"><Scale size={18} /></div>
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400">Drafts Generated</p>
            <h3 className="text-xl font-bold mt-0.5">{stats?.drafts_generated ?? 0}</h3>
          </div>
          <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-4 shadow-sm">
            <div className="p-2 bg-amber-500/10 text-amber-500 w-fit rounded-xl mb-3"><BookOpen size={18} /></div>
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400">Saved Citations</p>
            <h3 className="text-xl font-bold mt-0.5">{stats?.saved_citations ?? 0}</h3>
          </div>
        </div>
      )}

      {/* Grid of Sections */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* Quick Consultation Starters */}
        <div className="md:col-span-2 space-y-4">
          <div className="flex items-center space-x-2 text-gray-700 dark:text-gray-300 font-semibold px-1">
            <Compass size={18} className="text-brand-500" />
            <h2>Quick Consultation Starters</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickPrompts.map((item, idx) => (
              <div
                key={idx}
                onClick={() => handleQuickStart(item.prompt)}
                className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 hover:border-brand-500 dark:hover:border-brand-500 rounded-2xl p-5 shadow-sm hover:shadow-md cursor-pointer transition-all duration-200 flex flex-col justify-between group"
              >
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-brand-500 bg-brand-500/10 dark:bg-brand-500/5 px-2 py-0.5 rounded-full">{item.category}</span>
                  <h4 className="text-sm font-bold group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">{item.title}</h4>
                  <p className="text-[11px] text-gray-500 dark:text-gray-400 line-clamp-3 leading-normal">{item.desc}</p>
                </div>
                <div className="mt-4 flex items-center justify-between text-xs font-semibold text-brand-500 pt-2 border-t border-gray-100 dark:border-gray-800/50">
                  <span>Start query</span>
                  <ArrowRight size={14} className="transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Cases */}
        <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <h2 className="font-semibold text-gray-700 dark:text-gray-300 flex items-center space-x-2">
              <BookOpen size={18} className="text-brand-500" />
              <span>Recent Consultations</span>
            </h2>
            <Link to="/history" className="text-xs text-brand-500 hover:underline font-semibold">View all</Link>
          </div>
          <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-3xl p-4 shadow-sm space-y-3">
            {loading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => <div key={i} className="h-12 bg-gray-200 dark:bg-gray-800 animate-pulse rounded-xl" />)}
              </div>
            ) : recentChats.length === 0 ? (
              <div className="p-6 text-center text-xs text-gray-500 dark:text-gray-400">
                No consultation history found. Click "New Case Consult" to begin.
              </div>
            ) : (
              recentChats.map((chat) => (
                <Link
                  key={chat.id}
                  to={`/chat/${chat.id}`}
                  className="flex items-start space-x-3 p-3 rounded-2xl hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-all duration-150 border border-transparent hover:border-gray-200/50 dark:hover:border-gray-800/20"
                >
                  <div className="p-2 bg-gray-100 dark:bg-gray-800 text-gray-500 rounded-xl"><MessageSquare size={16} /></div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-semibold truncate">{chat.title}</h4>
                    <p className="text-[10px] text-gray-400 dark:text-gray-500 truncate mt-0.5">{chat.summary || 'Consultation file active.'}</p>
                  </div>
                  <ArrowRight size={14} className="text-gray-400 mt-1 self-center" />
                </Link>
              ))
            )}
          </div>
        </div>

      </div>

      {/* Compliance Callout */}
      <div className="bg-gray-100 dark:bg-gray-900/60 border border-gray-200 dark:border-gray-800/60 rounded-2xl p-4 flex items-start space-x-3">
        <div className="p-1.5 bg-amber-500/10 text-amber-500 rounded-lg"><Scale size={16} /></div>
        <p className="text-[11px] text-gray-500 dark:text-gray-400 leading-normal">
          <strong>BCI Compliance Notice</strong>: This system provides informative legal tools, citation references, and document drafting templates. It is not an alternative to an advocate's individual counsel under the Bar Council of India Rules. Please verify critical statutory amendments independently.
        </p>
      </div>

    </div>
  );
};

export default HomeDashboard;
