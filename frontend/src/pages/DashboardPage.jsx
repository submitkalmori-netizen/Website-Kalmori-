import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API, useAuth } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { 
  Disc, 
  Play, 
  CurrencyDollar, 
  TrendUp,
  Plus,
  ArrowRight,
  Clock
} from '@phosphor-icons/react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const DashboardPage = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [releases, setReleases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, releasesRes] = await Promise.all([
          axios.get(`${API}/analytics/overview`),
          axios.get(`${API}/releases`)
        ]);
        setAnalytics(analyticsRes.data);
        setReleases(releasesRes.data.slice(0, 5));
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const stats = [
    {
      label: 'Total Streams',
      value: analytics?.total_streams?.toLocaleString() || '0',
      icon: <Play className="w-5 h-5" />,
      color: '#FF3B30',
      change: '+12.5%'
    },
    {
      label: 'Total Earnings',
      value: `$${analytics?.total_earnings?.toFixed(2) || '0.00'}`,
      icon: <CurrencyDollar className="w-5 h-5" />,
      color: '#22C55E',
      change: '+8.2%'
    },
    {
      label: 'Releases',
      value: analytics?.release_count || '0',
      icon: <Disc className="w-5 h-5" />,
      color: '#007AFF',
      change: null
    },
    {
      label: 'Downloads',
      value: analytics?.total_downloads?.toLocaleString() || '0',
      icon: <TrendUp className="w-5 h-5" />,
      color: '#FFCC00',
      change: '+5.3%'
    }
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#141414] border border-white/10 p-3 rounded-md">
          <p className="text-xs text-[#A1A1AA]">{label}</p>
          <p className="text-sm font-mono text-white">{payload[0].value.toLocaleString()} streams</p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-[#FF3B30] border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="dashboard-page">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome back, {user?.artist_name || user?.name || 'Artist'}
          </h1>
          <p className="text-[#A1A1AA] mt-1">Here's how your music is performing</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <div 
              key={index}
              className="bg-[#141414] border border-white/10 p-5 rounded-md animate-fadeIn"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between mb-3">
                <div 
                  className="w-10 h-10 rounded-md flex items-center justify-center"
                  style={{ backgroundColor: `${stat.color}20`, color: stat.color }}
                >
                  {stat.icon}
                </div>
                {stat.change && (
                  <span className="text-xs text-[#22C55E] font-mono">{stat.change}</span>
                )}
              </div>
              <p className="text-2xl font-bold font-mono tracking-tight">{stat.value}</p>
              <p className="text-sm text-[#A1A1AA] mt-1">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Charts and Recent Releases */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Streams Chart */}
          <div className="lg:col-span-2 bg-[#141414] border border-white/10 p-6 rounded-md">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-medium">Streaming Activity</h2>
              <span className="text-xs text-[#A1A1AA]">Last 30 days</span>
            </div>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analytics?.daily_streams || []}>
                  <defs>
                    <linearGradient id="streamGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FF3B30" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#FF3B30" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fill: '#71717A', fontSize: 10 }}
                    tickFormatter={(value) => value.slice(5)}
                    axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  />
                  <YAxis 
                    tick={{ fill: '#71717A', fontSize: 10 }}
                    axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area 
                    type="monotone" 
                    dataKey="streams" 
                    stroke="#FF3B30" 
                    strokeWidth={2}
                    fill="url(#streamGradient)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Releases */}
          <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-medium">Recent Releases</h2>
              <Link to="/releases" className="text-xs text-[#FF3B30] hover:underline">
                View all
              </Link>
            </div>
            
            {releases.length === 0 ? (
              <div className="text-center py-8">
                <Disc className="w-12 h-12 text-[#71717A] mx-auto mb-3" />
                <p className="text-sm text-[#A1A1AA] mb-4">No releases yet</p>
                <Link to="/releases/new">
                  <Button size="sm" className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white">
                    <Plus className="w-4 h-4 mr-2" /> Create Release
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {releases.map((release, index) => (
                  <Link 
                    key={release.id}
                    to={`/releases/${release.id}`}
                    className="flex items-center gap-3 p-3 rounded-md hover:bg-white/5 transition-colors"
                  >
                    <div className="w-10 h-10 bg-[#1E1E1E] rounded flex items-center justify-center">
                      <Disc className="w-5 h-5 text-[#A1A1AA]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{release.title}</p>
                      <p className="text-xs text-[#71717A] capitalize">{release.release_type}</p>
                    </div>
                    <span className={`text-xs capitalize px-2 py-1 rounded ${
                      release.status === 'distributed' ? 'bg-[#22C55E]/10 text-[#22C55E]' :
                      release.status === 'processing' ? 'bg-[#FFCC00]/10 text-[#FFCC00]' :
                      'bg-[#71717A]/10 text-[#71717A]'
                    }`}>
                      {release.status}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/releases/new" className="group bg-[#141414] border border-white/10 p-6 rounded-md hover:border-[#FF3B30]/50 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium mb-1">Create New Release</h3>
                <p className="text-sm text-[#A1A1AA]">Upload and distribute your music</p>
              </div>
              <ArrowRight className="w-5 h-5 text-[#71717A] group-hover:text-[#FF3B30] transition-colors" />
            </div>
          </Link>
          
          <Link to="/analytics" className="group bg-[#141414] border border-white/10 p-6 rounded-md hover:border-[#007AFF]/50 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium mb-1">View Analytics</h3>
                <p className="text-sm text-[#A1A1AA]">Track your streaming stats</p>
              </div>
              <ArrowRight className="w-5 h-5 text-[#71717A] group-hover:text-[#007AFF] transition-colors" />
            </div>
          </Link>
          
          <Link to="/wallet" className="group bg-[#141414] border border-white/10 p-6 rounded-md hover:border-[#22C55E]/50 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium mb-1">Manage Wallet</h3>
                <p className="text-sm text-[#A1A1AA]">Withdraw your earnings</p>
              </div>
              <ArrowRight className="w-5 h-5 text-[#71717A] group-hover:text-[#22C55E] transition-colors" />
            </div>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
