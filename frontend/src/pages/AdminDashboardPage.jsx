import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API, useAuth } from '../App';
import AdminLayout from '../components/AdminLayout';
import { Users, Disc, ClipboardText, CurrencyDollar, TrendUp, Clock, CheckCircle, XCircle, ChartLineUp, Globe, MusicNotes, Lightning } from '@phosphor-icons/react';
import { Link } from 'react-router-dom';

const fmt = (n) => {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n?.toLocaleString?.() || '0';
};

const AdminDashboardPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recentSubs, setRecentSubs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashRes, subsRes, analyticsRes] = await Promise.all([
          axios.get(`${API}/admin/dashboard`),
          axios.get(`${API}/admin/submissions?limit=5`),
          axios.get(`${API}/admin/analytics`),
        ]);
        setStats(dashRes.data);
        setRecentSubs(subsRes.data.submissions);
        setAnalytics(analyticsRes.data);
      } catch (err) { console.error('Admin fetch failed:', err); }
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  if (loading) return <AdminLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" /></div></AdminLayout>;

  const cards = [
    { label: 'Total Users', value: stats?.total_users || 0, icon: <Users className="w-5 h-5" />, color: '#7C4DFF' },
    { label: 'Total Releases', value: stats?.total_releases || 0, icon: <Disc className="w-5 h-5" />, color: '#E040FB' },
    { label: 'Pending Review', value: stats?.pending_submissions || 0, icon: <Clock className="w-5 h-5" />, color: '#FFD700' },
    { label: 'Platform Revenue', value: `$${stats?.total_revenue?.toFixed(2) || '0.00'}`, icon: <CurrencyDollar className="w-5 h-5" />, color: '#4CAF50' },
    { label: 'Total Streams', value: fmt(analytics?.total_streams || 0), icon: <ChartLineUp className="w-5 h-5" />, color: '#1DB954' },
    { label: 'This Week Streams', value: fmt(analytics?.week_streams || 0), icon: <Lightning className="w-5 h-5" />, color: '#FF6B6B' },
  ];

  const statusColor = (s) => {
    if (s === 'pending_review') return 'bg-[#FFD700]/10 text-[#FFD700]';
    if (s === 'approved') return 'bg-[#4CAF50]/10 text-[#4CAF50]';
    if (s === 'rejected') return 'bg-[#E53935]/10 text-[#E53935]';
    return 'bg-gray-600/20 text-gray-400';
  };

  return (
    <AdminLayout>
      <div className="space-y-8" data-testid="admin-dashboard">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Admin <span className="text-[#E53935]">Dashboard</span></h1>
          <p className="text-gray-400 mt-1">Platform overview, analytics, and management</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {cards.map((card, i) => (
            <div key={i} className="card-kalmori p-5 animate-fadeInUp" style={{ animationDelay: `${i * 0.05}s` }} data-testid={`admin-stat-${card.label.toLowerCase().replace(/\s/g, '-')}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${card.color}20`, color: card.color }}>{card.icon}</div>
              </div>
              <p className="text-2xl font-bold font-mono">{card.value}</p>
              <p className="text-sm text-gray-400 mt-1">{card.label}</p>
            </div>
          ))}
        </div>

        {/* Platform Analytics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Platform Breakdown */}
          <div className="card-kalmori p-6" data-testid="admin-platform-breakdown">
            <h2 className="text-sm font-bold mb-4 flex items-center gap-2">
              <MusicNotes className="w-4 h-4 text-[#7C4DFF]" /> Platform Streams
            </h2>
            {analytics?.platform_breakdown?.length > 0 ? (
              <div className="space-y-3">
                {analytics.platform_breakdown.slice(0, 8).map((p, i) => {
                  const max = analytics.platform_breakdown[0]?.streams || 1;
                  return (
                    <div key={i} className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 w-20 truncate">{p.platform}</span>
                      <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] rounded-full" style={{ width: `${(p.streams / max) * 100}%` }} />
                      </div>
                      <span className="text-[10px] text-white font-mono w-12 text-right">{fmt(p.streams)}</span>
                    </div>
                  );
                })}
              </div>
            ) : <p className="text-gray-500 text-sm text-center py-4">No data yet</p>}
          </div>

          {/* Country Breakdown */}
          <div className="card-kalmori p-6" data-testid="admin-country-breakdown">
            <h2 className="text-sm font-bold mb-4 flex items-center gap-2">
              <Globe className="w-4 h-4 text-[#E040FB]" /> Top Markets
            </h2>
            {analytics?.country_breakdown?.length > 0 ? (
              <div className="space-y-3">
                {analytics.country_breakdown.slice(0, 8).map((c, i) => {
                  const max = analytics.country_breakdown[0]?.streams || 1;
                  return (
                    <div key={i} className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 w-20 truncate">{c.country}</span>
                      <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-[#E040FB] to-[#FF4081] rounded-full" style={{ width: `${(c.streams / max) * 100}%` }} />
                      </div>
                      <span className="text-[10px] text-white font-mono w-12 text-right">{fmt(c.streams)}</span>
                    </div>
                  );
                })}
              </div>
            ) : <p className="text-gray-500 text-sm text-center py-4">No data yet</p>}
          </div>

          {/* Top Artists */}
          <div className="card-kalmori p-6" data-testid="admin-top-artists">
            <h2 className="text-sm font-bold mb-4 flex items-center gap-2">
              <TrendUp className="w-4 h-4 text-[#FFD700]" /> Top Artists
            </h2>
            {analytics?.top_artists?.length > 0 ? (
              <div className="space-y-3">
                {analytics.top_artists.slice(0, 8).map((a, i) => (
                  <Link key={i} to={`/admin/users/${a.id}`} className="flex items-center gap-3 p-2 -mx-2 rounded-lg hover:bg-white/5 transition-colors" data-testid={`top-artist-${i}`}>
                    <span className="text-xs text-gray-500 w-4 font-mono">{i + 1}</span>
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0">
                      {a.artist_name?.charAt(0).toUpperCase() || 'A'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-white truncate">{a.artist_name || a.name}</p>
                    </div>
                    <span className="text-[10px] text-[#7C4DFF] font-mono">{fmt(a.streams)}</span>
                  </Link>
                ))}
              </div>
            ) : <p className="text-gray-500 text-sm text-center py-4">No data yet</p>}
          </div>
        </div>

        {/* Users & Activity Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Plan Distribution */}
          <div className="card-kalmori p-6">
            <h2 className="text-lg font-medium mb-4">Users by Plan</h2>
            <div className="space-y-3">
              {Object.entries(stats?.users_by_plan || {}).map(([plan, count]) => (
                <div key={plan} className="flex items-center justify-between">
                  <span className="text-sm capitalize text-gray-300">{plan}</span>
                  <div className="flex items-center gap-3">
                    <div className="w-32 h-2 bg-[#1a1a1a] rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${(count / (stats?.total_users || 1)) * 100}%`, backgroundColor: plan === 'pro' ? '#E040FB' : plan === 'rise' ? '#FFD700' : '#666' }} />
                    </div>
                    <span className="text-sm font-mono text-white">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Activity */}
          <div className="card-kalmori p-6">
            <h2 className="text-lg font-medium mb-4">This Week</h2>
            <div className="space-y-4">
              <div className="flex items-center gap-4 p-3 bg-white/5 rounded-lg">
                <TrendUp className="w-8 h-8 text-[#7C4DFF]" />
                <div>
                  <p className="text-2xl font-bold font-mono">{stats?.new_users_week || 0}</p>
                  <p className="text-xs text-gray-400">New users this week</p>
                </div>
              </div>
              <div className="flex items-center gap-4 p-3 bg-white/5 rounded-lg">
                <Disc className="w-8 h-8 text-[#E040FB]" />
                <div>
                  <p className="text-2xl font-bold font-mono">{stats?.new_releases_week || 0}</p>
                  <p className="text-xs text-gray-400">New releases this week</p>
                </div>
              </div>
              <div className="flex items-center gap-4 p-3 bg-white/5 rounded-lg">
                <Users className="w-8 h-8 text-[#1DB954]" />
                <div>
                  <p className="text-2xl font-bold font-mono">{analytics?.active_artists || 0}</p>
                  <p className="text-xs text-gray-400">Active artists (30 days)</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Monthly Stream Trend */}
        {analytics?.monthly_trend?.some(m => m.streams > 0) && (
          <div className="card-kalmori p-6" data-testid="admin-monthly-trend">
            <h2 className="text-lg font-medium mb-4">Monthly Streams (Platform-wide)</h2>
            <div className="flex items-end gap-3 h-32">
              {analytics.monthly_trend.map((m, i) => {
                const maxM = Math.max(...analytics.monthly_trend.map(t => t.streams), 1);
                const h = Math.max((m.streams / maxM) * 100, 8);
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-2">
                    <span className="text-[9px] text-white font-mono">{fmt(m.streams)}</span>
                    <div className="w-full rounded-t-lg bg-gradient-to-t from-[#7C4DFF] to-[#E040FB]" style={{ height: `${h}%` }} />
                    <span className="text-[9px] text-gray-500">{m.month}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Recent Submissions */}
        <div className="card-kalmori p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium">Recent Submissions</h2>
            <Link to="/admin/submissions" className="text-xs text-[#E53935] hover:underline">View all</Link>
          </div>
          {recentSubs.length === 0 ? (
            <p className="text-gray-500 text-sm py-4 text-center">No submissions yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-2 text-xs text-gray-500 font-medium">Release</th>
                    <th className="text-left py-3 px-2 text-xs text-gray-500 font-medium">Artist</th>
                    <th className="text-left py-3 px-2 text-xs text-gray-500 font-medium">Type</th>
                    <th className="text-left py-3 px-2 text-xs text-gray-500 font-medium">Status</th>
                    <th className="text-left py-3 px-2 text-xs text-gray-500 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentSubs.map((sub) => (
                    <tr key={sub.release_id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-3 px-2 text-sm">{sub.release_title}</td>
                      <td className="py-3 px-2 text-sm text-gray-400">{sub.artist_name}</td>
                      <td className="py-3 px-2 text-sm text-gray-400 capitalize">{sub.release_type}</td>
                      <td className="py-3 px-2"><span className={`text-xs px-2 py-1 rounded-full ${statusColor(sub.status)}`}>{sub.status.replace('_', ' ')}</span></td>
                      <td className="py-3 px-2 text-xs text-gray-500">{new Date(sub.submitted_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};

export default AdminDashboardPage;
