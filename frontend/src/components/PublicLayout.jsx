import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../App';
import { ShoppingCart, User, List, X, House, Disc, Tag, MusicNote, Megaphone, BookOpen, Briefcase, Info, Headset, Storefront, FileText, ShieldCheck, SignIn, UserPlus, ArrowUp } from '@phosphor-icons/react';

const PublicLayout = ({ children }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [animColor, setAnimColor] = useState('#7C4DFF');

  // Animated color cycling
  useEffect(() => {
    const colors = ['#7C4DFF', '#E040FB', '#FF4081'];
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % colors.length;
      setAnimColor(colors[idx]);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Scroll to top visibility
  useEffect(() => {
    const handleScroll = () => setShowScrollTop(window.scrollY > 400);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  const menuItems = [
    { path: '/', icon: <House className="w-5 h-5" />, label: 'Home' },
    { path: '/releases', icon: <Disc className="w-5 h-5" />, label: 'My Releases' },
    { path: '/pricing', icon: <Tag className="w-5 h-5" />, label: 'Pricing' },
    { path: '/leasing', icon: <MusicNote className="w-5 h-5" />, label: 'Leasing' },
    { path: '/promoting', icon: <Megaphone className="w-5 h-5" />, label: 'Promoting' },
    { path: '/publishing', icon: <BookOpen className="w-5 h-5" />, label: 'Publishing' },
    { path: '/services', icon: <Briefcase className="w-5 h-5" />, label: 'Our Services' },
    { path: '/about', icon: <Info className="w-5 h-5" />, label: 'About Us' },
    { path: '/contact', icon: <Headset className="w-5 h-5" />, label: 'Contact / Support' },
    { path: '/stores', icon: <Storefront className="w-5 h-5" />, label: 'Stores' },
  ];

  const handleNav = (path) => {
    setMenuOpen(false);
    setTimeout(() => navigate(path), 200);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-black/90 backdrop-blur-md" data-testid="public-header">
        <div className="flex items-center justify-between px-4 py-3">
          <button onClick={() => setMenuOpen(true)} className="p-2 z-20 hover:bg-white/10 rounded-lg transition-colors" data-testid="menu-toggle">
            <List className="w-6 h-6 text-white" />
          </button>
          
          <div className="absolute left-0 right-0 flex flex-col items-center pointer-events-none">
            <span className="text-[22px] font-extrabold tracking-[2px]" style={{ color: animColor, transition: 'color 2s ease' }}>KALMORI</span>
            <div className="w-10 h-[3px] rounded-full mt-1" style={{ backgroundColor: animColor, transition: 'background-color 2s ease' }} />
          </div>
          
          <div className="flex items-center gap-1 z-20">
            <button onClick={() => navigate(user ? '/dashboard' : '/login')} className="p-2 hover:bg-white/10 rounded-lg transition-colors" data-testid="header-account-btn">
              <User className="w-6 h-6" style={{ color: animColor, transition: 'color 2s ease' }} />
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main>{children}</main>

      {/* Slide-out Menu */}
      {menuOpen && (
        <div className="fixed inset-0 z-[100]" data-testid="slide-menu">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMenuOpen(false)} />
          <div className="absolute top-0 left-0 bottom-0 w-[85%] max-w-[320px] bg-[#0a0a0a] border-r border-[#1a1a1a] pt-[50px] animate-slideIn">
            <div className="flex justify-between items-center px-5 pt-2.5 pb-2">
              <span className="text-[22px] font-extrabold tracking-[2px]" style={{ color: animColor }}>KALMORI</span>
              <button onClick={() => setMenuOpen(false)} className="p-2"><X className="w-6 h-6 text-white" /></button>
            </div>
            <p className="px-5 mb-3 text-[13px] font-semibold tracking-wider text-[#E53935]">Your Music, Your Way</p>
            
            {/* Animated border */}
            <div className="h-[2px] mx-5 mb-4 rounded-full" style={{ backgroundColor: '#FF4444' }} />
            <div className="h-px bg-[#333] mx-5 mb-4" />
            
            <div className="flex-1 overflow-y-auto">
              {menuItems.map((item) => (
                <button key={item.path} onClick={() => handleNav(item.path)}
                  className={`flex items-center gap-4 w-full py-[18px] px-6 text-left transition-colors ${location.pathname === item.path ? 'bg-white/5 text-white' : 'text-white hover:bg-white/5'}`}
                  data-testid={`menu-${item.label.toLowerCase().replace(/[^a-z]/g, '-')}`}>
                  <span style={{ color: animColor }}>{item.icon}</span>
                  <span className="text-base font-medium">{item.label}</span>
                </button>
              ))}
              
              {/* Legal Links */}
              <div className="h-px bg-[#222] my-5 mx-6" />
              <button onClick={() => handleNav('/terms')} className="flex items-center gap-4 w-full py-[18px] px-6 text-left text-gray-400 hover:bg-white/5">
                <FileText className="w-5 h-5" />
                <span className="text-base font-medium">Terms & Conditions</span>
              </button>
              <button onClick={() => handleNav('/privacy')} className="flex items-center gap-4 w-full py-[18px] px-6 text-left text-gray-400 hover:bg-white/5">
                <ShieldCheck className="w-5 h-5" />
                <span className="text-base font-medium">Privacy Policy</span>
              </button>
              
              {/* Auth Buttons */}
              <div className="h-px bg-[#222] my-5 mx-6" />
              {!user ? (
                <>
                  <button onClick={() => handleNav('/login')} className="mx-6 my-2 py-4 rounded border border-[#7C4DFF] text-center text-[#7C4DFF] text-sm font-bold tracking-wider" data-testid="menu-signin">
                    <SignIn className="w-5 h-5 inline mr-2" />Sign In
                  </button>
                  <button onClick={() => handleNav('/register')} className="mx-6 my-2 py-4 rounded bg-[#7C4DFF] text-center text-white text-sm font-bold tracking-wider" data-testid="menu-create-account">
                    <UserPlus className="w-5 h-5 inline mr-2" />Create Account
                  </button>
                </>
              ) : (
                <button onClick={() => handleNav('/dashboard')} className="mx-6 my-2 py-4 rounded bg-[#7C4DFF] text-center text-white text-sm font-bold tracking-wider" data-testid="menu-dashboard">
                  Dashboard
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Scroll to Top */}
      {showScrollTop && (
        <button onClick={scrollToTop} className="fixed bottom-[90px] right-5 z-50 w-[50px] h-[50px] rounded-full flex items-center justify-center shadow-lg" style={{ backgroundColor: animColor }} data-testid="scroll-to-top">
          <ArrowUp className="w-6 h-6 text-white" weight="bold" />
        </button>
      )}
    </div>
  );
};

export default PublicLayout;
