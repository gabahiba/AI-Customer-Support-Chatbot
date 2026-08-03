import { useState } from 'react';
import { FiEdit2, FiTrash2, FiCheck, FiX } from 'react-icons/fi';

const SessionItem = ({ session, isActive, onSelect, onRename, onDelete, isDarkMode = false }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(session.title || 'محادثة جديدة');

  const handleRename = () => {
    if (editTitle.trim() && editTitle !== session.title) {
      onRename(session.session_id, editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(session.title || 'محادثة جديدة');
    setIsEditing(false);
  };

  // ========== الثيمات ==========
  const activeBg = isDarkMode ? 'bg-gray-800 text-white' : 'bg-[#E5E5EA] text-gray-900';
  const hoverBg = isDarkMode ? 'hover:bg-gray-800' : 'hover:bg-[#E5E5EA]';
  const textColor = isDarkMode ? 'text-gray-300' : 'text-gray-700';
  const inputBg = isDarkMode ? 'bg-gray-900 border-blue-500 text-white' : 'bg-white border-[#0084FF] text-gray-900';

  return (
    <div className={`group flex items-center gap-2 rounded-2xl border p-2.5 transition-all ${isActive ? `${activeBg} border` : `${hoverBg} ${textColor} border-transparent`}`}>
      <div onClick={() => onSelect(session.session_id)} className="min-w-0 flex-1">
        {isEditing ? (
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRename()}
            className={`w-full rounded-lg border px-2 py-1 text-sm outline-none focus:ring-1 focus:ring-sky-500 ${inputBg}`}
            autoFocus
          />
        ) : (
          <span className="block truncate text-sm font-medium">{session.title || 'محادثة جديدة'}</span>
        )}
      </div>

      <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        {isEditing ? (
          <>
            <button onClick={handleRename} className="rounded p-1 text-green-500 hover:bg-green-500/10">
              <FiCheck size={14} />
            </button>
            <button onClick={handleCancel} className="rounded p-1 text-red-500 hover:bg-red-500/10">
              <FiX size={14} />
            </button>
          </>
        ) : (
          <>
            <button onClick={() => setIsEditing(true)} className="rounded p-1 text-slate-400 hover:bg-sky-500/10 hover:text-sky-500">
              <FiEdit2 size={14} />
            </button>
            <button onClick={() => onDelete(session.session_id)} className="rounded p-1 text-slate-400 hover:bg-red-500/10 hover:text-red-500">
              <FiTrash2 size={14} />
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default SessionItem;