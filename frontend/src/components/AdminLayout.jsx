import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Button } from './ui/button';
import { House, Users, ClipboardText, ChartBar, Gear, SignOut, List, X, ArrowLeft, ShieldCheck } from '@phosphor-icons/react';

const AdminLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const navItems = [
    { path: '/admin', icon: <ChartBar className="w-5 h-5" />, label: 'Overview', exact: true },
    { path: '/admin/submissions', icon: <ClipboardText className="w-5 h-5" />, label: 'Submissions' },
    { path: '/admin/users', icon: <Users className="w-5 h-5" />, label: 'Users' },
  ];

  const isActive = (item) => {
    if (item.exact) return location.pathname === item.path;
    return location.pathname.startsWith(item.path);
  };

  const handleLogout = async () => { await logout(); navigate('/'); };

  return (
    <div className="min-h-screen bg-black text-white flex">
      {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />}

      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-[#0a0a0a] border-r border-white/10 transform transition-transform duration-200 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="h-full flex flex-col">
          <div className="p-6 border-b border-white/10 flex items-center justify-between">
            <Link to="/admin" className="flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-[#E53935]" />
              <div className="flex flex-col">
                <span className="text-lg font-black tracking-[2px] text-[#E53935]">ADMIN</span>
                <span className="text-[10px] text-gray-500 tracking-wider">KALMORI</span>
              </div>
            </Link>
            <button className="lg:hidden p-2" onClick={() => setSidebarOpen(false)}><X className="w-5 h-5" /></button>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => (
              <Link key={item.path} to={item.path} onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all ${isActive(item) ? 'bg-[#E53935]/10 text-[#E53935] border border-[#E53935]/30' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}
                data-testid={`admin-nav-${item.label.toLowerCase()}`}>
                {item.icon} {item.label}
              </Link>
            ))}
            <div className="border-t border-white/10 my-4" />
            <Link to="/dashboard" className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-gray-400 hover:bg-white/5 hover:text-white" data-testid="admin-nav-artist-view">
              <ArrowLeft className="w-5 h-5" /> Artist Dashboard
            </Link>
          </nav>

          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 px-4 py-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#E53935] to-[#FF6F61] flex items-center justify-center text-white font-bold">
                {user?.name?.charAt(0).toUpperCase() || 'A'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.name || 'Admin'}</p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
            <Button variant="ghost" className="w-full mt-2 text-gray-400 hover:text-white hover:bg-white/5 justify-start" onClick={handleLogout} data-testid="admin-logout-btn">
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
            <span className="text-xs px-3 py-1 bg-[#E53935]/10 text-[#E53935] rounded-full font-semibold uppercase tracking-wider">Admin Panel</span>
          </div>
        </header>
        <main className="flex-1 p-6 md:p-8">{children}</main>
      </div>
    </div>
  );
};

export default AdminLayout;
