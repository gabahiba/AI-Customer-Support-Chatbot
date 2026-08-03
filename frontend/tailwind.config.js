/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ألوان الخلفية الأساسية
        'bg-light': '#F7F7F8',        // خلفية الدردشة في النهاري (رمادي فاتح)
        'bg-dark': '#0A0A0A',         // خلفية الدردشة في الليلي (أسود)
        'sidebar-light': '#F0F0F2',   // خلفية الشريط الجانبي في النهاري
        'sidebar-dark': '#0D0D0D',    // خلفية الشريط الجانبي في الليلي
        // 🔹 ألوان الفقاعات
        'bubble-user': '#1d8cf4',
        'bubble-bot-light': '#FFFFFF',
        'bubble-bot-dark': '#1C1C1E',
        // 🔹 ألوان النصوص
        'text-light': '#111111',
        'text-dark': '#FFFFFF',
        'subtext-light': '#6B7280',
        'subtext-dark': '#9CA3AF',

        
      // 🔹 ألوان الحدود والمدخلات
      'border-light': '#E5E7EB',
      'border-dark': '#374151',
      'input-light': '#FFFFFF',
      'input-dark': '#1F2937',
      },
      fontFamily: {
        cairo: ['Cairo', 'sans-serif'],
      },
    },
  },
  plugins: [],
}