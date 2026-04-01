import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API, useAuth } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Disc, Play, CurrencyDollar, TrendUp, Plus, ArrowRight } from '@phosphor-icons/react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const DashboardPage = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [releases, setReleases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, releasesRes] = await Promise.all([axios.get(`${API}/analytics/overview`), axios.get(`${API}/releases`)]);
        setAnalytics(analyticsRes.data);
        setReleases(releasesRes.data.slice(0, 5));
      } catch (error) { console.error('Failed to fetch:', error); }
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  const stats = [
    { label: 'Total Streams', value: analytics?.total_streams?.toLocaleString() || '0', icon: <Play className="w-5 h-5" />, color: '#7C4DFF', change: '+12.5%' },
    { label: 'Total Earnings', value: `$${analytics?.total_earnings?.toFixed(2) || '0.00'}`, icon: <CurrencyDollar className="w-5 h-5" />, color: '#4CAF50', change: '+8.2%' },
    { label: 'Releases', value: analytics?.release_count || '0', icon: <Disc className="w-5 h-5" />, color: '#E040FB', change: null },
    { label: 'Downloads', value: analytics?.total_downloads?.toLocaleString() || '0', icon: <TrendUp className="w-5 h-5" />, color: '#FFD700', change: '+5.3%' }
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return <div className="bg-[#111] border border-white/10 p-3 rounded-lg"><p className="text-xs text-gray-400">{label}</p><p className="text-sm font-mono text-white">{payload[0].value.toLocaleString()} streams</p></div>;
    }
    return null;
  };

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="dashboard-page">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Welcome back, <span className="gradient-text">{user?.artist_name || user?.name || 'Artist'}</span></h1>
          <p className="text-gray-400 mt-1">Here's how your music is performing</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, i) => (
            <div key={i} className="card-kalmori p-5 animate-fadeInUp" style={{ animationDelay: `${i * 0.1}s` }}>
              <div className="flex items-center justify-between mb-3">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${stat.color}20`, color: stat.color }}>{stat.icon}</div>
                {stat.change && <span className="text-xs text-[#4CAF50] font-mono">{stat.change}</span>}
              </div>
              <p className="text-2xl font-bold font-mono">{stat.value}</p>
              <p className="text-sm text-gray-400 mt-1">{stat.label}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 card-kalmori p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-medium">Streaming Activity</h2>
              <span className="text-xs text-gray-500">Last 30 days</span>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analytics?.daily_streams || []}>
                  <defs><linearGradient id="streamGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#7C4DFF" stopOpacity={0.4}/><stop offset="95%" stopColor="#7C4DFF" stopOpacity={0}/></linearGradient></defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" tick={{ fill: '#666', fontSize: 10 }} tickFormatter={(v) => v.slice(5)} axisLine={{ stroke: 'rgba(255,255,255,0.1)' }} />
                  <YAxis tick={{ fill: '#666', fontSize: 10 }} axisLine={{ stroke: 'rgba(255,255,255,0.1)' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="streams" stroke="#7C4DFF" strokeWidth={2} fill="url(#streamGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card-kalmori p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-medium">Recent Releases</h2>
              <Link to="/releases" className="text-xs text-[#7C4DFF] hover:underline">View all</Link>
            </div>
            {releases.length === 0 ? (
              <div className="text-center py-8">
                <Disc className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <p className="text-sm text-gray-400 mb-4">No releases yet</p>
                <Link to="/releases/new"><button className="btn-red px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 mx-auto"><Plus className="w-4 h-4" /> Create Release</button></Link>
              </div>
            ) : (
              <div className="space-y-3">
                {releases.map((release) => (
                  <Link key={release.id} to={`/releases/${release.id}`} className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors">
                    <div className="w-10 h-10 bg-[#1a1a1a] rounded-lg flex items-center justify-center"><Disc className="w-5 h-5 text-gray-500" /></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{release.title}</p>
                      <p className="text-xs text-gray-500 capitalize">{release.release_type}</p>
                    </div>
                    <span className={`text-xs capitalize px-2 py-1 rounded ${release.status === 'distributed' ? 'bg-[#4CAF50]/10 text-[#4CAF50]' : release.status === 'processing' ? 'bg-[#FFD700]/10 text-[#FFD700]' : 'bg-gray-600/20 text-gray-400'}`}>{release.status}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/releases/new" className="group card-kalmori p-6 hover:border-[#7C4DFF]/50">
            <div className="flex items-center justify-between">
              <div><h3 className="font-medium mb-1">Create New Release</h3><p className="text-sm text-gray-400">Upload and distribute your music</p></div>
              <ArrowRight className="w-5 h-5 text-gray-600 group-hover:text-[#7C4DFF] transition-colors" />
            </div>
          </Link>
          <Link to="/analytics" className="group card-kalmori p-6 hover:border-[#E040FB]/50">
            <div className="flex items-center justify-between">
              <div><h3 className="font-medium mb-1">View Analytics</h3><p className="text-sm text-gray-400">Track your streaming stats</p></div>
              <ArrowRight className="w-5 h-5 text-gray-600 group-hover:text-[#E040FB] transition-colors" />
            </div>
          </Link>
          <Link to="/wallet" className="group card-kalmori p-6 hover:border-[#4CAF50]/50">
            <div className="flex items-center justify-between">
              <div><h3 className="font-medium mb-1">Manage Wallet</h3><p className="text-sm text-gray-400">Withdraw your earnings</p></div>
              <ArrowRight className="w-5 h-5 text-gray-600 group-hover:text-[#4CAF50] transition-colors" />
            </div>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
