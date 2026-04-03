import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API, BACKEND_URL, useAuth } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { Users, ChartLineUp, CurrencyDollar, Disc, MusicNotes, Globe, Plus, X, Trash, ArrowSquareOut, Lightning, Envelope } from '@phosphor-icons/react';
import { toast } from 'sonner';

const fmt = (n) => {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n?.toLocaleString?.() || '0';
};

const StatCard = ({ label, value, icon, color, testId }) => (
  <div className="bg-[#141414] border border-white/10 rounded-xl p-5" data-testid={testId}>
    <div className="flex items-center gap-3 mb-3">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}15`, color }}>{icon}</div>
    </div>
    <p className="text-2xl font-bold font-mono text-white">{value}</p>
    <p className="text-xs text-gray-500 mt-1">{label}</p>
  </div>
);

const LabelDashboardPage = () => {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviting, setInviting] = useState(false);

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      const [dashRes, artistsRes] = await Promise.all([
        axios.get(`${API}/label/dashboard`, { withCredentials: true }),
        axios.get(`${API}/label/artists`, { withCredentials: true }),
      ]);
      setDashboard(dashRes.data);
      setArtists(artistsRes.data.artists || []);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleInvite = async () => {
    if (!inviteEmail.trim()) return;
    setInviting(true);
    try {
      const res = await axios.post(`${API}/label/artists/invite`, { email: inviteEmail }, { withCredentials: true });
      toast.success(res.data.message);
      setInviteEmail('');
      setShowInvite(false);
      fetchAll();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add artist');
    } finally { setInviting(false); }
  };

  const handleRemove = async (artistId, name) => {
    if (!window.confirm(`Remove ${name} from your roster?`)) return;
    try {
      await axios.delete(`${API}/label/artists/${artistId}`, { withCredentials: true });
      toast.success(`${name} removed`);
      fetchAll();
    } catch { toast.error('Failed to remove artist'); }
  };

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#FFD700] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  const d = dashboard || {};
  const statusColor = (s) => s === 'distributed' ? 'text-[#1DB954]' : s === 'pending_review' ? 'text-[#FFD700]' : s === 'rejected' ? 'text-[#E53935]' : 'text-gray-400';

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="label-dashboard">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white">Label <span className="text-[#FFD700]">Dashboard</span></h1>
            <p className="text-gray-400 text-sm mt-1">Manage your roster, track collective performance</p>
          </div>
          <Button onClick={() => setShowInvite(!showInvite)} className="bg-[#FFD700] hover:bg-[#FFC107] text-black font-bold" data-testid="add-artist-btn">
            <Plus className="w-4 h-4 mr-2" /> Add Artist
          </Button>
        </div>

        {/* Invite Modal */}
        {showInvite && (
          <div className="bg-[#141414] border border-[#FFD700]/30 rounded-xl p-6" data-testid="invite-artist-form">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-[#FFD700]">Add Artist to Roster</h3>
              <button onClick={() => setShowInvite(false)} className="text-gray-500 hover:text-white"><X className="w-4 h-4" /></button>
            </div>
            <p className="text-xs text-gray-400 mb-4">Enter the email of an existing Kalmori user to add them to your label roster.</p>
            <div className="flex gap-3">
              <div className="flex-1 flex items-center bg-[#0A0A0A] border border-white/10 rounded-lg overflow-hidden">
                <Envelope className="w-4 h-4 text-gray-500 ml-3 flex-shrink-0" />
                <input type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="artist@email.com" className="flex-1 bg-transparent px-3 py-2.5 text-sm text-white outline-none"
                  onKeyDown={(e) => e.key === 'Enter' && handleInvite()} data-testid="invite-email-input" />
              </div>
              <Button onClick={handleInvite} disabled={inviting} className="bg-[#FFD700] hover:bg-[#FFC107] text-black font-bold px-6" data-testid="send-invite-btn">
                {inviting ? 'Adding...' : 'Add'}
              </Button>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <StatCard label="Artists" value={d.total_artists || 0} icon={<Users className="w-5 h-5" />} color="#FFD700" testId="label-stat-artists" />
          <StatCard label="Total Streams" value={fmt(d.total_streams || 0)} icon={<ChartLineUp className="w-5 h-5" />} color="#7C4DFF" testId="label-stat-streams" />
          <StatCard label="Revenue" value={`$${(d.total_revenue || 0).toFixed(2)}`} icon={<CurrencyDollar className="w-5 h-5" />} color="#1DB954" testId="label-stat-revenue" />
          <StatCard label="Releases" value={d.total_releases || 0} icon={<Disc className="w-5 h-5" />} color="#E040FB" testId="label-stat-releases" />
          <StatCard label="This Week" value={fmt(d.week_streams || 0)} icon={<Lightning className="w-5 h-5" />} color="#FF6B6B" testId="label-stat-week" />
        </div>

        {/* Analytics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Platform Breakdown */}
          <div className="bg-[#141414] border border-white/10 rounded-xl p-5" data-testid="label-platform-breakdown">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <MusicNotes className="w-4 h-4 text-[#7C4DFF]" /> Platform Streams
            </h3>
            {d.platform_breakdown?.length > 0 ? (
              <div className="space-y-3">
                {d.platform_breakdown.map((p, i) => {
                  const max = d.platform_breakdown[0]?.streams || 1;
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
            ) : <p className="text-gray-500 text-sm text-center py-4">Add artists to see data</p>}
          </div>

          {/* Country Breakdown */}
          <div className="bg-[#141414] border border-white/10 rounded-xl p-5" data-testid="label-country-breakdown">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <Globe className="w-4 h-4 text-[#E040FB]" /> Top Markets
            </h3>
            {d.country_breakdown?.length > 0 ? (
              <div className="space-y-3">
                {d.country_breakdown.map((c, i) => {
                  const max = d.country_breakdown[0]?.streams || 1;
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
            ) : <p className="text-gray-500 text-sm text-center py-4">Add artists to see data</p>}
          </div>

          {/* Top Artists (from roster) */}
          <div className="bg-[#141414] border border-white/10 rounded-xl p-5" data-testid="label-top-artists">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <ChartLineUp className="w-4 h-4 text-[#FFD700]" /> Top Performers
            </h3>
            {d.top_artists?.length > 0 ? (
              <div className="space-y-3">
                {d.top_artists.map((a, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-xs text-gray-500 w-4 font-mono">{i + 1}</span>
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#FFD700] to-[#FF6B6B] flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0">
                      {a.artist_name?.charAt(0).toUpperCase() || 'A'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-white truncate">{a.artist_name || a.name}</p>
                      <p className="text-[10px] text-gray-500">{a.releases} releases</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] text-[#7C4DFF] font-mono">{fmt(a.streams)}</p>
                      <p className="text-[10px] text-[#1DB954]">${a.revenue.toFixed(2)}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : <p className="text-gray-500 text-sm text-center py-4">Add artists to see data</p>}
          </div>
        </div>

        {/* Artist Roster Table */}
        <div className="bg-[#141414] border border-white/10 rounded-xl overflow-hidden" data-testid="label-artist-roster">
          <div className="p-5 border-b border-white/10 flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Artist Roster ({artists.length})</h2>
          </div>
          {artists.length === 0 ? (
            <div className="p-10 text-center">
              <Users className="w-12 h-12 text-white/10 mx-auto mb-4" />
              <p className="text-gray-400 text-sm mb-2">Your roster is empty</p>
              <p className="text-gray-500 text-xs mb-4">Add artists by their email to start managing their releases and tracking analytics.</p>
              <Button onClick={() => setShowInvite(true)} className="bg-[#FFD700] hover:bg-[#FFC107] text-black font-bold text-xs" data-testid="empty-add-artist-btn">
                <Plus className="w-4 h-4 mr-1" /> Add Your First Artist
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5 bg-white/5">
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Artist</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Plan</th>
                    <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Streams</th>
                    <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Revenue</th>
                    <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Releases</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Added</th>
                    <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {artists.map((a) => (
                    <tr key={a.id} className="border-b border-white/5 hover:bg-white/5 transition-colors" data-testid={`roster-artist-${a.id}`}>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          {a.avatar_url ? (
                            <img src={`${BACKEND_URL}/api/files/${a.avatar_url}`} alt="" className="w-8 h-8 rounded-full object-cover" />
                          ) : (
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                              {a.artist_name?.charAt(0).toUpperCase() || 'A'}
                            </div>
                          )}
                          <div>
                            <p className="text-sm font-medium text-white">{a.artist_name || a.name}</p>
                            <p className="text-[10px] text-gray-500">{a.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-xs capitalize px-2 py-0.5 rounded-full" style={{
                          backgroundColor: a.plan === 'pro' ? '#E040FB20' : a.plan === 'rise' ? '#FFD70020' : '#66666620',
                          color: a.plan === 'pro' ? '#E040FB' : a.plan === 'rise' ? '#FFD700' : '#666'
                        }}>{a.plan}</span>
                      </td>
                      <td className="py-3 px-4 text-right text-sm font-mono text-[#7C4DFF]">{fmt(a.streams)}</td>
                      <td className="py-3 px-4 text-right text-sm font-mono text-[#1DB954]">${a.revenue.toFixed(2)}</td>
                      <td className="py-3 px-4 text-right text-sm font-mono text-gray-300">{a.releases}</td>
                      <td className="py-3 px-4 text-xs text-gray-500">{a.added_at ? new Date(a.added_at).toLocaleDateString() : '-'}</td>
                      <td className="py-3 px-4 text-right">
                        <button onClick={() => handleRemove(a.id, a.artist_name || a.name)}
                          className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
                          data-testid={`remove-artist-${a.id}`}>
                          <Trash className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Recent Releases Across Roster */}
        {d.recent_releases?.length > 0 && (
          <div className="bg-[#141414] border border-white/10 rounded-xl overflow-hidden" data-testid="label-recent-releases">
            <div className="p-5 border-b border-white/10">
              <h2 className="text-base font-bold text-white">Recent Releases</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5 bg-white/5">
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Release</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Artist</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Type</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Status</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {d.recent_releases.map((r) => (
                    <tr key={r.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-3 px-4 text-sm font-medium text-white">{r.title}</td>
                      <td className="py-3 px-4 text-sm text-gray-400">{r.artist_name}</td>
                      <td className="py-3 px-4 text-xs text-gray-400 capitalize">{r.release_type}</td>
                      <td className="py-3 px-4"><span className={`text-xs capitalize ${statusColor(r.status)}`}>{r.status?.replace('_', ' ')}</span></td>
                      <td className="py-3 px-4 text-xs text-gray-500">{r.created_at ? new Date(r.created_at).toLocaleDateString() : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default LabelDashboardPage;
