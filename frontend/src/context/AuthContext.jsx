import React, { createContext, useState, useContext, useEffect } from 'react';
import { loginUser, registerUser, getCurrentUser } from '../services/api';

// إنشاء السياق (Context)
const AuthContext = createContext(null);

// Hook مخصص لاستخدام السياق بسهولة
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(() => localStorage.getItem('chat-token'));

  // تحميل بيانات المستخدم عند وجود Token
  useEffect(() => {
    const loadUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const userData = await getCurrentUser(token);
        setUser(userData);
      } catch (error) {
        console.error('فشل في تحميل المستخدم:', error);
        localStorage.removeItem('chat-token');
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, [token]);

  // دالة تسجيل الدخول
  const login = async (username, password) => {
    try {
      const response = await loginUser(username, password);
      const { access_token, user_id, username: userName } = response;
      
      localStorage.setItem('chat-token', access_token);
      localStorage.setItem('chat-user-id', user_id);
      setToken(access_token);
      setUser({ id: user_id, username: userName });
      
      return { success: true };
    } catch (error) {
      console.error('فشل تسجيل الدخول:', error);
      return { success: false, error: error.message || 'بيانات الدخول غير صحيحة' };
    }
  };

  // دالة التسجيل (إنشاء حساب)
  const register = async (username, email, password) => {
    try {
      const response = await registerUser(username, email, password);
      const { access_token, user_id, username: userName } = response;
      
      localStorage.setItem('chat-token', access_token);
      localStorage.setItem('chat-user-id', user_id);
      setToken(access_token);
      setUser({ id: user_id, username: userName });
      
      return { success: true };
    } catch (error) {
      console.error('فشل التسجيل:', error);
      return { success: false, error: error.message || 'فشل إنشاء الحساب' };
    }
  };

  // دالة تسجيل الخروج
  const logout = () => {
    localStorage.removeItem('chat-token');
    localStorage.removeItem('chat-user-id');
    setToken(null);
    setUser(null);
  };

  // القيم التي ستتاح لجميع مكونات التطبيق
  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};