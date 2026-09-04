import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ================================================
// دوال المحادثات
// ================================================

export const sendMessage = async (sessionId, message, browserId) => {
  try {
    const response = await apiClient.post('/chat/', {
      session_id: sessionId,
      message: message,
      browser_id: browserId || 'unknown',
    });
    return response.data;
  } catch (error) {
    console.error('خطأ في الاتصال بالخادم:', error);
    throw new Error('عذراً، حدث خلل في الاتصال بالخادم.');
  }
};

export const uploadPdf = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post('/upload/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('خطأ في رفع الملف:', error);
    throw new Error('فشل رفع الملف. تأكد من أنه بصيغة PDF.');
  }
};

export const getSessions = async (browserId) => {
  try {
    const url = browserId ? `/sessions/?browser_id=${browserId}` : '/sessions/';
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    console.error('خطأ في جلب الجلسات:', error);
    throw new Error('فشل في تحميل قائمة المحادثات.');
  }
};

export const createSession = async (sessionId, title = 'محادثة جديدة', browserId) => {
  try {
    const url = browserId ? `/sessions/?browser_id=${browserId}` : '/sessions/';
    const response = await apiClient.post(url, {
      session_id: sessionId,
      title: title,
    });
    return response.data;
  } catch (error) {
    console.error('خطأ في إنشاء الجلسة:', error);
    throw new Error('فشل في إنشاء محادثة جديدة.');
  }
};

export const updateSessionTitle = async (sessionId, newTitle, browserId) => {
  try {
    const url = browserId ? `/sessions/${sessionId}?browser_id=${browserId}` : `/sessions/${sessionId}`;
    const response = await apiClient.put(url, { title: newTitle });
    return response.data;
  } catch (error) {
    console.error('خطأ في تحديث العنوان:', error);
    throw new Error('فشل في تغيير اسم المحادثة.');
  }
};

export const deleteSession = async (sessionId, browserId) => {
  try {
    const url = browserId ? `/sessions/${sessionId}?browser_id=${browserId}` : `/sessions/${sessionId}`;
    const response = await apiClient.delete(url);
    return response.data;
  } catch (error) {
    console.error('خطأ في حذف الجلسة:', error);
    throw new Error('فشل في حذف المحادثة.');
  }
};

export const getSessionMessages = async (sessionId, browserId) => {
  try {
    const url = browserId ? `/sessions/${sessionId}/messages?browser_id=${browserId}` : `/sessions/${sessionId}/messages`;
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    console.error('خطأ في جلب رسائل الجلسة:', error);
    throw new Error('فشل في تحميل رسائل المحادثة.');
  }
};