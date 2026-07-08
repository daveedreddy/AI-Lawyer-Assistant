import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Trash2,
  MessageSquare,
  ChevronRight,
  Edit3,
  Check,
  X,
  Calendar,
} from 'lucide-react';
import { historyService } from '../services/history.service';
import { ChatSession } from '../types';

const ChatHistory: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    historyService.getSessions()
      .then(setSessions)
      .catch(() => setSessions([]))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this consultation history?')) return;
    try {
      await historyService.deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch {
      // Deletion failed — no UI crash
    }
  };

  const startEditing = (id: string, currentTitle: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(id);
    setEditTitle(currentTitle);
  };

  const saveTitle = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!editTitle.trim()) { setEditingId(null); return; }
    try {
      await historyService.updateSessionTitle(id, editTitle.trim());
      setSessions((prev) =>
        prev.map((s) => (s.id === id ? { ...s, title: editTitle.trim() } : s))
      );
    } catch {
      // Title update failed — keep existing
    }
    setEditingId(null);
  };

  const cancelEditing = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const filteredSessions = sessions.filter(
    (s) =>
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (s.summary && s.summary.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10">

      {/* Header & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Consultation History</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Browse and manage your saved legal help conversations.
          </p>
        </div>

        <div className="relative w-full sm:w-80">
          <Search size={16} className="absolute left-3 top-3 text-gray-400" />
          <input
            type="text"
            placeholder="Search titles or summaries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
      </div>

      {/* Main List */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-3xl p-4 shadow-sm">
        {loading ? (
          <div className="p-12 flex flex-col items-center space-y-3">
            <div className="w-7 h-7 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs text-gray-400">Loading consultations...</p>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="p-12 text-center text-xs text-gray-500 dark:text-gray-400">
            {searchQuery ? 'No chats match your search.' : 'No chat history yet. Start a new question!'}
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-800/80">
            {filteredSessions.map((session) => {
              const formattedDate = new Date(session.updatedAt).toLocaleDateString('en-IN', {
                day: 'numeric', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit',
              });
              const isEditing = editingId === session.id;

              return (
                <div
                  key={session.id}
                  onClick={() => navigate(`/chat/${session.id}`)}
                  className="flex items-start justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800/30 rounded-2xl cursor-pointer group transition-all duration-150 border border-transparent hover:border-gray-200/30"
                >
                  <div className="flex items-start space-x-3.5 flex-1 min-w-0">
                    <div className="p-3 bg-gray-100 dark:bg-gray-800 text-gray-500 rounded-xl mt-1 shrink-0">
                      <MessageSquare size={18} />
                    </div>

                    <div className="flex-1 min-w-0 space-y-1">
                      {isEditing ? (
                        <div className="flex items-center space-x-1.5 max-w-md" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="text"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            className="px-2.5 py-1 text-xs border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 focus:outline-none focus:ring-1 focus:ring-brand-500 rounded-lg flex-1 font-semibold"
                            autoFocus
                          />
                          <button onClick={(e) => saveTitle(session.id, e)} className="p-1 text-emerald-600 hover:bg-emerald-500/10 rounded-md">
                            <Check size={14} />
                          </button>
                          <button onClick={cancelEditing} className="p-1 text-red-600 hover:bg-red-500/10 rounded-md">
                            <X size={14} />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <h4 className="text-sm font-bold truncate text-gray-900 dark:text-white">{session.title}</h4>
                          <button
                            onClick={(e) => startEditing(session.id, session.title, e)}
                            className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-opacity"
                            title="Edit Title"
                          >
                            <Edit3 size={12} />
                          </button>
                        </div>
                      )}

                      <p className="text-[11px] text-gray-500 dark:text-gray-400 line-clamp-2 leading-relaxed">
                        {session.summary || 'Conversation ready.'}
                      </p>

                      <div className="flex items-center space-x-1.5 text-[10px] text-gray-400">
                        <Calendar size={10} />
                        <span>Last updated: {formattedDate}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0 ml-4">
                    <button
                      onClick={(e) => handleDelete(session.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all duration-150"
                      title="Delete chat"
                    >
                      <Trash2 size={15} />
                    </button>
                    <ChevronRight size={16} className="text-gray-300 dark:text-gray-600" />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatHistory;
