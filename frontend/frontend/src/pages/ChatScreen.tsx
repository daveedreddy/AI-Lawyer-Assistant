import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import {
  Send,
  Paperclip,
  Scale,
  Search,
  ExternalLink,
  ChevronRight,
  X,
  BookOpen,
  FileText,
  AlertCircle,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';
import { chatService } from '../services/chat.service';
import { historyService } from '../services/history.service';
import { uploadService } from '../services/upload.service';
import { Message, Citation } from '../types';

const ChatScreen: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const messageEndRef = useRef<HTMLDivElement>(null);

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionTitle, setSessionTitle] = useState<string>('Everyday Legal Help');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchStep, setSearchStep] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  useEffect(() => {
    const loadSession = async () => {
      try {
        const currentId = id;

        if (!currentId) {
          const sessions = await historyService.getSessions();
          if (sessions.length > 0) {
            navigate(`/chat/${sessions[0].id}`, { replace: true });
            return;
          }
          const newSession = await historyService.createSession('New Question');
          navigate(`/chat/${newSession.id}`, { replace: true });
          return;
        }

        const session = await historyService.getSessionById(currentId);
        if (session) {
          setSessionId(session.id);
          setSessionTitle(session.title);
          setMessages(session.messages);
          setActiveCitation(null);
        } else {
          navigate('/chat', { replace: true });
        }
      } catch (error) {
        console.error('Could not load or create chat history session.', error);
      }
    };

    loadSession();
  }, [id, navigate]);

  useEffect(() => {
    const state = location.state as { initialPrompt?: string } | null;
    if (sessionId && state?.initialPrompt) {
      window.history.replaceState({}, document.title);
      handleSendMessage(state.initialPrompt);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, location.state]);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingText, isSearching]);

  const parseQuickOptions = (text: string) => {
    const options: string[] = [];
    const lines = text.split('\n');

    lines.forEach((line) => {
      const trimmed = line.trim();
      const match = trimmed.match(/^(?:[-*]\s*)?(?:Option\s*)?(?:[A-D]|[1-9])[\).]\s*(.+)$/i);
      if (match?.[1]) {
        options.push(match[1].trim());
      }
    });

    return options;
  };

  const handleOptionSelect = async (optionText: string) => {
    await handleSendMessage(optionText);
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend ?? inputText).trim();
    if (!text) return;

    let activeSessionId = sessionId;
    if (!activeSessionId) {
      try {
        const newSession = await historyService.createSession('New Question');
        activeSessionId = newSession.id;
        setSessionId(newSession.id);
        setSessionTitle(newSession.title);
        navigate(`/chat/${newSession.id}`, { replace: true });
      } catch (error) {
        console.error('Could not create saved chat session.', error);
        const errMsg: Message = {
          id: `err_${Date.now()}`,
          sender: 'ai',
        text: 'I could not create a saved question. Please verify your login and try again.',
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errMsg]);
        return;
      }
    }

    if (!textToSend) setInputText('');

    const userMsg: Message = {
      id: `temp_${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    setIsSearching(true);
      setSearchStep('Checking relevant laws and reliable sources...');
    const stepTimer = setTimeout(() => {
      setSearchStep('Organizing the answer in plain language...');
    }, 850);

    try {
      const response = await chatService.getResponse(text, activeSessionId, (chunk) => {
        clearTimeout(stepTimer);
        setIsSearching(false);
        setIsStreaming(true);
        setStreamingText(chunk);
      });

      const aiMsg: Message = {
        id: `ai_${Date.now()}`,
        sender: 'ai',
        text: response.answer,
        timestamp: new Date().toISOString(),
        citations: response.citations,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, aiMsg]);
      window.dispatchEvent(new Event('chat-history-updated'));
    } catch (error) {
      console.error('Chat request failed.', error);
      clearTimeout(stepTimer);
      const errMsg: Message = {
        id: `err_${Date.now()}`,
        sender: 'ai',
        text: 'I could not connect to Nyaya Samrakshan. Please check your connection and try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      clearTimeout(stepTimer);
      setIsSearching(false);
      setIsStreaming(false);
      setStreamingText('');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !sessionId) return;

    const file = files[0];
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size exceeds the 10 MB limit.');
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const result = await uploadService.uploadDocument(file, sessionId);

      const userMsg: Message = {
        id: `upload_user_${Date.now()}`,
        sender: 'user',
        text: `Please review this document: ${result.fileName}`,
        timestamp: new Date().toISOString(),
      };

      const docMsgText =
        `**Document Uploaded**: \`${result.fileName}\` (${result.fileSize})\n` +
        `**Detected Type**: *${result.detectedType}*\n\n` +
        `### Summary:\n${result.summary}`;

      const aiMsg: Message = {
        id: `upload_ai_${Date.now()}`,
        sender: 'ai',
        text: docMsgText,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMsg, aiMsg]);
      setShowUploadModal(false);
    } catch {
      setUploadError('I could not read this document. Please try a PDF, DOCX, TXT, PNG, or JPG file.');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const suggestedQuestions = [
    { text: 'What should I do if I receive an eviction notice?', label: 'Eviction notice' },
    { text: 'How do I check if a contract is legally valid?', label: 'Contract help' },
    { text: 'What are my basic rights during a police inquiry?', label: 'Police inquiry' },
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-transparent relative overflow-hidden -m-4 md:-m-6">
      <div className="flex-1 flex flex-col h-full overflow-hidden border-r border-gray-200/50 dark:border-gray-800/50 relative z-10 bg-transparent">
        <div className="h-12 border-b border-gray-200/50 dark:border-gray-800/50 px-4 md:px-6 bg-white/55 dark:bg-gray-950/55 backdrop-blur-md flex items-center justify-between">
          <div className="flex items-center space-x-2 truncate">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold truncate text-gray-600 dark:text-gray-400">
              {sessionTitle}
            </span>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center space-x-1 px-2.5 py-1 text-[11px] font-semibold text-brand-500 hover:bg-brand-500/10 rounded-lg border border-brand-500/20 transition-all"
          >
            <Paperclip size={12} />
            <span>Upload file</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-6 md:px-6 space-y-6">
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
              className="max-w-xl mx-auto text-center py-12 space-y-4"
            >
              <div className="p-4 bg-brand-500/10 text-brand-500 rounded-2xl w-fit mx-auto shadow-lg shadow-brand-500/10">
                <Sparkles size={40} />
              </div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Simple legal help for everyday questions</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                Ask about your rights, common legal issues, documents, or next steps. I can explain things in plain language and point you to reliable sources.
              </p>
              <div className="pt-4 space-y-2">
                <p className="text-[10px] uppercase font-bold text-gray-400 dark:text-gray-500 tracking-wider">Popular starters</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {suggestedQuestions.map((chip, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(chip.text)}
                      className="px-3 py-1.5 bg-white hover:bg-gray-100 dark:bg-gray-900 dark:hover:bg-gray-800/80 border border-gray-200 dark:border-gray-800 rounded-lg text-xs text-gray-600 dark:text-gray-300 transition-all"
                    >
                      {chip.label}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {messages.map((message) => {
            const isUser = message.sender === 'user';
            const quickOptions = !isUser ? parseQuickOptions(message.text) : [];

            return (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[85%] sm:max-w-2xl rounded-2xl p-4 md:p-5 shadow-sm border ${
                  isUser
                    ? 'bg-gray-800 border-gray-700 dark:bg-gray-900 text-white rounded-tr-lg'
                    : 'bg-white/85 dark:bg-gray-900/85 border-gray-200/80 dark:border-gray-800/80 rounded-tl-lg'
                }`}>
                  <div className="flex items-center space-x-1.5 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 mb-2">
                    {isUser ? (
                      <span>You</span>
                    ) : (
                      <span className="text-brand-500 flex items-center space-x-1">
                        <Scale size={10} />
                        <span>Nyaya Samrakshan</span>
                      </span>
                    )}
                  </div>

                  <div className={`prose ${isUser ? 'text-gray-100' : 'text-gray-800 dark:text-gray-200'}`}>
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                  </div>

                  {quickOptions.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {quickOptions.map((option, idx) => (
                        <button
                          key={`${message.id}-${idx}`}
                          onClick={() => handleOptionSelect(option)}
                          className="rounded-full border border-brand-200 bg-brand-50 px-3 py-1.5 text-xs font-semibold text-brand-700 transition-all hover:bg-brand-100 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-300"
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  )}

                  {message.citations && message.citations.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800/80 space-y-2">
                      <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider flex items-center space-x-1">
                        <BookOpen size={10} />
                  <span>Sources used</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {message.citations.map((cit) => (
                          <button
                            key={cit.id}
                            onClick={() => setActiveCitation(cit)}
                            className={`flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-medium border transition-all ${
                              activeCitation?.id === cit.id
                                ? 'bg-brand-500 border-brand-500 text-white shadow-md shadow-brand-500/10'
                                : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700/80 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300'
                            }`}
                          >
                            <span>{cit.title}</span>
                            <ChevronRight size={10} />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}

          {isSearching && (
            <div className="flex justify-start animate-pulse">
              <div className="bg-white/70 dark:bg-gray-900/70 border border-gray-200/50 dark:border-gray-800/50 rounded-2xl rounded-tl-lg p-4 max-w-sm flex items-center space-x-3 shadow-sm">
                <Search size={16} className="text-brand-500 animate-spin" />
                <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">{searchStep}</span>
              </div>
            </div>
          )}

          {isStreaming && (
            <div className="flex justify-start">
              <div className="bg-white/85 dark:bg-gray-900/85 border border-gray-200/80 dark:border-gray-800/80 rounded-2xl rounded-tl-lg p-4 md:p-5 shadow-sm max-w-2xl">
                <div className="flex items-center space-x-1.5 text-[10px] font-bold uppercase tracking-wider text-brand-500 mb-2">
                  <Scale size={10} />
                  <span>Preparing your answer...</span>
                </div>
                <div className="prose text-gray-800 dark:text-gray-200">
                  <ReactMarkdown>{streamingText}</ReactMarkdown>
                </div>
              </div>
            </div>
          )}

          <div ref={messageEndRef} />
        </div>

        <div className="p-4 border-t border-gray-200/60 dark:border-gray-800/60 bg-white/55 dark:bg-gray-950/55 backdrop-blur-md">
          <div className="max-w-4xl mx-auto flex items-center space-x-2">
            <button
              onClick={() => setShowUploadModal(true)}
              className="p-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-900 dark:hover:bg-gray-800 border border-gray-200 dark:border-gray-800 text-gray-500 dark:text-gray-400 rounded-xl active:scale-95 transition-all"
              title="Upload document"
            >
              <Paperclip size={18} />
            </button>
            <input
              type="text"
              placeholder="Ask about rights, documents, or a legal issue in simple words"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={isStreaming || isSearching}
              className="flex-1 py-3 px-4 border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all rounded-xl text-sm"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputText.trim() || isStreaming || isSearching}
              className="p-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-40 disabled:hover:bg-brand-500 text-white rounded-xl active:scale-95 transition-all shadow-md shadow-brand-500/10"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {activeCitation && (
        <aside className="w-80 h-full border-l border-gray-200/60 dark:border-gray-800/60 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md p-5 flex flex-col z-20 absolute right-0 md:static shadow-2xl md:shadow-none animate-slide-up">
          <div className="flex items-center justify-between pb-3 border-b border-gray-200 dark:border-gray-800">
            <div className="flex items-center space-x-2 text-brand-500">
              <BookOpen size={16} />
              <h3 className="font-bold text-sm">Source Details</h3>
            </div>
            <button
              onClick={() => setActiveCitation(null)}
              className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <X size={16} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto py-4 space-y-4">
            <div>
              <span className="text-[9px] font-bold text-brand-500 bg-brand-500/10 dark:bg-brand-500/5 px-2 py-0.5 rounded-full uppercase">
                {activeCitation.source}
              </span>
              <h4 className="text-base font-bold mt-2 text-gray-900 dark:text-white leading-snug">
                {activeCitation.title}
              </h4>
            </div>

            {activeCitation.section && (
              <div className="bg-gray-50 dark:bg-gray-950 p-3 rounded-xl border border-gray-200 dark:border-gray-800/50">
                <span className="text-[10px] font-semibold text-gray-400 uppercase">Section or Article</span>
                <p className="text-xs font-bold text-brand-600 dark:text-brand-400 mt-0.5">
                  {activeCitation.section}
                </p>
              </div>
            )}

            <div className="space-y-1.5">
              <span className="text-[10px] font-semibold text-gray-400 uppercase">Why it matters</span>
              <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed font-sans">
                {activeCitation.description}
              </p>
            </div>

            {activeCitation.url && (
              <a
                href={activeCitation.url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center space-x-1.5 text-xs text-brand-500 hover:underline"
              >
                <ExternalLink size={12} />
                <span>View official source</span>
              </a>
            )}

            <div className="p-3.5 bg-amber-500/5 border border-amber-500/10 rounded-xl flex items-start space-x-2 text-[10px] text-gray-500 dark:text-gray-400">
              <Scale size={14} className="text-amber-500 shrink-0 mt-0.5" />
              <span>Legal sources can change. Please verify important citations before acting on them.</span>
            </div>
          </div>
        </aside>
      )}

      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-950/40 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl max-w-md w-full p-6 shadow-2xl relative animate-slide-up">
            <button
              onClick={() => setShowUploadModal(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <X size={18} />
            </button>

            <div className="space-y-4">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 bg-brand-500/10 text-brand-500 rounded-xl">
                  <FileText size={20} />
                </div>
                <div>
                  <h3 className="font-bold text-base">Review a document</h3>
                  <p className="text-xs text-gray-400">Upload a notice, agreement, letter, or court paper for a simple summary</p>
                </div>
              </div>

              {uploadError && (
                <div className="flex items-center space-x-2 p-3 bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs rounded-xl">
                  <AlertCircle size={14} className="shrink-0" />
                  <span>{uploadError}</span>
                </div>
              )}

              {isUploading ? (
                <div className="p-12 flex flex-col items-center justify-center space-y-4 bg-gray-50/70 dark:bg-gray-950/30 rounded-xl border border-dashed border-gray-200 dark:border-gray-800">
                  <div className="w-8 h-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                    Reading the file and summarizing key points...
                  </p>
                </div>
              ) : (
                <label className="border-2 border-dashed border-gray-200 dark:border-gray-800 hover:border-brand-500 dark:hover:border-brand-500 p-8 rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all bg-gray-50/50 dark:bg-gray-950/20 group">
                  <FileText size={32} className="text-gray-400 group-hover:text-brand-500 transition-colors mb-2" />
                  <span className="text-xs font-semibold">Click to browse documents</span>
                  <span className="text-[10px] text-gray-400 mt-1">PDF, DOC, DOCX, TXT, PNG, JPG up to 10 MB</span>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              )}

              <div className="p-3 bg-blue-500/5 rounded-xl border border-blue-500/10 flex items-start space-x-2">
                <ShieldCheck size={14} className="text-blue-500 shrink-0 mt-0.5" />
                <p className="text-[10px] text-gray-500 dark:text-gray-400 leading-normal">
                  Your uploads are used to prepare this response. Avoid sharing highly sensitive information unless you are comfortable storing it in this account.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatScreen;
