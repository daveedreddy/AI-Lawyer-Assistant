import React, { useState, useEffect } from 'react';
import {
  User,
  Scale,
  MapPin,
  BookOpen,
  CheckCircle,
  Edit3,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { profileService } from '../services/profile.service';

interface StatsShape {
  total_chats: number;
  documents_analyzed: number;
  drafts_generated: number;
  saved_citations: number;
}

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<StatsShape | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.fullName || '');
  const [barEnrollment, setBarEnrollment] = useState(user?.barEnrollment || '');
  const [practiceAreas, setPracticeAreas] = useState<string[]>(user?.practiceAreas || []);
  const [newArea, setNewArea] = useState('');
  const [saving, setSaving] = useState(false);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    profileService.getUserStats()
      .then((s) => setStats(s as StatsShape))
      .catch(() => setStats(null))
      .finally(() => setStatsLoading(false));
  }, []);

  const handleAddArea = () => {
    if (newArea.trim() && !practiceAreas.includes(newArea.trim())) {
      setPracticeAreas([...practiceAreas, newArea.trim()]);
      setNewArea('');
    }
  };

  const handleRemoveArea = (area: string) => {
    setPracticeAreas(practiceAreas.filter((a) => a !== area));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await profileService.updateProfile({ fullName, barEnrollment, practiceAreas });
      setIsEditing(false);
    } catch {
      // Update failed — silently stay in edit mode
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in relative z-10">

      {/* Profile Overview Card */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-3xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-brand-500/10 text-brand-500 border border-brand-500/20 flex items-center justify-center text-2xl font-black">
              {fullName.split(' ').map((n) => n[0]).join('').slice(0, 2)}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                {isEditing ? (
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="px-2 py-1 text-base border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 rounded-lg font-bold focus:ring-1 focus:ring-brand-500"
                  />
                ) : (
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">{fullName}</h2>
                )}
                <span className="flex items-center text-[10px] font-bold bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  <CheckCircle size={10} className="mr-1" /> Verified Advocate
                </span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{user?.email}</p>
              <div className="flex items-center space-x-3 text-xs text-gray-400 mt-2">
                <div className="flex items-center space-x-1">
                  <Scale size={13} />
                  {isEditing ? (
                    <input
                      type="text"
                      value={barEnrollment}
                      onChange={(e) => setBarEnrollment(e.target.value)}
                      placeholder="BCI Enrollment No."
                      className="px-1.5 py-0.5 text-xs border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 rounded-md focus:ring-1 focus:ring-brand-500"
                    />
                  ) : (
                    <span>BCI Code: {barEnrollment || 'N/A'}</span>
                  )}
                </div>
                <div className="flex items-center space-x-1">
                  <MapPin size={13} />
                  <span>India</span>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={() => isEditing ? handleSave() : setIsEditing(true)}
            disabled={saving}
            className="flex items-center space-x-1.5 px-4 py-2 border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl text-xs font-semibold transition-all disabled:opacity-50"
          >
            <Edit3 size={13} />
            <span>{saving ? 'Saving...' : isEditing ? 'Save Profile' : 'Edit Credentials'}</span>
          </button>
        </div>

        {/* Practice Areas */}
        <div className="mt-6 pt-5 border-t border-gray-100 dark:border-gray-800/80 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400">Practice Fields</h4>
          <div className="flex flex-wrap gap-2">
            {practiceAreas.map((area, idx) => (
              <span
                key={idx}
                className="flex items-center space-x-1 px-2.5 py-1 bg-gray-100 dark:bg-gray-800/80 border border-gray-200/50 dark:border-gray-700/50 rounded-lg text-xs font-medium"
              >
                <span>{area}</span>
                {isEditing && (
                  <button onClick={() => handleRemoveArea(area)} className="ml-1 text-red-500 hover:bg-red-500/10 rounded-full">×</button>
                )}
              </span>
            ))}
            {isEditing && (
              <div className="flex items-center space-x-1.5">
                <input
                  type="text"
                  placeholder="Add practice area"
                  value={newArea}
                  onChange={(e) => setNewArea(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddArea()}
                  className="px-2 py-0.5 text-xs border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-950 rounded-lg focus:outline-none"
                />
                <button onClick={handleAddArea} className="px-2 py-0.5 bg-brand-500 text-white rounded-lg text-xs">+</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Analytics Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {statsLoading ? (
          [...Array(4)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 dark:bg-gray-800 animate-pulse rounded-2xl" />
          ))
        ) : (
          <>
            <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-4 text-center">
              <p className="text-[10px] font-bold text-gray-400 uppercase">Total Chats</p>
              <p className="text-2xl font-black text-brand-500 mt-1">{stats?.total_chats ?? 0}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-4 text-center">
              <p className="text-[10px] font-bold text-gray-400 uppercase">Consultations</p>
              <p className="text-2xl font-black text-brand-500 mt-1">{stats?.total_chats ?? 0}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-4 text-center">
              <p className="text-[10px] font-bold text-gray-400 uppercase">Files Analyzed</p>
              <p className="text-2xl font-black text-brand-500 mt-1">{stats?.documents_analyzed ?? 0}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200/60 dark:border-gray-800/60 rounded-2xl p-4 text-center">
              <p className="text-[10px] font-bold text-gray-400 uppercase">Saved Citations</p>
              <p className="text-2xl font-black text-brand-500 mt-1">{stats?.saved_citations ?? 0}</p>
            </div>
          </>
        )}
      </div>

    </div>
  );
};

export default Profile;
