import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Toaster } from './components/ui/sonner';
import CookieConsent from './components/CookieConsent';
import { api } from './services/api';
import { CartProvider } from './context/CartContext';

// Configure axios for backward compatibility with cookie-based pages
axios.defaults.withCredentials = true;

// Global axios interceptor: auto-refresh token on 401
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error) => {
  failedQueue.forEach(p => error ? p.reject(error) : p.resolve());
  failedQueue = [];
};

axios.interceptors.response.use(
  res => res,
  async error => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/login') && !originalRequest.url?.includes('/auth/refresh')) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve: () => resolve(axios(originalRequest)), reject });
        });
      }
      originalRequest._retry = true;
      isRefreshing = true;
      try {
        await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/auth/refresh`, {}, { withCredentials: true });
        processQueue(null);
        return axios(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ReleasesPage from './pages/ReleasesPage';
import ReleaseDetailPage from './pages/ReleaseDetailPage';
import CreateReleasePage from './pages/CreateReleasePage';
import ReleaseWizardPage from './pages/ReleaseWizardPage';
import AnalyticsPage from './pages/AnalyticsPage';
import WalletPage from './pages/WalletPage';
import SettingsPage from './pages/SettingsPage';
import AuthCallback from './pages/AuthCallback';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AdminSubmissionsPage from './pages/AdminSubmissionsPage';
import AdminUsersPage from './pages/AdminUsersPage';
import AdminBeatsPage from './pages/AdminBeatsPage';
import AdminRoyaltyImportPage from './pages/AdminRoyaltyImportPage';
import AdminUserDetailPage from './pages/AdminUserDetailPage';
import AdminCampaignsPage from './pages/AdminCampaignsPage';
import AdminLeadsPage from './pages/AdminLeadsPage';
import AdminFeatureAnnouncementsPage from './pages/AdminFeatureAnnouncementsPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import AgreementPage from './pages/AgreementPage';
import PricingPage from './pages/PricingPage';
import ServicesPage from './pages/ServicesPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import PromotingPage from './pages/PromotingPage';
import PublishingPage from './pages/PublishingPage';
import StoresPage from './pages/StoresPage';
import InstrumentalsPage from './pages/InstrumentalsPage';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import SpotifyCanvasPage from './pages/SpotifyCanvasPage';
import ContentIdPage from './pages/ContentIdPage';
import MyPurchasesPage from './pages/MyPurchasesPage';
import CollaborationsPage from './pages/CollaborationsPage';
import PreSaveManagerPage, { PreSaveLandingPage } from './pages/PreSavePage';
import FanAnalyticsPage from './pages/FanAnalyticsPage';
import RevenueAnalyticsPage from './pages/RevenueAnalyticsPage';
import LeaderboardPage from './pages/LeaderboardPage';
import GoalsPage from './pages/GoalsPage';
import ArtistProfilePage from './pages/ArtistProfilePage';
import RoleSelectionPage from './pages/RoleSelectionPage';
import LabelDashboardPage from './pages/LabelDashboardPage';
import AdminEmailSettingsPage from './pages/AdminEmailSettingsPage';
import AdminPromoCodesPage from './pages/AdminPromoCodesPage';
import ReferralPage from './pages/ReferralPage';
import AdminReferralsPage from './pages/AdminReferralsPage';
import AdminAnalyticsReportsPage from './pages/AdminAnalyticsReportsPage';
import AdminContractsPage from './pages/AdminContractsPage';
import AdminPayoutsPage from './pages/AdminPayoutsPage';
import CalendarPage from './pages/CalendarPage';
import CollabHubPage from './pages/CollabHubPage';
import MessagesPage from './pages/MessagesPage';
import RoyaltySplitsPage from './pages/RoyaltySplitsPage';
import PageBuilderPage from './pages/PageBuilderPage';
import SpotifyAnalyticsPage from './pages/SpotifyAnalyticsPage';
import FeaturesPage from './pages/FeaturesPage';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Inactivity timeout (30 minutes)
const INACTIVITY_TIMEOUT = 30 * 60 * 1000;

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Activity tracking for inactivity timeout
  const updateActivity = useCallback(() => {
    localStorage.setItem('lastActivity', Date.now().toString());
  }, []);

  // Check for inactivity timeout
  useEffect(() => {
    if (!user || !token) return;
    const checkInactivity = () => {
      const lastActivityTime = parseInt(localStorage.getItem('lastActivity') || Date.now().toString());
      if (Date.now() - lastActivityTime > INACTIVITY_TIMEOUT) {
        console.log('Session expired due to inactivity');
        performLogout();
      }
    };
    const interval = setInterval(checkInactivity, 60000);
    return () => clearInterval(interval);
  }, [user, token]);

  // Activity listeners
  useEffect(() => {
    const handleActivity = () => updateActivity();
    window.addEventListener('click', handleActivity);
    window.addEventListener('keypress', handleActivity);
    window.addEventListener('scroll', handleActivity);
    return () => {
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('keypress', handleActivity);
      window.removeEventListener('scroll', handleActivity);
    };
  }, [updateActivity]);

  // Load stored auth on mount
  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      if (storedToken && storedUser) {
        const parsedUser = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
        api.setToken(storedToken);
        updateActivity();
      } else {
        // Fallback: try cookie-based auth check
        try {
          const response = await fetch(`${API}/auth/me`, { credentials: 'include' });
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          }
        } catch {}
      }
    } catch (error) {
      console.error('Error loading auth:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await api.login(email, password);
    const accessToken = response.access_token;
    const userData = response.user;
    setToken(accessToken);
    setUser(userData);
    api.setToken(accessToken);
    localStorage.setItem('token', accessToken);
    localStorage.setItem('user', JSON.stringify(userData));
    updateActivity();
    return userData;
  };

  const register = async (data) => {
    const response = await api.register(
      data.email, data.password, data.artist_name || data.name, data.name,
      data.user_role, data.legal_name, data.country,
      data.recaptcha_token, data.state, data.town, data.post_code
    );
    const accessToken = response.access_token;
    const userData = response.user;
    setToken(accessToken);
    setUser(userData);
    api.setToken(accessToken);
    localStorage.setItem('token', accessToken);
    localStorage.setItem('user', JSON.stringify(userData));
    updateActivity();
    return userData;
  };

  const performLogout = () => {
    setToken(null);
    setUser(null);
    api.setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('lastActivity');
  };

  const logout = async () => {
    try {
      await fetch(`${API}/auth/logout`, { method: 'POST', credentials: 'include' });
    } catch {}
    performLogout();
  };

  const processGoogleSession = async (sessionId) => {
    const response = await fetch(`${API}/auth/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ session_id: sessionId })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to process session');
    // If the session endpoint returns a token, use it
    if (data.access_token) {
      setToken(data.access_token);
      setUser(data.user);
      api.setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    } else {
      setUser(data);
      localStorage.setItem('user', JSON.stringify(data));
    }
    updateActivity();
    return data;
  };

  const updateUser = (data) => {
    if (user) {
      const updatedUser = { ...user, ...data };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      updateActivity();
    }
  };

  const checkAuth = loadStoredAuth;

  return (
    <AuthContext.Provider value={{ user, setUser, token, loading, login, register, logout, processGoogleSession, checkAuth, updateUser, updateActivity }}>
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
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
};

// Admin Protected Route
const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  if (user.role !== 'admin') return <Navigate to="/dashboard" replace />;
  return children;
};

// App Router
const AppRouter = () => {
  const location = useLocation();
  if (location.hash?.includes('session_id=')) return <AuthCallback />;
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/releases" element={<ProtectedRoute><ReleasesPage /></ProtectedRoute>} />
      <Route path="/releases/new" element={<ProtectedRoute><ReleaseWizardPage /></ProtectedRoute>} />
      <Route path="/releases/:id" element={<ProtectedRoute><ReleaseDetailPage /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
      <Route path="/wallet" element={<ProtectedRoute><WalletPage /></ProtectedRoute>} />
      <Route path="/spotify-canvas" element={<ProtectedRoute><SpotifyCanvasPage /></ProtectedRoute>} />
      <Route path="/content-id" element={<ProtectedRoute><ContentIdPage /></ProtectedRoute>} />
      <Route path="/purchases" element={<ProtectedRoute><MyPurchasesPage /></ProtectedRoute>} />
      <Route path="/collaborations" element={<ProtectedRoute><CollaborationsPage /></ProtectedRoute>} />
              <Route path="/collab-hub" element={<ProtectedRoute><CollabHubPage /></ProtectedRoute>} />
              <Route path="/messages" element={<ProtectedRoute><MessagesPage /></ProtectedRoute>} />
              <Route path="/royalty-splits" element={<ProtectedRoute><RoyaltySplitsPage /></ProtectedRoute>} />
      <Route path="/presave-manager" element={<ProtectedRoute><PreSaveManagerPage /></ProtectedRoute>} />
      <Route path="/fan-analytics" element={<ProtectedRoute><FanAnalyticsPage /></ProtectedRoute>} />
      <Route path="/revenue" element={<ProtectedRoute><RevenueAnalyticsPage /></ProtectedRoute>} />
      <Route path="/leaderboard" element={<ProtectedRoute><LeaderboardPage /></ProtectedRoute>} />
      <Route path="/goals" element={<ProtectedRoute><GoalsPage /></ProtectedRoute>} />
              <Route path="/referrals" element={<ProtectedRoute><ReferralPage /></ProtectedRoute>} />
              <Route path="/calendar" element={<ProtectedRoute><CalendarPage /></ProtectedRoute>} />
      <Route path="/presave/:campaignId" element={<PreSaveLandingPage />} />
      <Route path="/artist/:slug" element={<ArtistProfilePage />} />
      <Route path="/select-role" element={<RoleSelectionPage />} />
      <Route path="/label" element={<ProtectedRoute><LabelDashboardPage /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
      <Route path="/spotify" element={<ProtectedRoute><SpotifyAnalyticsPage /></ProtectedRoute>} />
      <Route path="/features" element={<ProtectedRoute><FeaturesPage /></ProtectedRoute>} />
      <Route path="/admin" element={<AdminRoute><AdminDashboardPage /></AdminRoute>} />
      <Route path="/admin/submissions" element={<AdminRoute><AdminSubmissionsPage /></AdminRoute>} />
      <Route path="/admin/users" element={<AdminRoute><AdminUsersPage /></AdminRoute>} />
              <Route path="/admin/users/:userId" element={<AdminRoute><AdminUserDetailPage /></AdminRoute>} />
              <Route path="/admin/beats" element={<AdminRoute><AdminBeatsPage /></AdminRoute>} />
              <Route path="/admin/royalty-import" element={<AdminRoute><AdminRoyaltyImportPage /></AdminRoute>} />
              <Route path="/admin/campaigns" element={<AdminRoute><AdminCampaignsPage /></AdminRoute>} />
              <Route path="/admin/leads" element={<AdminRoute><AdminLeadsPage /></AdminRoute>} />
              <Route path="/admin/email-settings" element={<AdminRoute><AdminEmailSettingsPage /></AdminRoute>} />
              <Route path="/admin/promo-codes" element={<AdminRoute><AdminPromoCodesPage /></AdminRoute>} />
              <Route path="/admin/referrals" element={<AdminRoute><AdminReferralsPage /></AdminRoute>} />
              <Route path="/admin/analytics-reports" element={<AdminRoute><AdminAnalyticsReportsPage /></AdminRoute>} />
              <Route path="/admin/contracts" element={<AdminRoute><AdminContractsPage /></AdminRoute>} />
              <Route path="/admin/payouts" element={<AdminRoute><AdminPayoutsPage /></AdminRoute>} />
              <Route path="/admin/page-builder" element={<AdminRoute><PageBuilderPage /></AdminRoute>} />
              <Route path="/admin/page-builder/:slug" element={<AdminRoute><PageBuilderPage /></AdminRoute>} />
              <Route path="/admin/feature-announcements" element={<AdminRoute><AdminFeatureAnnouncementsPage /></AdminRoute>} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              <Route path="/agreement" element={<AgreementPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/services" element={<ServicesPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/promoting" element={<PromotingPage />} />
      <Route path="/publishing" element={<PublishingPage />} />
      <Route path="/stores" element={<StoresPage />} />
      <Route path="/leasing" element={<InstrumentalsPage />} />
      <Route path="/instrumentals" element={<InstrumentalsPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/forgot-password" element={<ResetPasswordPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <AppRouter />
          <Toaster position="top-right" />
          <CookieConsent />
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
export { API, BACKEND_URL };
