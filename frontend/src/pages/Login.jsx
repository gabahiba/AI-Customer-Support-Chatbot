import React, { useState } from 'react';
import { FiUser, FiLock, FiLogIn, FiZap } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const Login = ({ onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const result = await login(username, password);
    if (!result.success) {
      setError(result.error || 'بيانات الدخول غير صحيحة');
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.14),_transparent_30%),linear-gradient(135deg,_#f8fbff_0%,_#f5f7fb_60%,_#eef2ff_100%)]">
      <div className="w-full max-w-md bg-white/70 backdrop-blur-xl border border-slate-200/80 rounded-3xl p-8 shadow-xl">
        <div className="text-center mb-8">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-100">
            <FiZap className="text-2xl text-sky-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">مرحباً بك</h1>
          <p className="text-slate-500 text-sm mt-1">سجل الدخول للوصول إلى مساعدك الذكي</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-2 rounded-xl text-sm text-center">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">اسم المستخدم</label>
            <div className="flex items-center border border-slate-300 rounded-xl px-3 py-2 focus-within:ring-2 focus-within:ring-sky-500 focus-within:border-transparent">
              <FiUser className="text-slate-400 mr-2" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="أدخل اسم المستخدم"
                className="w-full bg-transparent outline-none text-sm text-slate-900"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">كلمة المرور</label>
            <div className="flex items-center border border-slate-300 rounded-xl px-3 py-2 focus-within:ring-2 focus-within:ring-sky-500 focus-within:border-transparent">
              <FiLock className="text-slate-400 mr-2" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="أدخل كلمة المرور"
                className="w-full bg-transparent outline-none text-sm text-slate-900"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-br from-sky-500 to-blue-600 text-white font-medium py-2.5 rounded-xl hover:shadow-lg hover:shadow-sky-500/25 transition disabled:opacity-50"
          >
            <FiLogIn className="text-lg" />
            {isLoading ? 'جاري تسجيل الدخول...' : 'تسجيل الدخول'}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          ليس لديك حساب؟{' '}
          <button
            onClick={onSwitchToRegister}
            className="text-sky-600 font-semibold hover:underline"
          >
            إنشاء حساب جديد
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;