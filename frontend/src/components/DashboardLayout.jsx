import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Button } from './ui/button';
import { MusicNotes, House, Disc, ChartLineUp, Wallet, Gear, SignOut, List, X, Plus, ShieldCheck, SpotifyLogo, YoutubeLogo, ArrowLeft, ShoppingBag, Bell, Check, UsersThree, Megaphone, HeartStraight, Lightning } from '@phosphor-icons/react';
import axios from 'axios';
import { API } from '../App';

const NotificationPanel = ({ notifications, onMarkRead, onMarkAllRead, onClose }) => (
  <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-[#111] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50" data-testid="notification-panel">
    <div className="flex items-center justify-between p-4 border-b border-white/10">
      <h3 className="text-sm font-bold text-white">Notifications</h3>
      {notifications.some(n => !n.read) && (
        <button onClick={onMarkAllRead} className="text-xs text-[#7C4DFF] hover:underline" data-testid="mark-all-read-btn">Mark all read</button>
      )}
    </div>
    <div className="max-h-80 overflow-y-auto">
      {notifications.length === 0 ? (
        <div className="p-6 text-center text-sm text-gray-500">No notifications yet</div>
      ) : (
        notifications.map(n => (
          <div key={n.id} className={`p-4 border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer ${!n.read ? (n.type === 'ai_insight' ? 'bg-[#E040FB]/5' : 'bg-[#7C4DFF]/5') : ''}`}
            onClick={() => !n.read && onMarkRead(n.id)} data-testid={`notification-${n.id}`}>
            <div className="flex items-start gap-3">
              {n.type === 'ai_insight' ? (
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Lightning className="w-3 h-3 text-white" weight="fill" />
                </div>
              ) : (
                !n.read && <div className="w-2 h-2 rounded-full bg-[#7C4DFF] mt-1.5 flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                {n.type === 'ai_insight' && (
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-[10px] font-bold text-[#E040FB] uppercase tracking-wider">AI Insight</span>
                    {n.metric_value && <span className="text-[10px] font-bold text-[#FFD700] bg-[#FFD700]/10 px-1.5 py-0.5 rounded">{n.metric_value}</span>}
                  </div>
                )}
                <p className="text-sm text-white leading-snug">{n.message}</p>
                {n.action_suggestion && (
                  <p className="text-xs text-[#7C4DFF] mt-1 leading-snug">{n.action_suggestion}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  {n.created_at ? new Date(n.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}
                </p>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  </div>
);

const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const notifRef = useRef(null);

  // Fetch notifications and unread count
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  // Close panel on outside click
  useEffect(() => {
    const handleClick = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) setShowNotifications(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const res = await axios.get(`${API}/notifications/unread-count`, { withCredentials: true });
      setUnreadCount(res.data.count || 0);
    } catch {}
  };

  const fetchNotifications = async () => {
    try {
      const res = await axios.get(`${API}/notifications`, { withCredentials: true });
      setNotifications(Array.isArray(res.data) ? res.data : []);
    } catch {}
  };

  const toggleNotifications = () => {
    if (!showNotifications) fetchNotifications();
    setShowNotifications(!showNotifications);
  };

  const markRead = async (id) => {
    try {
      await axios.put(`${API}/notifications/${id}/read`, {}, { withCredentials: true });
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch {}
  };

  const markAllRead = async () => {
    try {
      await axios.put(`${API}/notifications/read-all`, {}, { withCredentials: true });
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch {}
  };

  const navItems = [
    { path: '/dashboard', icon: <House className="w-5 h-5" />, label: 'Dashboard' },
    { path: '/releases', icon: <Disc className="w-5 h-5" />, label: 'Releases' },
    { path: '/analytics', icon: <ChartLineUp className="w-5 h-5" />, label: 'Analytics' },
    { path: '/wallet', icon: <Wallet className="w-5 h-5" />, label: 'Wallet' },
    { path: '/spotify-canvas', icon: <SpotifyLogo className="w-5 h-5" />, label: 'Spotify Canvas' },
    { path: '/content-id', icon: <YoutubeLogo className="w-5 h-5" />, label: 'Content ID' },
    { path: '/purchases', icon: <ShoppingBag className="w-5 h-5" />, label: 'My Purchases' },
    { path: '/collaborations', icon: <UsersThree className="w-5 h-5" />, label: 'Collaborations' },
    { path: '/presave-manager', icon: <Megaphone className="w-5 h-5" />, label: 'Pre-Save' },
    { path: '/fan-analytics', icon: <HeartStraight className="w-5 h-5" />, label: 'Fan Analytics' },
    { path: '/settings', icon: <Gear className="w-5 h-5" />, label: 'Settings' },
  ];

  const handleLogout = async () => { await logout(); navigate('/'); };

  return (
    <div className="min-h-screen bg-black text-white flex">
      {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />}

      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-[#0a0a0a] border-r border-white/10 transform transition-transform duration-200 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="h-full flex flex-col">
          <div className="p-6 border-b border-white/10 flex items-center justify-between">
            <Link to="/dashboard" className="flex flex-col items-start">
              <span className="text-xl font-black tracking-[3px] gradient-text">KALMORI</span>
              <div className="gradient-underline mt-1" />
            </Link>
            <button className="lg:hidden p-2" onClick={() => setSidebarOpen(false)}><X className="w-5 h-5" /></button>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => (
              <Link key={item.path} to={item.path} onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all ${location.pathname === item.path ? 'bg-[#7C4DFF]/10 text-[#7C4DFF] border border-[#7C4DFF]/30' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}
                data-testid={`nav-${item.label.toLowerCase()}`}>
                {item.icon} {item.label}
              </Link>
            ))}
            {user?.role === 'admin' && (
              <>
                <div className="border-t border-white/10 my-3" />
                <Link to="/admin" onClick={() => setSidebarOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-[#E53935] hover:bg-[#E53935]/10 transition-all"
                  data-testid="nav-admin">
                  <ShieldCheck className="w-5 h-5" /> Admin Panel
                </Link>
              </>
            )}
          </nav>

          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 px-4 py-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center text-white font-bold">
                {user?.name?.charAt(0).toUpperCase() || 'A'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.name || 'Artist'}</p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
            <Button variant="ghost" className="w-full mt-2 text-gray-400 hover:text-white hover:bg-white/5 justify-start" onClick={handleLogout} data-testid="logout-btn">
              <SignOut className="w-5 h-5 mr-3" /> Sign Out
            </Button>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-h-screen">
        <header className="sticky top-0 z-30 bg-black/80 backdrop-blur-lg border-b border-white/10">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button className="lg:hidden p-2 hover:bg-white/5 rounded-lg" onClick={() => navigate(-1)} data-testid="dashboard-back-btn"><ArrowLeft className="w-6 h-6" /></button>
              <span className="lg:hidden text-white text-[16px] font-bold">
                {location.pathname === '/dashboard' ? 'Dashboard' : location.pathname === '/releases' ? 'Releases' : location.pathname === '/analytics' ? 'Analytics' : location.pathname === '/wallet' ? 'Wallet' : location.pathname === '/purchases' ? 'My Purchases' : location.pathname === '/collaborations' ? 'Collaborations' : location.pathname === '/settings' ? 'Settings' : location.pathname === '/spotify-canvas' ? 'Spotify Canvas' : location.pathname === '/content-id' ? 'Content ID' : location.pathname.startsWith('/releases/') ? 'Release Details' : 'Dashboard'}
              </span>
            </div>
            <div className="flex-1" />
            <div className="flex items-center gap-4">
              <button className="lg:hidden p-2 hover:bg-white/5 rounded-lg" onClick={() => setSidebarOpen(true)}><List className="w-6 h-6" /></button>
              <span className="text-xs px-3 py-1 bg-[#FFD700]/10 text-[#FFD700] rounded-full font-semibold uppercase tracking-wider hidden sm:inline">{user?.plan || 'Free'}</span>
              {/* Notification Bell */}
              <div className="relative" ref={notifRef}>
                <button onClick={toggleNotifications} className="relative p-2 hover:bg-white/5 rounded-lg transition-colors" data-testid="notification-bell">
                  <Bell className="w-5 h-5 text-gray-400" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-[#E040FB] rounded-full flex items-center justify-center text-[10px] font-bold text-white" data-testid="unread-badge">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>
                {showNotifications && (
                  <NotificationPanel notifications={notifications} onMarkRead={markRead} onMarkAllRead={markAllRead} onClose={() => setShowNotifications(false)} />
                )}
              </div>
              <Link to="/releases/new">
                <button className="btn-animated px-4 py-2 rounded-full text-sm font-semibold text-white flex items-center gap-2" data-testid="new-release-btn">
                  <Plus className="w-4 h-4" /> New Release
                </button>
              </Link>
            </div>
          </div>
        </header>
        <main className="flex-1 p-6 md:p-8">{children}</main>
      </div>
    </div>
  );
};

export default DashboardLayout;
