import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Button } from './ui/button';
import { 
  MusicNotes, 
  House, 
  Disc, 
  ChartLineUp, 
  Wallet, 
  Gear,
  SignOut,
  List
} from '@phosphor-icons/react';

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

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-64 bg-[#0A0A0A] border-r border-white/10
        transform transition-transform duration-200 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="p-6 border-b border-white/10">
            <Link to="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-[#FF3B30] rounded-md flex items-center justify-center">
                <MusicNotes className="w-5 h-5 text-white" weight="bold" />
              </div>
              <span className="text-xl font-bold tracking-tight">TuneDrop</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-md text-sm transition-all duration-200
                  ${location.pathname === item.path 
                    ? 'bg-[#FF3B30]/10 text-[#FF3B30] border border-[#FF3B30]/20' 
                    : 'text-[#A1A1AA] hover:bg-white/5 hover:text-white'
                  }
                `}
                data-testid={`nav-${item.label.toLowerCase()}`}
              >
                {item.icon}
                {item.label}
              </Link>
            ))}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 px-4 py-3">
              <div className="w-8 h-8 rounded-full bg-[#FF3B30]/20 flex items-center justify-center text-[#FF3B30] font-semibold">
                {user?.name?.charAt(0).toUpperCase() || 'A'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.name || 'Artist'}</p>
                <p className="text-xs text-[#71717A] truncate">{user?.email}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              className="w-full mt-2 text-[#A1A1AA] hover:text-white hover:bg-white/5 justify-start"
              onClick={handleLogout}
              data-testid="logout-btn"
            >
              <SignOut className="w-5 h-5 mr-3" />
              Sign Out
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-30 glass border-b border-white/10">
          <div className="px-6 py-4 flex items-center justify-between">
            <button 
              className="lg:hidden p-2 hover:bg-white/5 rounded-md"
              onClick={() => setSidebarOpen(true)}
            >
              <List className="w-6 h-6" />
            </button>
            
            <div className="flex-1" />
            
            <div className="flex items-center gap-4">
              <span className="text-xs px-2 py-1 bg-[#FFCC00]/10 text-[#FFCC00] rounded font-mono uppercase">
                {user?.plan || 'Free'}
              </span>
              <Link to="/releases/new">
                <Button className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white" data-testid="new-release-btn">
                  New Release
                </Button>
              </Link>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 md:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
