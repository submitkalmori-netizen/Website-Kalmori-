import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API, useAuth } from '../App';
import AdminLayout from '../components/AdminLayout';
import { Users, Disc, ClipboardText, CurrencyDollar, TrendUp, Clock, CheckCircle, XCircle } from '@phosphor-icons/react';
import { Link } from 'react-router-dom';

const AdminDashboardPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentSubs, setRecentSubs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashRes, subsRes] = await Promise.all([
          axios.get(`${API}/admin/dashboard`),
          axios.get(`${API}/admin/submissions?limit=5`)
        ]);
        setStats(dashRes.data);
        setRecentSubs(subsRes.data.submissions);
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
    { label: 'Revenue', value: `$${stats?.total_revenue?.toFixed(2) || '0.00'}`, icon: <CurrencyDollar className="w-5 h-5" />, color: '#4CAF50' },
    { label: 'Approved', value: stats?.approved_submissions || 0, icon: <CheckCircle className="w-5 h-5" />, color: '#4CAF50' },
    { label: 'Rejected', value: stats?.rejected_submissions || 0, icon: <XCircle className="w-5 h-5" />, color: '#E53935' },
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
          <p className="text-gray-400 mt-1">Platform overview and management</p>
        </div>

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
            </div>
          </div>
        </div>

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
