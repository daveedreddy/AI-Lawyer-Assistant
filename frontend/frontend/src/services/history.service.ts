import axios from 'axios';
import { ChatSession, Message, Citation } from '../types';
import { authService } from './auth.service';
import { apiUrl } from './api';

const API = apiUrl('/history');

const getAuthHeaders = async (): Promise<Record<string, string>> => {
  const token = await authService.getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const mapMessage = (m: any): Message => ({
  id: m.id ?? String(Math.random()),
  sender: m.role === 'user' ? 'user' : 'ai',
  text: m.content ?? '',
  timestamp: m.timestamp ?? m.created_at ?? new Date().toISOString(),
  citations: m.citations ?? [],
});

const mapSession = (s: any): ChatSession => ({
  id: s.session_id ?? s.id,
  title: s.title ?? 'Untitled',
  messages: (s.messages ?? []).map(mapMessage),
  createdAt: s.created_at ?? new Date().toISOString(),
  updatedAt: s.updated_at ?? new Date().toISOString(),
  summary: s.summary,
});

export const historyService = {
  async getSessions(): Promise<ChatSession[]> {
    const headers = await getAuthHeaders();
    const { data } = await axios.get(`${API}/`, { headers });
    return (data as any[]).map(mapSession);
  },

  async getSessionById(id: string): Promise<ChatSession | null> {
    const headers = await getAuthHeaders();
    try {
      const { data } = await axios.get(`${API}/${id}`, { headers });
      return mapSession(data);
    } catch (err: any) {
      if (err?.response?.status === 404) return null;
      throw err;
    }
  },

  async createSession(title: string = 'New Question'): Promise<ChatSession> {
    const headers = await getAuthHeaders();
    const { data } = await axios.post(`${API}/`, { title }, { headers });
    return mapSession(data);
  },

  async updateSessionTitle(id: string, title: string): Promise<void> {
    const headers = await getAuthHeaders();
    await axios.patch(`${API}/${id}`, { title }, { headers });
  },

  async deleteSession(id: string): Promise<void> {
    const headers = await getAuthHeaders();
    await axios.delete(`${API}/${id}`, { headers });
  },

  async addMessage(
    sessionId: string,
    role: 'user' | 'ai',
    content: string,
    citations?: Citation[],
    confidence?: number
  ): Promise<Message> {
    const headers = await getAuthHeaders();
    const { data } = await axios.post(
      `${API}/${sessionId}/message`,
      { role, content, citations, confidence },
      { headers }
    );
    return mapMessage(data);
  },

  async deleteMessage(sessionId: string, messageId: string): Promise<void> {
    const headers = await getAuthHeaders();
    await axios.delete(`${API}/${sessionId}/message/${messageId}`, { headers });
  },
};
