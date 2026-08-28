import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import { useState } from 'react';

function App() {
  const { user, loading } = useAuth();
  const [authView, setAuthView] = useState('login');

  // إذا كان التحميل قيد التشغيل
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sky-500 mx-auto"></div>
          <p className="mt-4 text-slate-500">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  // إذا لم يكن المستخدم مسجلاً
  if (!user) {
    if (authView === 'login') {
      return <Login onSwitchToRegister={() => setAuthView('register')} />;
    } else {
      return <Register onSwitchToLogin={() => setAuthView('login')} />;
    }
  }

  // إذا كان المستخدم مسجلاً، اعرض الدردشة
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-green-600">✅ تم تسجيل الدخول بنجاح!</h1>
        <p className="text-slate-600">مرحباً بك: {user?.email || user?.displayName}</p>
        <button 
          onClick={() => {}} 
          className="mt-4 bg-red-500 text-white px-4 py-2 rounded-lg"
        >
          تسجيل الخروج
        </button>
      </div>
    </div>
  );
}

export default App;