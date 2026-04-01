import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Button } from './ui/button';
import { MusicNotes, House, Disc, ChartLineUp, Wallet, Gear, SignOut, List, X, Plus, ShieldCheck } from '@phosphor-icons/react';

const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const navItems = [
    { path: '/dashboard', icon: <House className="w-5 h-5" />, label: 'Dashboard' },
    { path: '/releases', icon: <Disc className="w-5 h-5" />, label: 'Releases' },
    { path: '/analytics', icon: <ChartLineUp className="w-5 h-5" />, label: 'Analytics' },
    { path: '/wallet', icon: <Wallet className="w-5 h-5" />, label: 'Wallet' },
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
            <button className="lg:hidden p-2 hover:bg-white/5 rounded-lg" onClick={() => setSidebarOpen(true)}><List className="w-6 h-6" /></button>
            <div className="flex-1" />
            <div className="flex items-center gap-4">
              <span className="text-xs px-3 py-1 bg-[#FFD700]/10 text-[#FFD700] rounded-full font-semibold uppercase tracking-wider">{user?.plan || 'Free'}</span>
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
