import { useState, useMemo } from 'react';
import { FiPlus, FiMessageCircle, FiSearch } from 'react-icons/fi';
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
  // ========== حالة البحث ==========
  const [searchTerm, setSearchTerm] = useState('');

  // ========== تصفية المحادثات حسب نص البحث ==========
  const filteredSessions = useMemo(() => {
    if (!searchTerm.trim()) {
      return sessions; // إذا كان البحث فارغاً، نعرض كل المحادثات
    }
    const lowerSearch = searchTerm.toLowerCase().trim();
    return sessions.filter((session) =>
      session.title?.toLowerCase().includes(lowerSearch)
    );
  }, [sessions, searchTerm]);

  // ========== تجميع المحادثات المصفاة حسب التاريخ ==========
  const groupedSessions = groupSessionsByDate(filteredSessions);
  const groupKeys = Object.keys(groupedSessions);

  // ========== الثيمات ==========
  const bgColor = isDarkMode ? 'bg-sidebar-dark' : 'bg-sidebar-light';
  const textColor = isDarkMode ? 'text-text-dark' : 'text-text-light';
  const subTextColor = isDarkMode ? 'text-subtext-dark' : 'text-subtext-light';
  const borderColor = isDarkMode ? 'border-gray-800' : 'border-gray-200';
  const inputBg = isDarkMode ? 'bg-[#1C1C1E] border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-800';
  const inputPlaceholder = isDarkMode ? 'placeholder-gray-500' : 'placeholder-gray-400';

  return (
    <div className={`w-72 h-screen ${bgColor} border-l ${borderColor} flex flex-col ${textColor}`}>
      
      {/* زر محادثة جديدة */}
      <div className="p-4 border-b ${borderColor}">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 bg-[#0084FF] hover:bg-[#0070E0] text-white font-medium py-2.5 px-4 rounded-lg transition-colors"
        >
          <FiPlus size={20} />
          محادثة جديدة
        </button>
      </div>

      {/* ===== شريط البحث ===== */}
      <div className="px-3 py-3">
        <div className={`flex items-center gap-2 ${inputBg} rounded-lg px-3 py-2 border transition-colors focus-within:border-[#0084FF]`}>
          <FiSearch size={16} className={subTextColor} />
          <input
            type="text"
            placeholder="بحث في المحادثات..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`bg-transparent text-sm outline-none w-full ${textColor} ${inputPlaceholder}`}
          />
          {/* زر مسح البحث (يظهر فقط عند وجود نص) */}
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* ===== قائمة المحادثات ===== */}
      <div className="flex-1 overflow-y-auto px-3 py-2 sidebar-scroll space-y-4">
        {isLoading ? (
          <div className={`text-center ${subTextColor} py-8 text-sm`}>جاري التحميل...</div>
        ) : filteredSessions.length === 0 ? (
          <div className={`text-center ${subTextColor} py-8`}>
            {searchTerm ? (
              <>
                <FiSearch className="mx-auto text-3xl mb-2 opacity-50" />
                <p className="text-sm">لا توجد محادثات تطابق "<span className="font-semibold">{searchTerm}</span>"</p>
                <button
                  onClick={() => setSearchTerm('')}
                  className="text-xs text-[#0084FF] hover:underline mt-1"
                >
                  مسح البحث
                </button>
              </>
            ) : (
              <>
                <FiMessageCircle className="mx-auto text-3xl mb-2" />
                <p className="text-sm">لا توجد محادثات</p>
                <p className="text-xs">ابدأ محادثة جديدة</p>
              </>
            )}
          </div>
        ) : (
          groupKeys.map((groupTitle) => (
            <div key={groupTitle} className="space-y-1">
              <div className={`text-xs font-semibold ${subTextColor} uppercase tracking-wider px-2 pt-2 pb-1`}>
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

      {/* ===== تذييل (عدد المحادثات الظاهرة) ===== */}
      <div className={`border-t ${borderColor} p-3 text-xs ${subTextColor} text-center`}>
        {filteredSessions.length} محادثة{filteredSessions.length !== 1 ? 'ات' : ''}
        {searchTerm && ` (نتائج البحث)`}
      </div>
    </div>
  );
};

export default Sidebar;