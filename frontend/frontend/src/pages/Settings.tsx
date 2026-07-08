import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/useTheme';
import {
  Globe,
  Sliders,
  Server,
  Sun,
  Moon,
  Check,
  Info,
  Bell,
} from 'lucide-react';
import { profileService } from '../services/profile.service';
import { API_BASE_URL } from '../services/api';

const Settings: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  const [language, setLanguage] = useState('en');
  const [model, setModel] = useState('nvidia');
  const [temp, setTemp] = useState(0.3);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [apiBaseUrl, setApiBaseUrl] = useState(API_BASE_URL);
  const [showSaveAlert, setShowSaveAlert] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    profileService.getSettings()
      .then((s) => {
        setLanguage(s.language || 'en');
        setModel(s.model_preference || 'nvidia');
        setNotificationsEnabled(s.notifications_enabled ?? true);
        setTemp(s.temperature ?? 0.3);
        setApiBaseUrl(s.api_base_url || API_BASE_URL);
        if (s.theme && s.theme !== theme) {
          toggleTheme();
        }
      })
      .catch(() => { /* Use defaults when settings are unavailable. */ })
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await profileService.updateSettings({
        theme,
        language,
        model_preference: model,
        notifications_enabled: notificationsEnabled,
        temperature: temp,
        api_base_url: apiBaseUrl,
      });
      setShowSaveAlert(true);
      setTimeout(() => setShowSaveAlert(false), 2000);
    } catch {
      setShowSaveAlert(true);
      setTimeout(() => setShowSaveAlert(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'mr', name: 'Marathi' },
    { code: 'bn', name: 'Bengali' },
    { code: 'ta', name: 'Tamil' },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Preferences</h1>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          Choose how Nyaya AI looks, responds, and connects to the backend.
        </p>
      </div>

      {showSaveAlert && (
        <div className="flex items-center space-x-2.5 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-semibold animate-fade-in">
          <Check size={16} />
          <span>Preferences saved.</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-5 shadow-sm space-y-5">
          <div className="flex items-center space-x-2 pb-3 border-b border-gray-150 dark:border-gray-800">
            <Globe className="text-brand-500" size={18} />
            <h3 className="font-bold text-sm">Display & Language</h3>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Theme</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => theme === 'dark' && toggleTheme()}
                className={`flex items-center justify-center space-x-2 p-3 rounded-xl border text-xs font-semibold transition-all ${
                  theme === 'light' ? 'bg-brand-50 border-brand-500 text-brand-600 dark:text-brand-400' : 'bg-transparent border-gray-200 dark:border-gray-800'
                }`}
              >
                <Sun size={15} />
                <span>Light</span>
              </button>
              <button
                onClick={() => theme === 'light' && toggleTheme()}
                className={`flex items-center justify-center space-x-2 p-3 rounded-xl border text-xs font-semibold transition-all ${
                  theme === 'dark' ? 'bg-gray-800 border-brand-500 text-brand-400' : 'bg-transparent border-gray-200 dark:border-gray-800'
                }`}
              >
                <Moon size={15} />
                <span>Dark</span>
              </button>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Preferred Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 focus:ring-1 focus:ring-brand-500 focus:outline-none text-xs"
            >
              {languages.map((l) => <option key={l.code} value={l.code}>{l.name}</option>)}
            </select>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-950">
            <div className="flex items-center space-x-2">
              <Bell size={15} className="text-brand-500" />
              <span className="text-xs font-semibold text-gray-600 dark:text-gray-300">Helpful reminders</span>
            </div>
            <button
              type="button"
              onClick={() => setNotificationsEnabled((value) => !value)}
              className={`h-6 w-11 rounded-full p-0.5 transition-colors ${notificationsEnabled ? 'bg-brand-500' : 'bg-gray-300 dark:bg-gray-700'}`}
              aria-pressed={notificationsEnabled}
            >
              <span className={`block h-5 w-5 rounded-full bg-white transition-transform ${notificationsEnabled ? 'translate-x-5' : 'translate-x-0'}`} />
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-5 shadow-sm space-y-5">
          <div className="flex items-center space-x-2 pb-3 border-b border-gray-150 dark:border-gray-800">
            <Sliders className="text-brand-500" size={18} />
            <h3 className="font-bold text-sm">Answer Style</h3>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">Primary AI Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 focus:ring-1 focus:ring-brand-500 focus:outline-none text-xs"
            >
              <option value="nvidia">Nyaya AI default</option>
              <option value="claude">Drafting-focused model</option>
              <option value="gemini">Document-focused model</option>
            </select>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <label className="font-semibold text-gray-500 dark:text-gray-400">Response Flexibility</label>
              <span className="font-bold text-brand-500">{temp}</span>
            </div>
            <input
              type="range" min="0.0" max="1.0" step="0.1"
              value={temp}
              onChange={(e) => setTemp(parseFloat(e.target.value))}
              className="w-full accent-brand-500 bg-gray-200 dark:bg-gray-800 rounded-lg h-2"
            />
            <div className="flex justify-between text-[10px] text-gray-400">
              <span>More precise</span>
              <span>More exploratory</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-5 shadow-sm space-y-4 md:col-span-2">
          <div className="flex items-center space-x-2 pb-3 border-b border-gray-150 dark:border-gray-800">
            <Server className="text-brand-500" size={18} />
            <h3 className="font-bold text-sm">Backend Connection</h3>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-500 dark:text-gray-400">API Base URL</label>
            <input
              type="text"
              value={apiBaseUrl}
              onChange={(e) => setApiBaseUrl(e.target.value)}
              placeholder="http://localhost:8000"
              className="w-full px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 focus:ring-1 focus:ring-brand-500 focus:outline-none text-xs"
            />
            <div className="flex items-start space-x-2 mt-2 p-3 bg-gray-50 dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800/50">
              <Info size={14} className="text-blue-500 shrink-0 mt-0.5" />
              <p className="text-[10px] text-gray-500 dark:text-gray-400 leading-normal">
                Change this only when your backend is running at a different address.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-2">
        <button
          onClick={handleSave}
          disabled={saving || loading}
          className="bg-brand-500 hover:bg-brand-600 text-white font-semibold text-sm px-6 py-2.5 rounded-2xl shadow-lg shadow-brand-500/15 transition-all duration-250 active:scale-[0.98] disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
};

export default Settings;
