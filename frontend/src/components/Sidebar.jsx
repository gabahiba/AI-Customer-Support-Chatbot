import { FiPlus, FiMessageCircle, FiSearch, FiZap } from 'react-icons/fi';
import SessionItem from './SessionItem';
import { groupSessionsByDate } from '../utils/dateUtils';

const Sidebar = ({
  sessions,
  activeSessionId,
  onNewChat,
  onSelectSession,
  onRenameSession,
  onDeleteSession,
  isLoading,
  isDarkMode = false,
}) => {
  const bgColor = isDarkMode ? 'bg-slate-950/95' : 'bg-slate-50/80';
  const textColor = isDarkMode ? 'text-slate-100' : 'text-slate-800';
  const subTextColor = isDarkMode ? 'text-slate-400' : 'text-slate-500';
  const borderColor = isDarkMode ? 'border-slate-800' : 'border-slate-200';
  const inputBg = isDarkMode ? 'bg-slate-900/80 border-slate-700 text-slate-100' : 'bg-white border-slate-200 text-slate-800';

  const groupedSessions = groupSessionsByDate(sessions);
  const groupKeys = Object.keys(groupedSessions);

  return (
    <div className={`flex h-screen w-80 flex-col border-r ${borderColor} ${bgColor} backdrop-blur-xl ${textColor}`}>
      <div className={`border-b ${borderColor} p-4`}>
        <div className={`mb-3 rounded-2xl border p-3 ${isDarkMode ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white/70'}`}>
          <div className="flex items-center gap-2">
            <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${isDarkMode ? 'bg-sky-500/10 text-sky-300' : 'bg-sky-100 text-sky-600'}`}>
              <FiZap size={18} />
            </div>
            <div>
              <div className="text-sm font-semibold">AI Assistant</div>
              <div className={`text-xs ${subTextColor}`}>مساعد ذكي جاهز</div>
            </div>
          </div>
        </div>

        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-600 px-4 py-2.5 font-medium text-white shadow-lg shadow-sky-500/20 transition hover:opacity-90"
        >
          <FiPlus size={18} />
          محادثة جديدة
        </button>
      </div>

      <div className="px-3 py-3">
        <div className={`flex items-center gap-2 rounded-2xl border px-3 py-2 transition focus-within:border-sky-500 ${inputBg}`}>
          <FiSearch size={16} className={subTextColor} />
          <input
            type="text"
            placeholder="بحث في المحادثات..."
            className="w-full bg-transparent text-sm outline-none"
          />
        </div>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-3 py-2 sidebar-scroll">
        {isLoading ? (
          <div className={`py-8 text-center text-sm ${subTextColor}`}>جاري التحميل...</div>
        ) : sessions.length === 0 ? (
          <div className={`py-8 text-center ${subTextColor}`}>
            <FiMessageCircle className="mx-auto mb-2 text-3xl" />
            <p className="text-sm">لا توجد محادثات</p>
            <p className="text-xs">ابدأ محادثة جديدة</p>
          </div>
        ) : (
          groupKeys.map((groupTitle) => (
            <div key={groupTitle} className="space-y-1">
              <div className={`px-2 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-[0.2em] ${subTextColor}`}>
                {groupTitle}
              </div>
              {groupedSessions[groupTitle].map((session) => (
                <SessionItem
                  key={session.session_id}
                  session={session}
                  isActive={session.session_id === activeSessionId}
                  onSelect={onSelectSession}
                  onRename={onRenameSession}
                  onDelete={onDeleteSession}
                  isDarkMode={isDarkMode}
                />
              ))}
            </div>
          ))
        )}
      </div>

      <div className={`border-t ${borderColor} p-3 text-center text-xs ${subTextColor}`}>
        {sessions.length} محادثة{sessions.length !== 1 ? 'ات' : ''}
      </div>
    </div>
  );
};

export default Sidebar;