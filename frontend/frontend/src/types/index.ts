export interface User {
  id: string;
  email: string;
  fullName: string;
  barEnrollment?: string;
  practiceAreas?: string[];
  createdAt: string;
}

export interface Citation {
  id: string;
  title: string;
  source: string;
  section?: string;
  description: string;
  url?: string;
}

export interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  citations?: Citation[];
  sources?: string[];
  confidence?: number;
  isSearchingWeb?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  updatedAt: string;
  createdAt: string;
  summary?: string;
}

export interface UserStats {
  casesAnalyzed: number;
  totalChats: number;
  draftsGenerated: number;
  savedCitations: number;
}
