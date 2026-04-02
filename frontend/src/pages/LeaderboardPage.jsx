import React, { useEffect, useState, useMemo } from 'react';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Trophy, Fire, TrendUp, TrendDown, ArrowUp, ArrowDown, Equals, MusicNote, CurrencyDollar, ChartLineUp, SortAscending } from '@phosphor-icons/react';

const SORT_OPTIONS = [
  { key: 'total_streams', label: 'Total Streams' },
  { key: 'streams_this_week', label: 'This Week' },
  { key: 'growth_percent', label: 'Growth Rate' },
  { key: 'total_revenue', label: 'Revenue' },
  { key: 'momentum', label: 'Momentum' },
];

export default function LeaderboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('total_streams');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const res = await axios.get(`${API}/analytics/leaderboard`, { withCredentials: true });
      setData(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const sorted = useMemo(() => {
    if (!data) return [];
    let list = [...data.leaderboard];
    if (filterStatus !== 'all') list = list.filter(r => filterStatus === 'active' ? r.total_streams > 0 : r.total_streams === 0);
    list.sort((a, b) => b[sortBy] - a[sortBy]);
    return list.map((item, i) => ({ ...item, displayRank: i + 1 }));
  }, [data, sortBy, filterStatus]);

  if (loading) return (
    <DashboardLayout>
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-[#FFD700] border-t-transparent rounded-full animate-spin" />
      </div>
    </DashboardLayout>
  );

  if (!data) return <DashboardLayout><p className="text-gray-400">Failed to load leaderboard.</p></DashboardLayout>;

  const hotCount = data.leaderboard.filter(r => r.hot_streak).length;
  const topRelease = data.leaderboard[0];

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="leaderboard-page">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold flex items-center gap-3">
              <Trophy className="w-8 h-8 text-[#FFD700]" weight="fill" /> Release Leaderboard
            </h1>
            <p className="text-gray-400 mt-1">
              {data.active_releases} active / {data.total_releases} total releases
              {hotCount > 0 && <span className="text-orange-400 ml-2">{hotCount} on hot streaks</span>}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={filterStatus}
              onChange={e => setFilterStatus(e.target.value)}
              className="bg-[#111] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#7C4DFF]/50"
              data-testid="filter-status"
            >
              <option value="all">All Releases</option>
              <option value="active">Active Only</option>
              <option value="inactive">No Streams</option>
            </select>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              className="bg-[#111] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#7C4DFF]/50"
              data-testid="sort-select"
            >
              {SORT_OPTIONS.map(o => (
                <option key={o.key} value={o.key}>{o.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Top 3 Podium */}
        {sorted.length >= 3 && sortBy === 'total_streams' && filterStatus === 'all' && (
          <div className="grid grid-cols-3 gap-4" data-testid="podium">
            <PodiumCard release={sorted[1]} place={2} />
            <PodiumCard release={sorted[0]} place={1} featured />
            <PodiumCard release={sorted[2]} place={3} />
          </div>
        )}

        {/* Full Leaderboard */}
        <div className="space-y-2" data-testid="leaderboard-list">
          {sorted.map((release) => (
            <LeaderboardRow key={release.release_id} release={release} />
          ))}
          {sorted.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <MusicNote className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No releases match this filter</p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

function PodiumCard({ release, place, featured }) {
  const colors = { 1: '#FFD700', 2: '#C0C0C0', 3: '#CD7F32' };
  const color = colors[place];
  const r = release;

  return (
    <div
      className={`bg-[#111] border rounded-2xl p-5 text-center transition-transform hover:scale-[1.02] ${featured ? 'border-[#FFD700]/40 ring-1 ring-[#FFD700]/20 -mt-2 pb-7' : 'border-white/10 mt-2'}`}
      data-testid={`podium-${place}`}
    >
      <div className="w-10 h-10 rounded-full mx-auto mb-3 flex items-center justify-center text-lg font-black" style={{ backgroundColor: `${color}20`, color }}>
        {place}
      </div>
      <h3 className="text-sm font-bold text-white truncate mb-1">{r.title}</h3>
      {r.genre && <p className="text-[10px] text-gray-500 mb-2">{r.genre}</p>}
      <p className="text-xl font-bold font-mono" style={{ color }}>{r.total_streams.toLocaleString()}</p>
      <p className="text-[10px] text-gray-500">streams</p>
      {r.hot_streak && (
        <div className="mt-2 inline-flex items-center gap-1 bg-orange-500/10 text-orange-400 text-[10px] font-bold px-2 py-0.5 rounded-full">
          <Fire className="w-3 h-3" weight="fill" /> HOT STREAK
        </div>
      )}
      <div className="mt-3">
        <Sparkline data={r.sparkline} color={color} height={28} />
      </div>
    </div>
  );
}

function LeaderboardRow({ release }) {
  const r = release;
  const growthColor = r.growth_percent > 0 ? 'text-green-400' : r.growth_percent < 0 ? 'text-red-400' : 'text-gray-500';
  const GrowthIcon = r.growth_percent > 0 ? TrendUp : r.growth_percent < 0 ? TrendDown : Equals;
  const rankColor = r.displayRank <= 3 ? { 1: '#FFD700', 2: '#C0C0C0', 3: '#CD7F32' }[r.displayRank] : '#555';

  return (
    <div className="bg-[#111] border border-white/10 rounded-xl p-4 hover:border-white/20 transition-colors" data-testid={`release-row-${r.release_id}`}>
      <div className="flex items-center gap-4">
        {/* Rank */}
        <div className="w-9 h-9 rounded-lg flex items-center justify-center font-black text-sm flex-shrink-0" style={{ backgroundColor: `${rankColor}15`, color: rankColor }}>
          {r.displayRank}
        </div>

        {/* Title + Meta */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <h3 className="text-sm font-bold text-white truncate">{r.title}</h3>
            {r.hot_streak && (
              <span className="flex items-center gap-0.5 bg-orange-500/10 text-orange-400 text-[9px] font-bold px-1.5 py-0.5 rounded-full flex-shrink-0" data-testid={`hot-streak-${r.release_id}`}>
                <Fire className="w-2.5 h-2.5" weight="fill" /> HOT
              </span>
            )}
            {r.momentum > 50 && (
              <span className="bg-green-500/10 text-green-400 text-[9px] font-bold px-1.5 py-0.5 rounded-full flex-shrink-0">
                RISING
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-[11px] text-gray-500">
            {r.genre && <span>{r.genre}</span>}
            {r.genre && r.top_platform !== 'N/A' && <span>|</span>}
            {r.top_platform !== 'N/A' && <span>Top: {r.top_platform}</span>}
            <span>| {r.release_type}</span>
          </div>
        </div>

        {/* Sparkline */}
        <div className="hidden sm:block w-24 flex-shrink-0">
          <Sparkline data={r.sparkline} color={r.growth_percent >= 0 ? '#1DB954' : '#F44336'} height={24} />
        </div>

        {/* Stats */}
        <div className="flex items-center gap-5 flex-shrink-0">
          <div className="text-right hidden lg:block">
            <p className="text-xs text-gray-500">This Week</p>
            <p className="text-sm font-bold font-mono text-white">{r.streams_this_week.toLocaleString()}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">Total</p>
            <p className="text-sm font-bold font-mono text-white">{r.total_streams.toLocaleString()}</p>
          </div>
          <div className="text-right w-16">
            <p className="text-xs text-gray-500">Growth</p>
            <p className={`text-sm font-bold font-mono flex items-center justify-end gap-0.5 ${growthColor}`}>
              <GrowthIcon className="w-3 h-3" />
              {r.growth_percent > 0 ? '+' : ''}{r.growth_percent}%
            </p>
          </div>
          <div className="text-right hidden md:block">
            <p className="text-xs text-gray-500">Revenue</p>
            <p className="text-sm font-bold font-mono text-[#1DB954]">${r.total_revenue.toFixed(2)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Sparkline({ data, color, height = 24 }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data, 1);
  const w = 96;
  const step = w / (data.length - 1 || 1);
  const points = data.map((v, i) => `${i * step},${height - (v / max) * (height - 2)}`).join(' ');
  const fillPoints = `0,${height} ${points} ${(data.length - 1) * step},${height}`;

  return (
    <svg width={w} height={height} className="overflow-visible" data-testid="sparkline">
      <defs>
        <linearGradient id={`spark-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={fillPoints} fill={`url(#spark-${color.replace('#', '')})`} />
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
