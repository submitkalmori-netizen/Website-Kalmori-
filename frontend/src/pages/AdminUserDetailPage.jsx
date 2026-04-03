import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { API, BACKEND_URL } from '../App';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { ArrowLeft, User, Disc, ChartLineUp, CurrencyDollar, Globe, Target, Users as UsersIcon, MusicNotes, PencilSimple, X, CheckCircle, SpotifyLogo, AppleLogo, InstagramLogo, TwitterLogo, ArrowSquareOut, FloppyDisk } from '@phosphor-icons/react';
import { toast } from 'sonner';

const StatCard = ({ label, value, icon, color, testId }) => (
  <div className="bg-[#141414] border border-white/10 rounded-xl p-4" data-testid={testId}>
    <div className="flex items-center gap-3 mb-2">
      <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15`, color }}>{icon}</div>
    </div>
    <p className="text-xl font-bold font-mono text-white">{value}</p>
    <p className="text-xs text-gray-500 mt-0.5">{label}</p>
  </div>
);

const fmt = (n) => {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
};

const AdminUserDetailPage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => { fetchDetail(); }, [userId]);

  const fetchDetail = async () => {
    try {
      const res = await axios.get(`${API}/admin/users/${userId}/detail`);
      setData(res.data);
      setEditForm({
        name: res.data.user.name || '',
        artist_name: res.data.user.artist_name || '',
        bio: res.data.user.bio || '',
        genre: res.data.user.genre || '',
        country: res.data.user.country || '',
        website: res.data.user.website || '',
        spotify_url: res.data.user.spotify_url || '',
        apple_music_url: res.data.user.apple_music_url || '',
        instagram: res.data.user.instagram || '',
        twitter: res.data.user.twitter || '',
        role: res.data.user.role || 'artist',
        plan: res.data.user.plan || 'free',
        status: res.data.user.status || 'active',
      });
    } catch { toast.error('Failed to load user'); navigate('/admin/users'); }
    finally { setLoading(false); }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/admin/users/${userId}/profile`, editForm);
      toast.success('Profile updated!');
      setEditing(false);
      fetchDetail();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed');
    } finally { setSaving(false); }
  };

  if (loading) return <AdminLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" /></div></AdminLayout>;
  if (!data) return null;

  const { user, stats, releases, platform_breakdown, country_breakdown, weekly_trends, goals } = data;
  const statusColor = (s) => s === 'distributed' ? 'text-[#1DB954]' : s === 'pending_review' ? 'text-[#FFD700]' : s === 'rejected' ? 'text-[#E53935]' : 'text-gray-400';
  const planColors = { pro: '#E040FB', rise: '#FFD700', free: '#666', single: '#7C4DFF', album: '#FF6B6B' };

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="admin-user-detail">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/admin/users')} className="p-2 hover:bg-white/5 rounded-lg" data-testid="back-to-users-btn">
            <ArrowLeft className="w-5 h-5 text-gray-400" />
          </button>
          <div className="flex items-center gap-4 flex-1">
            {user.avatar_url ? (
              <img src={`${BACKEND_URL}/api/files/${user.avatar_url}`} alt="" className="w-14 h-14 rounded-full border-2 border-white/10 object-cover" />
            ) : (
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center text-xl font-bold text-white">
                {user.artist_name?.charAt(0).toUpperCase() || 'A'}
              </div>
            )}
            <div>
              <h1 className="text-xl font-bold text-white flex items-center gap-3" data-testid="user-detail-name">
                {user.artist_name || user.name}
                <span className="text-xs px-2 py-0.5 rounded-full capitalize" style={{ backgroundColor: `${planColors[user.plan] || '#666'}20`, color: planColors[user.plan] || '#666' }}>{user.plan}</span>
                <span className={`text-xs capitalize ${user.role === 'admin' ? 'text-[#E53935]' : 'text-gray-500'}`}>{user.role}</span>
              </h1>
              <p className="text-sm text-gray-500">{user.email} &middot; Joined {new Date(user.created_at).toLocaleDateString()}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {user.slug && (
              <a href={`/artist/${user.slug}`} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-xs text-gray-400 hover:bg-white/10 transition-all"
                data-testid="view-public-profile-link">
                <ArrowSquareOut className="w-3.5 h-3.5" /> Public Profile
              </a>
            )}
            <Button onClick={() => setEditing(!editing)} className="bg-[#7C4DFF] hover:bg-[#7C4DFF]/80 text-white text-xs" data-testid="edit-profile-btn">
              <PencilSimple className="w-4 h-4 mr-1.5" /> {editing ? 'Cancel' : 'Edit Profile'}
            </Button>
          </div>
        </div>

        {/* Edit Form */}
        {editing && (
          <div className="bg-[#141414] border border-[#7C4DFF]/30 rounded-xl p-6 space-y-5" data-testid="admin-edit-profile-form">
            <h2 className="text-sm font-bold text-[#7C4DFF] uppercase tracking-wider">Edit Profile</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { key: 'name', label: 'Legal Name' },
                { key: 'artist_name', label: 'Artist / Stage Name' },
                { key: 'genre', label: 'Genre' },
                { key: 'country', label: 'Country' },
                { key: 'website', label: 'Website' },
                { key: 'spotify_url', label: 'Spotify URL' },
                { key: 'apple_music_url', label: 'Apple Music URL' },
                { key: 'instagram', label: 'Instagram' },
                { key: 'twitter', label: 'Twitter / X' },
              ].map(f => (
                <div key={f.key}>
                  <label className="block text-xs text-gray-500 mb-1">{f.label}</label>
                  <input value={editForm[f.key] || ''} onChange={(e) => setEditForm({ ...editForm, [f.key]: e.target.value })}
                    className="w-full bg-[#0A0A0A] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#7C4DFF]"
                    data-testid={`edit-field-${f.key}`} />
                </div>
              ))}
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Bio</label>
              <textarea value={editForm.bio || ''} onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                rows={3} className="w-full bg-[#0A0A0A] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#7C4DFF] resize-none"
                data-testid="edit-field-bio" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Role</label>
                <select value={editForm.role} onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                  className="w-full bg-[#0A0A0A] border border-white/10 rounded-lg px-3 py-2 text-sm text-white" data-testid="edit-field-role">
                  <option value="artist">Artist</option>
                  <option value="producer">Producer</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Plan</label>
                <select value={editForm.plan} onChange={(e) => setEditForm({ ...editForm, plan: e.target.value })}
                  className="w-full bg-[#0A0A0A] border border-white/10 rounded-lg px-3 py-2 text-sm text-white" data-testid="edit-field-plan">
                  <option value="free">Free</option>
                  <option value="single">Single</option>
                  <option value="album">Album</option>
                  <option value="rise">Rise</option>
                  <option value="pro">Pro</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Status</label>
                <select value={editForm.status} onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                  className="w-full bg-[#0A0A0A] border border-white/10 rounded-lg px-3 py-2 text-sm text-white" data-testid="edit-field-status">
                  <option value="active">Active</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <Button onClick={() => setEditing(false)} variant="outline" className="border-white/10 text-gray-400">Cancel</Button>
              <Button onClick={handleSave} disabled={saving} className="bg-[#E53935] hover:bg-[#d32f2f] text-white" data-testid="save-profile-btn">
                <FloppyDisk className="w-4 h-4 mr-1.5" /> {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <StatCard label="Total Streams" value={fmt(stats.total_streams)} icon={<ChartLineUp className="w-4 h-4" />} color="#7C4DFF" testId="stat-streams" />
          <StatCard label="Revenue" value={`$${stats.total_revenue.toFixed(2)}`} icon={<CurrencyDollar className="w-4 h-4" />} color="#1DB954" testId="stat-revenue" />
          <StatCard label="Releases" value={stats.total_releases} icon={<Disc className="w-4 h-4" />} color="#E040FB" testId="stat-releases" />
          <StatCard label="Pre-Saves" value={fmt(stats.presave_subscribers)} icon={<UsersIcon className="w-4 h-4" />} color="#FFD700" testId="stat-presaves" />
          <StatCard label="Goals" value={`${stats.goals_completed}/${stats.goals_active + stats.goals_completed}`} icon={<Target className="w-4 h-4" />} color="#FF6B6B" testId="stat-goals" />
        </div>

        {/* Analytics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Platform Breakdown */}
          <div className="bg-[#141414] border border-white/10 rounded-xl p-5" data-testid="platform-breakdown">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <MusicNotes className="w-4 h-4 text-[#7C4DFF]" /> Platform Breakdown
            </h3>
            {platform_breakdown.length === 0 ? (
              <p className="text-gray-500 text-sm py-4 text-center">No streaming data yet</p>
            ) : (
              <div className="space-y-3">
                {platform_breakdown.map((p, i) => {
                  const maxStreams = platform_breakdown[0]?.streams || 1;
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-xs text-gray-400 w-24 truncate">{p.platform}</span>
                      <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-[#7C4DFF] rounded-full" style={{ width: `${(p.streams / maxStreams) * 100}%` }} />
                      </div>
                      <span className="text-xs text-white font-mono w-16 text-right">{fmt(p.streams)}</span>
                      <span className="text-xs text-gray-500 w-16 text-right">${p.revenue.toFixed(2)}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Country Breakdown */}
          <div className="bg-[#141414] border border-white/10 rounded-xl p-5" data-testid="country-breakdown">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <Globe className="w-4 h-4 text-[#E040FB]" /> Top Markets
            </h3>
            {country_breakdown.length === 0 ? (
              <p className="text-gray-500 text-sm py-4 text-center">No geographic data yet</p>
            ) : (
              <div className="space-y-3">
                {country_breakdown.map((c, i) => {
                  const maxStreams = country_breakdown[0]?.streams || 1;
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-xs text-gray-400 w-24 truncate">{c.country}</span>
                      <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-[#E040FB] rounded-full" style={{ width: `${(c.streams / maxStreams) * 100}%` }} />
                      </div>
                      <span className="text-xs text-white font-mono w-16 text-right">{fmt(c.streams)}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Weekly Trend (mini sparkline bars) */}
        {weekly_trends.some(w => w.streams > 0) && (
          <div className="bg-[#141414] border border-white/10 rounded-xl p-5" data-testid="weekly-trends">
            <h3 className="text-sm font-bold text-white mb-4">Weekly Stream Trend</h3>
            <div className="flex items-end gap-2 h-24">
              {weekly_trends.map((w, i) => {
                const maxW = Math.max(...weekly_trends.map(t => t.streams), 1);
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-1">
                    <div className="w-full bg-[#7C4DFF]/20 rounded-t relative" style={{ height: `${Math.max((w.streams / maxW) * 80, 4)}px` }}>
                      <div className="absolute inset-0 bg-[#7C4DFF] rounded-t" style={{ height: '100%' }} />
                    </div>
                    <span className="text-[9px] text-gray-500">{w.week}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Releases Table */}
        <div className="bg-[#141414] border border-white/10 rounded-xl overflow-hidden" data-testid="releases-table">
          <div className="p-5 border-b border-white/10">
            <h3 className="text-sm font-bold text-white">Releases ({releases.length})</h3>
          </div>
          {releases.length === 0 ? (
            <p className="text-gray-500 text-sm py-8 text-center">No releases yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5 bg-white/5">
                    <th className="text-left py-2.5 px-4 text-xs text-gray-500 font-medium">Title</th>
                    <th className="text-left py-2.5 px-4 text-xs text-gray-500 font-medium">Type</th>
                    <th className="text-left py-2.5 px-4 text-xs text-gray-500 font-medium">Genre</th>
                    <th className="text-left py-2.5 px-4 text-xs text-gray-500 font-medium">Status</th>
                    <th className="text-left py-2.5 px-4 text-xs text-gray-500 font-medium">Tracks</th>
                    <th className="text-left py-2.5 px-4 text-xs text-gray-500 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {releases.map(r => (
                    <tr key={r.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-2.5 px-4 text-sm font-medium text-white">{r.title}</td>
                      <td className="py-2.5 px-4 text-xs text-gray-400 capitalize">{r.release_type}</td>
                      <td className="py-2.5 px-4 text-xs text-gray-400">{r.genre || '-'}</td>
                      <td className="py-2.5 px-4"><span className={`text-xs capitalize ${statusColor(r.status)}`}>{r.status?.replace('_', ' ')}</span></td>
                      <td className="py-2.5 px-4 text-xs text-gray-400 font-mono">{r.track_count || 0}</td>
                      <td className="py-2.5 px-4 text-xs text-gray-500">{r.created_at ? new Date(r.created_at).toLocaleDateString() : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Goals */}
        {goals.length > 0 && (
          <div className="bg-[#141414] border border-white/10 rounded-xl p-5" data-testid="user-goals">
            <h3 className="text-sm font-bold text-white mb-4">Goals & Milestones</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {goals.map(g => {
                const pct = Math.min(((g.current_value || 0) / (g.target_value || 1)) * 100, 100);
                const isComplete = g.status === 'completed';
                return (
                  <div key={g.id} className={`p-4 rounded-lg border ${isComplete ? 'border-[#FFD700]/30 bg-[#FFD700]/5' : 'border-white/10 bg-white/5'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium text-white truncate">{g.title || g.type}</p>
                      {isComplete && <CheckCircle className="w-4 h-4 text-[#FFD700]" weight="fill" />}
                    </div>
                    <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden mb-1.5">
                      <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: isComplete ? '#FFD700' : '#7C4DFF' }} />
                    </div>
                    <p className="text-[10px] text-gray-500">{fmt(g.current_value || 0)} / {fmt(g.target_value)} &middot; {pct.toFixed(0)}%</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminUserDetailPage;
