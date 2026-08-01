import axios from 'axios';

// الرابط الأساسي للخادم الخلفي (Backend)
// لاحظ أن الخادم الخلفي يعمل على المنفذ 8000
const API_BASE_URL = 'http://localhost:8000';

// إنشاء كائن Axios مع إعدادات أساسية
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * إرسال رسالة إلى البوت
 * @param {string} sessionId - معرف الجلسة (لتذكر المحادثة)
 * @param {string} message - نص الرسالة
 * @returns {Promise} - رد البوت
 */
export const sendMessage = async (sessionId, message) => {
  try {
    const response = await apiClient.post('/chat/', {
      session_id: sessionId,
      message: message,
    });
    return response.data; // يعيد { session_id, response }
  } catch (error) {
    console.error('خطأ في الاتصال بالخادم:', error);
    // نعيد رسالة خطأ مفهومة للمستخدم
    throw new Error('عذراً، حدث خلل في الاتصال بالخادم. تأكد من أن الخادم الخلفي يعمل.');
  }
};

/**
 * (اختياري) رفع ملف PDF
 * @param {File} file - ملف PDF
 * @returns {Promise} - رسالة نجاح
 */
export const uploadPdf = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post('/upload/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('خطأ في رفع الملف:', error);
    throw new Error('فشل رفع الملف. تأكد من أنه بصيغة PDF.');
  }
};
/**
 * جلب قائمة جميع الجلسات (المحادثات)
 * @returns {Promise} - قائمة الجلسات
 */
export const getSessions = async () => {
  try {
    const response = await apiClient.get('/sessions/');
    return response.data;
  } catch (error) {
    console.error('خطأ في جلب الجلسات:', error);
    throw new Error('فشل في تحميل قائمة المحادثات.');
  }
};

/**
 * إنشاء جلسة جديدة
 * @param {string} sessionId - معرف الجلسة
 * @param {string} title - عنوان الجلسة (اختياري)
 * @returns {Promise} - بيانات الجلسة المنشأة
 */
export const createSession = async (sessionId, title = 'محادثة جديدة') => {
  try {
    const response = await apiClient.post('/sessions/', {
      session_id: sessionId,
      title: title,
    });
    return response.data;
  } catch (error) {
    console.error('خطأ في إنشاء الجلسة:', error);
    throw new Error('فشل في إنشاء محادثة جديدة.');
  }
};

/**
 * تحديث عنوان جلسة (إعادة تسمية)
 * @param {string} sessionId - معرف الجلسة
 * @param {string} newTitle - العنوان الجديد
 * @returns {Promise} - بيانات الجلسة المحدثة
 */
export const updateSessionTitle = async (sessionId, newTitle) => {
  try {
    const response = await apiClient.put(`/sessions/${sessionId}`, {
      title: newTitle,
    });
    return response.data;
  } catch (error) {
    console.error('خطأ في تحديث العنوان:', error);
    throw new Error('فشل في تغيير اسم المحادثة.');
  }
};

/**
 * حذف جلسة (وجميع رسائلها)
 * @param {string} sessionId - معرف الجلسة
 * @returns {Promise} - رسالة نجاح
 */
export const deleteSession = async (sessionId) => {
  try {
    const response = await apiClient.delete(`/sessions/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('خطأ في حذف الجلسة:', error);
    throw new Error('فشل في حذف المحادثة.');
  }
};

/**
 * جلب رسائل جلسة معينة
 * @param {string} sessionId - معرف الجلسة
 * @returns {Promise} - قائمة الرسائل
 */
export const getSessionMessages = async (sessionId) => {
  try {
    const response = await apiClient.get(`/sessions/${sessionId}/messages`);
    return response.data;
  } catch (error) {
    console.error('خطأ في جلب رسائل الجلسة:', error);
    throw new Error('فشل في تحميل رسائل المحادثة.');
  }
};
