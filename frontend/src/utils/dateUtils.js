/**
 * تجميع الجلسات حسب التاريخ (مثل ChatGPT)
 * @param {Array} sessions - قائمة الجلسات من الخادم
 * @returns {Object} - كائن يحتوي على مجموعات (اليوم، الأمس، ...)
 */
export const groupSessionsByDate = (sessions) => {

  if (!sessions || sessions.length === 0) return {};

  const now = new Date();
  
  
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const weekAgo = new Date(today);
  weekAgo.setDate(weekAgo.getDate() - 7);
  
  const monthAgo = new Date(today);
  monthAgo.setMonth(monthAgo.getMonth() - 1);

 
  const groups = {
    'اليوم': [],
    'الأمس': [],
    'هذا الأسبوع': [],
    'هذا الشهر': [],
    'الأقدم': []
  };

  sessions.forEach(session => {
  
    const date = new Date(session.created_at);
    const compareDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (compareDate.getTime() === today.getTime()) {
      groups['اليوم'].push(session);
    } else if (compareDate.getTime() === yesterday.getTime()) {
      groups['الأمس'].push(session);
    } else if (compareDate > weekAgo) {
      groups['هذا الأسبوع'].push(session);
    } else if (compareDate > monthAgo) {
      groups['هذا الشهر'].push(session);
    } else {
      groups['الأقدم'].push(session);
    }
  });

  
  const nonEmptyGroups = {};
  for (const [key, items] of Object.entries(groups)) {
    if (items.length > 0) {
      nonEmptyGroups[key] = items;
    }
  }

  return nonEmptyGroups;
};