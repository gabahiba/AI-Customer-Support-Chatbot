import React, { createContext, useState, useContext, useEffect } from 'react';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged 
} from 'firebase/auth';
import { auth } from '../firebase';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("🔄 AuthProvider: بدء مراقبة حالة المستخدم");
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      console.log("👤 تغيرت حالة المستخدم:", user);
      if (user) {
        setUser(user);
      } else {
        setUser(null);
      }
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const login = async (email, password) => {
    try {
      console.log("🔐 محاولة تسجيل الدخول:", email);
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();
      localStorage.setItem('firebase-token', token);
      console.log("✅ تم تسجيل الدخول بنجاح");
      return { success: true };
    } catch (error) {
      console.error("❌ خطأ في تسجيل الدخول:", error);
      return { success: false, error: error.message };
    }
  };

  const register = async (email, password) => {
    try {
      console.log("📝 محاولة إنشاء حساب:", email);
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();
      localStorage.setItem('firebase-token', token);
      console.log("✅ تم إنشاء الحساب بنجاح");
      return { success: true };
    } catch (error) {
      console.error("❌ خطأ في إنشاء الحساب:", error);
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    await signOut(auth);
    localStorage.removeItem('firebase-token');
    console.log("🚪 تم تسجيل الخروج");
  };

  const value = { user, loading, login, register, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};