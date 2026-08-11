// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDj9cEIGiz_f7-AFWNBGb2R0FuR3xu3OIY",
  authDomain: "hebaapp-3dda7.firebaseapp.com",
  projectId: "hebaapp-3dda7",
  storageBucket: "hebaapp-3dda7.firebasestorage.app",
  messagingSenderId: "342931373226",
  appId: "1:342931373226:web:f05963198c1b4ba83a64d3"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;