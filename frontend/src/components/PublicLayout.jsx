import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../App';
import {
  List, X, ArrowUp, User, ShoppingCart, House, Disc, CloudArrowUp, MusicNotes, PlusCircle,
  Megaphone, FileText, ChartLine, Speedometer, ChartBar, CurrencyDollar, Wallet as WalletIcon,
  ArrowCircleUp, CreditCard, UserCircle, Palette, Bell, CaretDown, CaretUp,
  Tag, MusicNote, Briefcase, Info, Headset, Storefront, ShieldCheck, SignIn, UserPlus, ArrowLeft
} from '@phosphor-icons/react';

const PublicLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [activeSubmenu, setActiveSubmenu] = useState(null);

  useEffect(() => {
    const handleScroll = () => setShowScrollTop(window.scrollY > 300);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isHomePage = location.pathname === '/';

  // Page title mapping for back button header
  const pageTitles = {
    '/pricing': 'Pricing',
    '/leasing': 'Leasing',
    '/promoting': 'Promotion',
    '/publishing': 'Publishing',
    '/services': 'Our Services',
    '/about': 'About Us',
    '/contact': 'Contact / Support',
    '/stores': 'Stores',
    '/terms': 'Terms & Conditions',
    '/privacy': 'Privacy Policy',
    '/login': 'Sign In',
    '/register': 'Create Account',
    '/reset-password': 'Reset Password',
    '/dashboard': 'Dashboard',
    '/releases': 'My Releases',
    '/releases/new': 'New Release',
    '/analytics': 'Analytics',
    '/wallet': 'Wallet',
    '/settings': 'Settings',
    '/spotify-canvas': 'Spotify Canvas',
    '/content-id': 'Content ID',
    '/instrumentals': 'Instrumentals',
  };

  const getPageTitle = () => {
    if (pageTitles[location.pathname]) return pageTitles[location.pathname];
    if (location.pathname.startsWith('/releases/')) return 'Release Details';
    return 'Back';
  };

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  // Guest menu items — each with its OWN distinct icon color (matching screenshot exactly)
  const guestMenuItems = [
    { path: '/', icon: <House className="w-6 h-6" weight="fill" />, label: 'Home', color: '#E040FB' },
    { path: '/releases', icon: <Disc className="w-6 h-6" weight="fill" />, label: 'My Releases', color: '#4CAF50' },
    { path: '/pricing', icon: <Tag className="w-6 h-6" weight="fill" />, label: 'Pricing', color: '#E040FB' },
    { path: '/leasing', icon: <MusicNote className="w-6 h-6" weight="fill" />, label: 'Leasing', color: '#FF4081' },
    { path: '/promoting', icon: <Megaphone className="w-6 h-6" weight="fill" />, label: 'Promoting', color: '#E040FB' },
    { path: '/publishing', icon: <FileText className="w-6 h-6" weight="fill" />, label: 'Publishing', color: '#FFD700' },
    { path: '/services', icon: <Briefcase className="w-6 h-6" weight="fill" />, label: 'Our Services', color: '#E040FB' },
    { path: '/about', icon: <Info className="w-6 h-6" weight="fill" />, label: 'About Us', color: '#E040FB' },
    { path: '/contact', icon: <Headset className="w-6 h-6" weight="fill" />, label: 'Contact / Support', color: '#E040FB' },
    { path: '/stores', icon: <Storefront className="w-6 h-6" weight="fill" />, label: 'Stores', color: '#E040FB' },
  ];

  // Logged-in user menu items with individual icon colors
  const userMenuItems = [
    { path: '/dashboard', icon: <House className="w-6 h-6" weight="fill" />, label: 'Dashboard', color: '#E040FB' },
    { path: '/releases', icon: <Disc className="w-6 h-6" weight="fill" />, label: 'My Releases', color: '#4CAF50' },
    {
      icon: <CloudArrowUp className="w-6 h-6" weight="fill" />, label: 'Distribute', color: '#7C4DFF',
      submenu: [
        { path: '/releases/new', icon: <MusicNotes className="w-5 h-5" />, label: 'Upload Music' },
        { path: '/releases', icon: <PlusCircle className="w-5 h-5" />, label: 'Add Tracks' },
      ]
    },
    { path: '/promoting', icon: <Megaphone className="w-6 h-6" weight="fill" />, label: 'Promoting', color: '#E040FB' },
    { path: '/publishing', icon: <FileText className="w-6 h-6" weight="fill" />, label: 'Publishing', color: '#FFD700' },
    {
      icon: <ChartLine className="w-6 h-6" weight="fill" />, label: 'Analytics', color: '#00B0FF',
      submenu: [
        { path: '/analytics', icon: <Speedometer className="w-5 h-5" />, label: 'Overview' },
        { path: '/analytics', icon: <ChartBar className="w-5 h-5" />, label: 'Stream Reports' },
        { path: '/wallet', icon: <CurrencyDollar className="w-5 h-5" />, label: 'Revenue' },
      ]
    },
    {
      icon: <WalletIcon className="w-6 h-6" weight="fill" />, label: 'Wallet', color: '#FF6B35',
      submenu: [
        { path: '/wallet', icon: <WalletIcon className="w-5 h-5" />, label: 'Balance' },
        { path: '/wallet', icon: <ArrowCircleUp className="w-5 h-5" />, label: 'Withdrawals' },
        { path: '/wallet', icon: <CreditCard className="w-5 h-5" />, label: 'Payment Methods' },
      ]
    },
  ];

  const handleNav = (path) => {
    closeMenu();
    setTimeout(() => navigate(path), 200);
  };

  const closeMenu = () => {
    setMenuOpen(false);
    setActiveSubmenu(null);
  };

  const toggleSubmenu = (label) => {
    setActiveSubmenu(activeSubmenu === label ? null : label);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-black border-b border-[#1a1a1a]" data-testid="public-header">
        <div className="flex items-center justify-between px-4 py-3">
          {isHomePage ? (
            <button onClick={() => setMenuOpen(true)} className="p-1 min-w-[44px] min-h-[44px] flex items-center justify-center" data-testid="menu-toggle">
              <List className="w-6 h-6 text-white" />
            </button>
          ) : (
            <button onClick={() => navigate(-1)} className="flex items-center gap-1 p-1 min-w-[44px] min-h-[44px]" data-testid="back-button">
              <ArrowLeft className="w-6 h-6 text-white" />
            </button>
          )}

          {/* KALMORI logo / Page title centered */}
          {isHomePage ? (
            <button onClick={() => navigate('/')} className="absolute left-0 right-0 flex flex-col items-center" style={{ pointerEvents: 'none' }}>
              <span className="text-[24px] font-extrabold tracking-[4px] text-[#E040FB] pointer-events-auto" style={{ textShadow: '0 0 10px rgba(224,64,251,0.5), 0 0 20px rgba(224,64,251,0.3)' }}>KALMORI</span>
              <div className="w-10 h-[3px] rounded-sm mt-1 bg-[#7C4DFF] pointer-events-auto" />
            </button>
          ) : (
            <span className="absolute left-0 right-0 text-center text-white text-[16px] font-bold pointer-events-none">{getPageTitle()}</span>
          )}

          <div className="flex items-center gap-2 z-20">
            {user && (
              <button onClick={() => navigate('/releases')} className="relative p-1" data-testid="header-cart-btn">
                <ShoppingCart className="w-6 h-6 text-[#E040FB]" />
              </button>
            )}
            {isHomePage ? (
              user ? (
                <button onClick={() => navigate('/settings')} className="p-1" data-testid="header-profile-btn">
                  <User className="w-6 h-6 text-[#E040FB]" weight="fill" />
                </button>
              ) : (
                <button onClick={() => navigate('/login')} className="p-1" data-testid="header-account-btn">
                  <User className="w-6 h-6 text-[#E040FB]" weight="fill" />
                </button>
              )
            ) : (
              <button onClick={() => setMenuOpen(true)} className="p-1 min-w-[44px] min-h-[44px] flex items-center justify-end" data-testid="menu-toggle-right">
                <List className="w-6 h-6 text-white" />
              </button>
            )}
          </div>
        </div>
      </header>

      <main>{children}</main>

      {/* Slide-out Menu */}
      {menuOpen && (
        <div className="fixed inset-0 z-[100]" data-testid="slide-menu">
          <div className="absolute inset-0 bg-black/70" onClick={closeMenu} />
          <div className="absolute top-0 left-0 bottom-0 w-[85%] max-w-[320px] bg-[#0a0a0a] border-r border-[#1a1a1a] flex flex-col animate-slideIn">
            {/* Menu Header */}
            <div className="flex items-center justify-between px-5 pt-[50px] pb-2">
              <div className="flex flex-col">
                <span className="text-[22px] font-extrabold tracking-[3px] text-[#E040FB]" style={{ textShadow: '0 0 10px rgba(224,64,251,0.5), 0 0 20px rgba(224,64,251,0.3)' }}>KALMORI</span>
                <div className="w-10 h-[3px] rounded-sm mt-1 bg-[#7C4DFF]" />
              </div>
              <button onClick={closeMenu} className="p-1"><X className="w-6 h-6 text-white" /></button>
            </div>

            {/* Tagline — bright red */}
            <p className="px-5 mb-3 text-[13px] font-semibold tracking-wider text-[#FF4444]">Your Music, Your Way</p>

            {/* Gray separator */}
            <div className="h-px bg-[#333] mx-5 mb-4" />

            {/* Scrollable Menu Content */}
            <div className="flex-1 overflow-y-auto px-5">
              {user ? (
                <>
                  {/* User Info */}
                  <div className="flex items-center bg-[#111] rounded-xl p-3.5 mb-6">
                    <div className="w-12 h-12 rounded-full bg-[#E53935] flex items-center justify-center mr-3 flex-shrink-0">
                      <span className="text-white text-lg font-bold">{user.artist_name?.charAt(0) || user.name?.charAt(0) || 'K'}</span>
                    </div>
                    <div className="min-w-0">
                      <p className="text-white text-base font-semibold truncate">{user.artist_name || user.name}</p>
                      <p className="text-white/80 text-[13px] mt-0.5 truncate">{user.email}</p>
                    </div>
                  </div>

                  {/* Logged-in Menu Items */}
                  {userMenuItems.map((item) => (
                    <div key={item.label}>
                      <button
                        onClick={() => item.submenu ? toggleSubmenu(item.label) : item.path && handleNav(item.path)}
                        className="flex items-center gap-4 w-full py-[14px] text-left"
                        data-testid={`menu-${item.label.toLowerCase().replace(/[^a-z]/g, '-')}`}
                      >
                        <span style={{ color: item.color }}>{item.icon}</span>
                        <span className="flex-1 text-white text-[16px] font-bold">{item.label}</span>
                        {item.submenu && (
                          activeSubmenu === item.label
                            ? <CaretUp className="w-4 h-4 text-gray-500" />
                            : <CaretDown className="w-4 h-4 text-gray-500" />
                        )}
                      </button>
                      {item.submenu && activeSubmenu === item.label && (
                        <div className="pl-10 pb-2">
                          {item.submenu.map((sub) => (
                            <button key={sub.label} onClick={() => handleNav(sub.path)}
                              className="flex items-center gap-3 w-full py-2.5 text-left"
                              data-testid={`submenu-${sub.label.toLowerCase().replace(/[^a-z]/g, '-')}`}>
                              <span className="text-[#ccc]">{sub.icon}</span>
                              <span className="text-[#ccc] text-sm">{sub.label}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}

                  <div className="h-px bg-[#222] my-4" />

                  <button onClick={() => handleNav('/settings')} className="flex items-center gap-4 w-full py-[14px] text-left">
                    <UserCircle className="w-6 h-6 text-[#E040FB]" weight="fill" />
                    <span className="text-white text-[16px] font-bold">Profile</span>
                  </button>
                  <button onClick={() => handleNav('/settings')} className="flex items-center gap-4 w-full py-[14px] text-left">
                    <Palette className="w-6 h-6 text-[#7C4DFF]" weight="fill" />
                    <span className="text-white text-[16px] font-bold">Theme Settings</span>
                  </button>
                  <button onClick={() => handleNav('/dashboard')} className="flex items-center gap-4 w-full py-[14px] text-left">
                    <Bell className="w-6 h-6 text-[#FF6B35]" weight="fill" />
                    <span className="text-white text-[16px] font-bold">Notifications</span>
                  </button>

                  <div className="h-px bg-[#222] my-4" />

                  <button onClick={() => handleNav('/terms')} className="flex items-center gap-4 w-full py-[14px] text-left">
                    <FileText className="w-6 h-6 text-[#E040FB]" weight="fill" />
                    <span className="text-white text-[16px] font-bold">Terms & Conditions</span>
                  </button>
                  <button onClick={() => handleNav('/privacy')} className="flex items-center gap-4 w-full py-[14px] text-left">
                    <ShieldCheck className="w-6 h-6 text-[#E040FB]" weight="fill" />
                    <span className="text-white text-[16px] font-bold">Privacy Policy</span>
                  </button>

                  <button onClick={async () => { closeMenu(); await logout(); navigate('/'); }}
                    className="flex items-center gap-4 w-full py-[14px] text-left" data-testid="menu-logout">
                    <SignIn className="w-6 h-6 text-[#E53935]" weight="fill" />
                    <span className="text-[#E53935] text-[16px] font-bold">Logout</span>
                  </button>
                </>
              ) : (
                <>
                  {/* Guest Menu — each icon with its own color */}
                  {guestMenuItems.map((item) => (
                    <button key={item.path} onClick={() => handleNav(item.path)}
                      className="flex items-center gap-4 w-full py-[14px] text-left"
                      data-testid={`menu-${item.label.toLowerCase().replace(/[^a-z]/g, '-')}`}>
                      <span style={{ color: item.color }}>{item.icon}</span>
                      <span className="text-white text-[16px] font-bold">{item.label}</span>
                    </button>
                  ))}

                  <div className="h-px bg-[#222] my-4" />

                  <button onClick={() => handleNav('/terms')} className="flex items-center gap-4 w-full py-[14px] text-left">
                    <FileText className="w-6 h-6 text-[#E040FB]" weight="fill" />
                    <span className="text-white text-[16px] font-bold">Terms & Conditions</span>
                  </button>
                  <button onClick={() => handleNav('/privacy')} className="flex items-center gap-4 w-full py-[14px] text-left">
                    <ShieldCheck className="w-6 h-6 text-[#E040FB]" weight="fill" />
                    <span className="text-white text-[16px] font-bold">Privacy Policy</span>
                  </button>

                  <div className="h-px bg-[#222] my-4" />

                  {/* Auth Buttons */}
                  <button onClick={() => handleNav('/login')}
                    className="w-full py-3.5 rounded-lg bg-[#E040FB] text-center text-white text-base font-semibold mb-3"
                    data-testid="menu-signin">
                    Sign In
                  </button>
                  <button onClick={() => handleNav('/register')}
                    className="w-full py-3.5 rounded-lg border border-[#E040FB] text-center text-[#E040FB] text-base font-semibold"
                    data-testid="menu-create-account">
                    Create Account
                  </button>
                </>
              )}
            </div>

            {/* Footer */}
            <div className="px-5 py-4 border-t border-[#1a1a1a]">
              <p className="text-[#666] text-xs text-center">&copy; 2026 Kalmori. All rights reserved.</p>
            </div>
          </div>
        </div>
      )}

      {/* Scroll to Top */}
      {showScrollTop && (
        <button onClick={scrollToTop} className="fixed bottom-[90px] right-5 z-50 w-[50px] h-[50px] rounded-full flex items-center justify-center bg-[#7C4DFF] shadow-lg shadow-[#7C4DFF]/30" data-testid="scroll-to-top">
          <ArrowUp className="w-6 h-6 text-white" weight="bold" />
        </button>
      )}
    </div>
  );
};

export default PublicLayout;
