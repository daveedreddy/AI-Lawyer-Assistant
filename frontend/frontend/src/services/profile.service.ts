import axios from 'axios';
import { authService } from './auth.service';
import { apiUrl } from './api';

export interface UserStats {
  total_chats: number;
  documents_analyzed: number;
  drafts_generated: number;
  saved_citations: number;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  bar_enrollment?: string;
  practice_areas: string[];
  location?: string;
  avatar_url?: string;
}

export interface UserSettings {
  theme: string;
  language: string;
  model_preference: string;
  notifications_enabled: boolean;
  temperature: number;
  api_base_url?: string;
}

const getHeaders = async (): Promise<Record<string, string>> => {
  const token = await authService.getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const profileService = {
  async getUserStats(): Promise<UserStats> {
    const headers = await getHeaders();
    const { data } = await axios.get(apiUrl('/profile/stats'), { headers });
    return data;
  },

  async getProfile(): Promise<UserProfile> {
    const headers = await getHeaders();
    const { data } = await axios.get(apiUrl('/profile/'), { headers });
    return data;
  },

  async updateProfile(updates: {
    fullName?: string;
    barEnrollment?: string;
    practiceAreas?: string[];
    location?: string;
  }): Promise<UserProfile> {
    const headers = await getHeaders();
    const body: Record<string, unknown> = {};
    if (updates.fullName !== undefined) body.full_name = updates.fullName;
    if (updates.barEnrollment !== undefined) body.bar_enrollment = updates.barEnrollment;
    if (updates.practiceAreas !== undefined) body.practice_areas = updates.practiceAreas;
    if (updates.location !== undefined) body.location = updates.location;

    const { data } = await axios.patch(apiUrl('/profile/'), body, { headers });
    return data;
  },

  async getSettings(): Promise<UserSettings> {
    const headers = await getHeaders();
    const { data } = await axios.get(apiUrl('/profile/settings'), { headers });
    return data;
  },

  async updateSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    const headers = await getHeaders();
    const { data } = await axios.patch(apiUrl('/profile/settings'), settings, { headers });
    return data;
  },
};
