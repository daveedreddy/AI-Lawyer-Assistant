import axios from 'axios';
import { authService } from './auth.service';
import { apiUrl } from './api';

export interface UploadAnalysisResult {
  fileName: string;
  fileSize: string;
  detectedType: string;
  summary: string;
  suggestedPrompts: string[];
  storageUrl?: string;
  documentId?: string;
}

export const uploadService = {
  async uploadDocument(
    file: File,
    sessionId?: string
  ): Promise<UploadAnalysisResult> {
    const token = await authService.getAccessToken();
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const formData = new FormData();
    formData.append('file', file);

    const url = sessionId
      ? `${apiUrl('/upload/')}?session_id=${encodeURIComponent(sessionId)}`
      : apiUrl('/upload/');

    const response = await axios.post<UploadAnalysisResult>(url, formData, { headers });
    return response.data;
  },
};
