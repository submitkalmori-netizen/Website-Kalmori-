import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Toaster } from './components/ui/sonner';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ReleasesPage from './pages/ReleasesPage';
import ReleaseDetailPage from './pages/ReleaseDetailPage';
import CreateReleasePage from './pages/CreateReleasePage';
import AnalyticsPage from './pages/AnalyticsPage';
import WalletPage from './pages/WalletPage';
import SettingsPage from './pages/SettingsPage';
import AuthCallback from './pages/AuthCallback';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios
axios.defaults.withCredentials = true;

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    // CRITICAL: Skip auth check if returning from OAuth callback
    if (window.location.hash?.includes('session_id=')) {
      setLoading(false);
      return;
    }
    
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    setUser(response.data);
    return response.data;
  };

  const register = async (data) => {
    const response = await axios.post(`${API}/auth/register`, data);
    setUser(response.data);
    return response.data;
  };

  const logout = async () => {
    await axios.post(`${API}/auth/logout`);
    setUser(null);
  };

  const processGoogleSession = async (sessionId) => {
    const response = await axios.post(`${API}/auth/session`, { session_id: sessionId });
    setUser(response.data);
    return response.data;
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, register, logout, processGoogleSession, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#FF3B30] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

// App Router
const AppRouter = () => {
  const location = useLocation();

  // Handle OAuth callback - check synchronously during render
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/releases" element={<ProtectedRoute><ReleasesPage /></ProtectedRoute>} />
      <Route path="/releases/new" element={<ProtectedRoute><CreateReleasePage /></ProtectedRoute>} />
      <Route path="/releases/:id" element={<ProtectedRoute><ReleaseDetailPage /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
      <Route path="/wallet" element={<ProtectedRoute><WalletPage /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
        <Toaster position="top-right" />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
export { API, BACKEND_URL };
