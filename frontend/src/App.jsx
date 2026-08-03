import { useState, useEffect, useRef } from 'react';
import { FiSend, FiPaperclip, FiMessageCircle, FiLoader, FiMoon, FiSun, FiZap, FiUploadCloud, FiMenu } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import Sidebar from './components/Sidebar';
import {
  sendMessage,
  uploadPdf,
  getSessions,
  createSession,
  updateSessionTitle,
  deleteSession,
  getSessionMessages,
} from './services/api';

function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window === 'undefined') return false;
    const stored = localStorage.getItem('chat-dark-mode');
    if (stored !== null) return stored === 'true';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [browserId, setBrowserId] = useState(() => {
    let storedId = localStorage.getItem('chat-browser-id');
    if (!storedId) {
      storedId = crypto.randomUUID();
      localStorage.setItem('chat-browser-id', storedId);
    }
    return storedId;
  });

  const messagesEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem('chat-dark-mode', String(isDarkMode));
  }, [isDarkMode]);

  useEffect(() => {
    loadSessions();
  }, [browserId]);

  useEffect(() => {
    if (activeSessionId) {
      loadSessionMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const loadSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const data = await getSessions(browserId);
      setSessions(data);
      if (data.length > 0 && !activeSessionId) {
        setActiveSessionId(data[0].session_id);
      }
    } catch (error) {
      console.error('فشل في تحميل الجلسات:', error);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const loadSessionMessages = async (sessionId) => {
    try {
      const data = await getSessionMessages(sessionId);
      setMessages(data);
    } catch (error) {
      console.error('فشل في تحميل الرسائل:', error);
      setMessages([]);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSession = await createSession(browserId, 'محادثة جديدة');
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(browserId);
      setMessages([]);
      setIsSidebarOpen(false);
    } catch (error) {
      console.error('فشل في إنشاء محادثة جديدة:', error);
    }
  };

  const handleSelectSession = (sessionId) => {
    if (sessionId === activeSessionId) return;
    setActiveSessionId(sessionId);
    setIsSidebarOpen(false);
  };

  const handleRenameSession = async (sessionId, newTitle) => {
    try {
      await updateSessionTitle(sessionId, newTitle);
      setSessions((prev) => prev.map((s) => (s.session_id === sessionId ? { ...s, title: newTitle } : s)));
    } catch (error) {
      console.error('فشل في تغيير الاسم:', error);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('هل أنت متأكد من حذف هذه المحادثة؟')) return;
    try {
      await deleteSession(sessionId);
      const updatedSessions = sessions.filter((s) => s.session_id !== sessionId);
      setSessions(updatedSessions);
      if (sessionId === activeSessionId) {
        if (updatedSessions.length > 0) {
          setActiveSessionId(updatedSessions[0].session_id);
        } else {
          setActiveSessionId(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('فشل في حذف المحادثة:', error);
    }
  };

  const handleSend = async () => {
    if (input.trim() === '' || isLoading || !activeSessionId) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendMessage(activeSessionId, input);
      const botMessage = { role: 'assistant', content: response.response };
      setMessages((prev) => [...prev, botMessage]);
      await loadSessions();
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: '⚠️ عذراً، حدث خطأ في الاتصال بالخادم.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    try {
      const result = await uploadPdf(file);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `✅ تم رفع الملف "${file.name}" بنجاح! (${result.chunks_stored} قطعة مخزنة)`,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ فشل رفع الملف: ${error.message}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode((prev) => !prev);
  };

  // ============================================================
  // 🎨 الثيمات (تم تعديل shellBg في الوضع الليلي)
  // ============================================================
  const shellBg = isDarkMode
    ? 'bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.08),_transparent_60%),#000000] text-slate-100'
    : 'bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.14),_transparent_30%),linear-gradient(135deg,_#f8fbff_0%,_#f5f7fb_60%,_#eef2ff_100%)] text-slate-900';
  const headerBg = isDarkMode ? 'bg-slate-900/90 border-slate-800/80' : 'bg-white/75 border-slate-200/80';
  const panelBg = isDarkMode ? 'bg-slate-900/70 border-slate-800/80' : 'bg-white/70 border-slate-200/80';
  const inputBg = isDarkMode ? 'bg-slate-800/90 border-slate-700 text-slate-100' : 'bg-white border-slate-300 text-slate-900';
  const userBubble = 'bg-gradient-to-br from-sky-500 to-blue-600 text-white shadow-lg shadow-sky-500/20';
  const botBubble = isDarkMode ? 'bg-slate-800/90 text-slate-100 border-slate-700' : 'bg-white text-slate-700 border-slate-200';
  const mutedText = isDarkMode ? 'text-slate-400' : 'text-slate-500';
  const accentText = isDarkMode ? 'text-sky-300' : 'text-sky-600';

  const today = new Date();
  const formattedDate = today.toLocaleDateString('ar-EG', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <div className={`flex h-screen ${shellBg} font-cairo transition-colors duration-300 relative`}>
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <div className={`
        fixed lg:relative z-50 h-full transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onNewChat={handleNewChat}
          onSelectSession={handleSelectSession}
          onRenameSession={handleRenameSession}
          onDeleteSession={handleDeleteSession}
          isLoading={isLoadingSessions}
          isDarkMode={isDarkMode}
        />
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <header className={`sticky top-0 z-10 ${headerBg} border-b backdrop-blur-xl py-3 px-4 sm:px-6 flex items-center justify-between shadow-sm`}>
          <div className="flex items-center gap-2 sm:gap-3">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-200/50 dark:hover:bg-slate-800/50 transition-colors"
              aria-label="Open sidebar"
            >
              <FiMenu className="text-xl" />
            </button>
            
            <button
              onClick={toggleDarkMode}
              className={`p-2.5 rounded-full transition-all ${isDarkMode ? 'bg-slate-800/80 hover:bg-slate-700' : 'bg-slate-100 hover:bg-slate-200'}`}
              aria-label="Toggle Dark Mode"
            >
              {isDarkMode ? <FiSun className="text-yellow-400 text-xl" /> : <FiMoon className="text-slate-600 text-xl" />}
            </button>
          </div>

          <div className="text-right">
            <div className="text-base sm:text-lg font-semibold">مرحباً بك</div>
            <div className={`text-xs sm:text-sm font-light ${mutedText}`}>مساعدك الذكي</div>
          </div>
        </header>

        <div className={`flex-1 overflow-y-auto p-3 sm:p-6 ${shellBg}`}>
          <div className="mx-auto flex w-full max-w-3xl flex-col gap-3 sm:gap-4">
            {messages.length === 0 ? (
              <div className={`rounded-3xl border ${panelBg} p-5 sm:p-8 text-center shadow-sm backdrop-blur-xl`}>
                <div className={`mx-auto mb-4 flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-2xl ${isDarkMode ? 'bg-sky-500/10' : 'bg-sky-100'}`}>
                  <FiZap className={`text-xl sm:text-2xl ${accentText}`} />
                </div>
                <h2 className="text-base sm:text-lg font-semibold">أهلاً وسهلاً! كيف يمكنني مساعدتك اليوم؟</h2>
                <p className={`mt-2 text-xs sm:text-sm ${mutedText}`}>
                  يمكنك سؤالي عن أي موضوع، أو رفع ملف PDF والبدء مباشرة.
                </p>
              </div>
            ) : (
              <>
                <div className="flex justify-center">
                  <span className={`rounded-full border px-3 sm:px-4 py-0.5 sm:py-1 text-[10px] sm:text-xs ${isDarkMode ? 'border-slate-700 bg-slate-800/80 text-slate-400' : 'border-slate-200 bg-white/80 text-slate-500'}`}>
                    {formattedDate}
                  </span>
                </div>

                {messages.map((msg, index) => (
                  <div key={`${msg.role}-${index}`} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] sm:max-w-[80%] rounded-3xl border px-3 sm:px-4 py-2 sm:py-3 shadow-sm ${msg.role === 'user' ? `${userBubble} rounded-br-md` : `${botBubble} rounded-bl-md}`}`}>
                      <div className={`mb-1 text-[10px] sm:text-xs font-semibold ${msg.role === 'assistant' ? accentText : 'opacity-80'}`}>
                        {msg.role === 'assistant' ? 'AI' : 'أنت'}
                      </div>
                      <div className="prose prose-sm max-w-none break-words dark:prose-invert">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))}
              </>
            )}

            {isLoading && (
              <div className="flex justify-start">
                <div className={`${botBubble} rounded-3xl rounded-bl-md border px-4 py-3 shadow-sm`}>
                  <div className="flex items-center gap-2">
                    <FiLoader className="animate-spin text-sky-500" />
                    <span className={mutedText}>البوت يكتب...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className={`${headerBg} border-t p-3 sm:p-4 backdrop-blur-xl`}>
          <div className="mx-auto flex max-w-3xl items-center gap-2">
            <label className={`flex h-10 w-10 sm:h-11 sm:w-11 items-center justify-center rounded-full transition ${isDarkMode ? 'text-slate-400 hover:bg-slate-800 hover:text-slate-200' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'} cursor-pointer`}>
              <FiPaperclip className="text-lg sm:text-xl" />
              <input type="file" accept=".pdf" onChange={handleFileUpload} className="hidden" />
            </label>

            <div className={`flex flex-1 items-center gap-2 rounded-full border px-3 py-1.5 sm:py-2 shadow-sm ${inputBg}`}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="اكتب رسالتك هنا..."
                className={`flex-1 bg-transparent text-xs sm:text-sm outline-none placeholder:font-light ${isDarkMode ? 'placeholder-slate-500' : 'placeholder-slate-400'}`}
                disabled={!activeSessionId}
              />
              <FiUploadCloud className={`text-base sm:text-lg ${mutedText}`} />
            </div>

            <button
              onClick={handleSend}
              className="flex h-10 w-10 sm:h-11 sm:w-11 items-center justify-center rounded-full bg-gradient-to-br from-sky-500 to-blue-600 text-white shadow-lg shadow-sky-500/20 transition disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!input.trim() || isLoading || !activeSessionId}
            >
              <FiSend className="text-base sm:text-lg" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;