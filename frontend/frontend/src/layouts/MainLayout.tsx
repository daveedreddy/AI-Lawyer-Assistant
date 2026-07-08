import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  MessageSquare, 
  History, 
  User, 
  Settings, 
  HelpCircle, 
  AlertTriangle, 
  Sun, 
  Moon, 
  Menu, 
  X, 
  LogOut, 
  Plus,
  Scale
} from 'lucide-react';
import { useAuth } from '../context/useAuth';
import { useTheme } from '../context/useTheme';
import { historyService } from '../services/history.service';
import { ChatSession } from '../types';
import Watermark from '../components/Watermark';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [recentChats, setRecentChats] = useState<ChatSession[]>([]);

  // Reload history sessions on path changes and after chat messages are saved.
 useEffect(() => {
  const loadChats = async () => {
    try {
      const chats = await historyService.getSessions();
      setRecentChats(chats.slice(0, 5));
    } catch {
      setRecentChats([]);
    }
  };

  loadChats();
  window.addEventListener('chat-history-updated', loadChats);
  return () => window.removeEventListener('chat-history-updated', loadChats);
}, [location]);

const handleNewChat = async () => {
  const newSession = await historyService.createSession('New Question');
  setSidebarOpen(false);
  navigate(`/chat/${newSession.id}`);
};

  const menuItems = [
    { name: 'Ask Nyaya Samrakshan', path: '/chat', icon: MessageSquare },
    { name: 'Question History', path: '/history', icon: History },
    { name: 'Profile', path: '/profile', icon: User },
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'Help & FAQ', path: '/help', icon: HelpCircle },
    { name: 'Important Note', path: '/disclaimer', icon: AlertTriangle },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors duration-200 font-sans relative">
      {/* Watermark in background */}
      <Watermark />

      {/* MOBILE SIDEBAR OVERLAY */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-950/40 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* SIDEBAR PANEL */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-72 flex flex-col bg-gray-100 dark:bg-gray-900 border-r border-gray-200/80 dark:border-gray-800/80 transition-transform duration-300 md:translate-x-0 md:static md:h-screen ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 flex items-center justify-between border-b border-gray-200 dark:border-gray-800">
          <Link to="/chat" className="flex items-center space-x-3" onClick={() => setSidebarOpen(false)}>
            <div className="p-2 bg-brand-500 text-white rounded-lg shadow-md shadow-brand-500/10">
              <Scale size={20} />
            </div>
            <div>
              <h1 className="text-base font-bold tracking-wide font-sans">Nyaya Samrakshan</h1>
              <p className="text-[10px] text-gray-500 dark:text-gray-400">Legal help for everyone</p>
            </div>
          </Link>
          <button 
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 md:hidden"
          >
            <X size={20} />
          </button>
        </div>

        {/* Start New Chat Action */}
        <div className="p-4">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center space-x-2 bg-brand-500 hover:bg-brand-600 text-white py-2.5 px-4 rounded-xl shadow-lg shadow-brand-500/15 hover:shadow-brand-500/25 active:scale-[0.98] transition-all duration-200 text-sm font-semibold"
          >
            <Plus size={18} />
            <span>New Question</span>
          </button>
        </div>

        {/* Primary Navigation Menu */}
        <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
          <div className="py-2 text-[11px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 px-3">
            Menu
          </div>
          {menuItems.map((item) => {
            const Icon = item.icon;
            // Check if active or subpath
            const isActive = item.path === '/chat' 
              ? location.pathname.startsWith('/chat') 
              : location.pathname === item.path;

            return (
              <Link
                key={item.name}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                  isActive 
                    ? 'bg-gray-200 dark:bg-gray-800 text-brand-600 dark:text-brand-400 font-semibold' 
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200/50 dark:hover:bg-gray-800/50 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                <Icon size={18} className={isActive ? 'text-brand-500' : 'text-gray-400 dark:text-gray-500'} />
                <span>{item.name}</span>
              </Link>
            );
          })}

          {/* Chat History on the side */}
          <div className="pt-6 pb-2">
            <div className="text-[11px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 px-3 mb-2 flex items-center justify-between">
              <span>Recent Questions</span>
              <Link to="/history" className="text-[10px] text-brand-500 hover:underline">View All</Link>
            </div>
            <div className="space-y-1">
              {recentChats.length === 0 ? (
                <div className="text-[11px] text-gray-400 dark:text-gray-500 px-3 py-2 italic">
                  No questions yet
                </div>
              ) : (
                recentChats.map((chat) => {
                  const isActive = location.pathname === `/chat/${chat.id}`;
                  return (
                    <Link
                      key={chat.id}
                      to={`/chat/${chat.id}`}
                      onClick={() => setSidebarOpen(false)}
                      className={`block px-3 py-2 rounded-xl text-xs truncate transition-all duration-150 ${
                        isActive
                          ? 'bg-gray-200/80 dark:bg-gray-800/80 text-brand-600 dark:text-brand-400 font-semibold'
                          : 'text-gray-500 dark:text-gray-400 hover:bg-gray-200/40 dark:hover:bg-gray-800/40'
                      }`}
                    >
                      {chat.title}
                    </Link>
                  );
                })
              )}
            </div>
          </div>
        </nav>

        {/* User Card & Logout */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-800 bg-gray-150/50 dark:bg-gray-950/20">
          {user && (
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-9 h-9 rounded-full bg-brand-500/20 dark:bg-brand-500/10 flex items-center justify-center text-brand-600 dark:text-brand-400 font-bold border border-brand-500/20">
                {user.fullName.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold truncate">{user.fullName}</p>
                <p className="text-[10px] text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center space-x-2 text-red-600 dark:text-red-400 hover:bg-red-500/10 py-2 rounded-xl text-xs font-medium border border-transparent hover:border-red-500/20 transition-all duration-150"
          >
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* MAIN VIEWPORT */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden relative z-10">
        {/* TOP HEADER */}
        <header className="h-16 flex items-center justify-between px-4 md:px-6 border-b border-gray-200/80 dark:border-gray-800/80 bg-white/70 dark:bg-gray-950/70 backdrop-blur-md">
          <div className="flex items-center space-x-3">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 md:hidden"
            >
              <Menu size={20} />
            </button>
            <h2 className="text-sm font-semibold tracking-wide text-gray-500 dark:text-gray-400 uppercase">
              {menuItems.find(item => location.pathname.startsWith(item.path))?.name || 'Nyaya Samrakshan'}
            </h2>
          </div>

          <div className="flex items-center space-x-3">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 dark:bg-gray-900 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-300 transition-all duration-150 border border-gray-200/50 dark:border-gray-800/50"
              title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>

            {/* Account Badge */}
            <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1 bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-200 dark:border-brand-500/20 text-xs font-semibold rounded-full">
              <Scale size={12} />
              <span>Private Account</span>
            </div>
          </div>
        </header>

        {/* PAGE BODY */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-transparent relative">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
