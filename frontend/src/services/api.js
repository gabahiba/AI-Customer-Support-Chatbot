import axios from 'axios';


const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// 🔹 Interceptor لإضافة Token إلى كل طلب
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('firebase-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// الرابط الأساسي للخادم الخلفي (Backend)
// إذا كنت في التطوير المحلي، استخدم localhost، وإلا استخدم رابط Render
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// إنشاء كائن Axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ================================================
// إضافة Interceptor لإرسال Token مع كل طلب
// ================================================
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('chat-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ================================================
// دوال المصادقة (Authentication)
// ================================================

export const loginUser = async (username, password) => {
  const response = await apiClient.post('/auth/login', { username, password });
  return response.data;
};

export const registerUser = async (username, email, password) => {
  const response = await apiClient.post('/auth/register', { username, email, password });
  return response.data;
};

export const getCurrentUser = async (token) => {
  // نمرر token مباشرة لأن الـ Interceptor قد لا يعمل إذا لم يكن مخزناً
  const response = await axios.get(`${API_BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

// ================================================
// دوال المحادثات (Chat) - تُستخدم في App.jsx
// ================================================

export const sendMessage = async (sessionId, message) => {
  try {
    const response = await apiClient.post('/chat/', {
      session_id: sessionId,
      message: message,
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

export const getSessions = async () => {
  try {
    const response = await apiClient.get('/sessions/');
    return response.data;
  } catch (error) {
    console.error('خطأ في جلب الجلسات:', error);
    throw new Error('فشل في تحميل قائمة المحادثات.');
  }
};

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

export const deleteSession = async (sessionId) => {
  try {
    const response = await apiClient.delete(`/sessions/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('خطأ في حذف الجلسة:', error);
    throw new Error('فشل في حذف المحادثة.');
  }
};

export const getSessionMessages = async (sessionId) => {
  try {
    const response = await apiClient.get(`/sessions/${sessionId}/messages`);
    return response.data;
  } catch (error) {
    console.error('خطأ في جلب رسائل الجلسة:', error);
    throw new Error('فشل في تحميل رسائل المحادثة.');
  }
};