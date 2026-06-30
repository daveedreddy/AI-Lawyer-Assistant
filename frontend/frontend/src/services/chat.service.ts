import axios from 'axios';
import { Citation } from '../types';
import { authService } from './auth.service';

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  sources: string[];
  confidence: number;
  session_id: string | null;
}

const getAuthHeaders = async (): Promise<Record<string, string>> => {
  const token = await authService.getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const chatService = {
  async getResponse(
    prompt: string,
    sessionId: string,
    onProgress: (chunk: string) => void
  ): Promise<ChatResponse> {
    const headers = await getAuthHeaders();

    const response = await axios.post(
      `${API_BASE}/chat/`,
      { query: prompt, top_k: 5, session_id: sessionId },
      { headers }
    );

    const data = response.data;
    const answer: string = data.answer || '';

    // Simulate word-by-word streaming for smooth UX
    let current = '';
    for (const word of answer.split(' ')) {
      current += (current ? ' ' : '') + word;
      onProgress(current);
      await new Promise((r) => setTimeout(r, 15));
    }

    return {
      answer,
      citations: (data.citations ?? []).map((c: any) => ({
        id: c.id ?? String(Math.random()),
        title: c.title ?? 'Source',
        source: c.source ?? 'unknown',
        section: c.section,
        description: c.description ?? '',
        url: c.url,
      })),
      sources: data.sources ?? [],
      confidence: data.confidence ?? 0,
      session_id: data.session_id ?? sessionId,
    };
  },
};