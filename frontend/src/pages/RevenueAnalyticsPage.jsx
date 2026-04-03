import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { CurrencyDollar, TrendUp, TrendDown, ChartLineUp, Calculator, UsersThree, Wallet, ArrowRight, SpinnerGap, Bank, DownloadSimple } from '@phosphor-icons/react';
import { BarChart, Bar, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';
import { toast } from 'sonner';

const PLATFORM_COLORS = {
  'Spotify': '#1DB954', 'Apple Music': '#FC3C44', 'YouTube Music': '#FF0000',
  'Amazon Music': '#FF9900', 'Tidal': '#000000', 'Deezer': '#A238FF',
  'Pandora': '#224099', 'SoundCloud': '#FF5500', 'Other': '#666',
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1a1a1a] border border-white/10 rounded-lg px-3 py-2 shadow-xl">
      <p className="text-xs text-gray-400">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-sm font-bold" style={{ color: p.color || p.stroke }}>{p.name}: ${typeof p.value === 'number' ? p.value.toFixed(2) : p.value}</p>
      ))}
    </div>
  );
};

export default function RevenueAnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showExport, setShowExport] = useState(false);
  const [calcStreams, setCalcStreams] = useState(10000);
  const [calcMix, setCalcMix] = useState({ Spotify: 45, 'Apple Music': 25, 'YouTube Music': 15, 'Amazon Music': 10, Other: 5 });
  const [calcResult, setCalcResult] = useState(null);
  const [calcLoading, setCalcLoading] = useState(false);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const res = await axios.get(`${API}/analytics/revenue`, { withCredentials: true });
      setData(res.data);
    } catch (err) { console.error(err); toast.error('Failed to load revenue data'); }
    finally { setLoading(false); }
  };

  const runCalculator = async () => {
    setCalcLoading(true);
    try {
      const res = await axios.post(`${API}/analytics/revenue/calculator`, {
        streams: calcStreams, platform_mix: calcMix,
      }, { withCredentials: true });
      setCalcResult(res.data);
    } catch (err) { console.error(err); toast.error('Calculator error'); }
    finally { setCalcLoading(false); }
  };

  const updateMix = (platform, value) => {
    setCalcMix(prev => ({ ...prev, [platform]: Math.max(0, Math.min(100, parseInt(value) || 0)) }));
  };

  if (loading) return (
    <DashboardLayout>
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-[#1DB954] border-t-transparent rounded-full animate-spin" />
      </div>
    </DashboardLayout>
  );

  if (!data) return <DashboardLayout><p className="text-gray-400">Failed to load revenue analytics.</p></DashboardLayout>;

  const s = data.summary;
  const k = data.kalmori || { total_streams: 0, total_revenue: 0, your_take: 0, artist_split_pct: 100, platforms: [], monthly_trend: [], entries_count: 0 };
  const combined = data.combined || { total_streams: s.total_streams, total_gross: s.gross_revenue, total_net: s.net_revenue };
  const monthlyData = data.monthly_trend.map((m, i) => {
    const km = k.monthly_trend?.[i] || { revenue: 0 };
    return { month: m.month.slice(5), streams_net: m.net, kalmori_rev: km.revenue };
  });
  const hasKalmori = k.entries_count > 0;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    ...(hasKalmori ? [{ id: 'kalmori', label: 'Kalmori Earnings' }] : []),
    { id: 'calculator', label: 'Calculator' },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="revenue-analytics-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Revenue Analytics</h1>
            <p className="text-gray-400 mt-1">Track your earnings across all sources</p>
          </div>
          <div className="flex items-center gap-3">
            {hasKalmori && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#7C4DFF]/10 border border-[#7C4DFF]/30 rounded-lg">
                <Bank className="w-4 h-4 text-[#7C4DFF]" />
                <span className="text-xs text-[#7C4DFF] font-medium">Kalmori Distribution Active</span>
              </div>
            )}
            <div className="relative" data-testid="export-dropdown">
              <button
                onClick={() => setShowExport(!showExport)}
                className="flex items-center gap-2 px-3 py-1.5 bg-[#1DB954]/10 border border-[#1DB954]/30 rounded-lg text-[#1DB954] text-xs font-medium hover:bg-[#1DB954]/20 transition-colors"
                data-testid="export-btn"
              >
                <DownloadSimple className="w-4 h-4" /> Export Report
              </button>
              {showExport && (
                <div className="absolute right-0 top-10 bg-[#1a1a1a] border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden min-w-[180px]">
                  <a
                    href={`${API}/analytics/revenue/export/csv`}
                    className="flex items-center gap-2 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors"
                    onClick={() => setShowExport(false)}
                    data-testid="export-csv-btn"
                  >
                    <DownloadSimple className="w-4 h-4" /> Download CSV
                  </a>
                  <a
                    href={`${API}/analytics/revenue/export/pdf`}
                    className="flex items-center gap-2 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 transition-colors border-t border-white/5"
                    onClick={() => setShowExport(false)}
                    data-testid="export-pdf-btn"
                  >
                    <DownloadSimple className="w-4 h-4" /> Download PDF
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex gap-1 bg-[#0a0a0a] border border-white/10 rounded-xl p-1 w-fit" data-testid="revenue-tabs">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === t.id ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-gray-300'}`}
              data-testid={`tab-${t.id}`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Combined Summary Cards — always visible */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4" data-testid="revenue-summary">
          <SummaryCard
            label="Total Earnings"
            value={`$${combined.total_gross.toFixed(2)}`}
            sub={`${combined.total_streams.toLocaleString()} total streams`}
            color="#1DB954"
            icon={<CurrencyDollar className="w-5 h-5 text-[#1DB954]" />}
          />
          <SummaryCard
            label="Streaming Revenue"
            value={`$${s.gross_revenue.toFixed(2)}`}
            sub={`${s.total_streams.toLocaleString()} streams`}
            color="#7C4DFF"
            icon={<ChartLineUp className="w-5 h-5 text-[#7C4DFF]" />}
          />
          <SummaryCard
            label="Kalmori Earnings"
            value={`$${k.total_revenue.toFixed(2)}`}
            sub={hasKalmori ? `${k.total_streams.toLocaleString()} streams imported` : 'No imports yet'}
            color="#FFD700"
            icon={<Bank className="w-5 h-5 text-[#FFD700]" />}
          />
          <SummaryCard
            label="Your Take"
            value={`$${(s.artist_take + k.your_take).toFixed(2)}`}
            sub={s.collab_payouts > 0 ? `After $${s.collab_payouts.toFixed(2)} splits` : 'After fees & splits'}
            color="#FC3C44"
            icon={<Wallet className="w-5 h-5 text-[#FC3C44]" />}
          />
        </div>

        {/* =========== OVERVIEW TAB =========== */}
        {activeTab === 'overview' && (
          <>
            {/* Combined Monthly Trend */}
            <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
              <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                <ChartLineUp className="w-5 h-5 text-[#1DB954]" /> Monthly Revenue Trend
              </h2>
              <div className="h-56" data-testid="monthly-trend-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={monthlyData}>
                    <defs>
                      <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1DB954" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#1DB954" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="kalGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#FFD700" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#FFD700" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="month" tick={{ fill: '#666', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#666', fontSize: 11 }} tickFormatter={v => `$${v}`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="streams_net" stroke="#1DB954" fill="url(#revGrad)" strokeWidth={2} name="Streaming" />
                    {hasKalmori && <Area type="monotone" dataKey="kalmori_rev" stroke="#FFD700" fill="url(#kalGrad)" strokeWidth={2} name="Kalmori" />}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Streaming Platform Breakdown */}
            <div className="bg-[#111] border border-white/10 rounded-2xl p-6" data-testid="platform-breakdown">
              <h2 className="text-base font-bold text-white mb-4">Streaming Earnings by Platform</h2>
              <div className="h-48 mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.platforms.slice(0, 8)} layout="vertical">
                    <XAxis type="number" tick={{ fill: '#666', fontSize: 10 }} tickFormatter={v => `$${v}`} />
                    <YAxis type="category" dataKey="platform" tick={{ fill: '#ccc', fontSize: 11 }} width={100} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="net_revenue" name="Net Revenue" radius={[0, 4, 4, 0]}>
                      {data.platforms.slice(0, 8).map((p, i) => (
                        <Cell key={i} fill={PLATFORM_COLORS[p.platform] || '#666'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <StreamingTable platforms={data.platforms} />
            </div>

            {/* Fee Breakdown */}
            <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
              <h2 className="text-base font-bold text-white mb-3">Fee Breakdown</h2>
              <div className="space-y-3">
                <FeeRow label="Gross Streaming Revenue" value={`$${s.gross_revenue.toFixed(2)}`} />
                <FeeRow label={`Platform Fee (${s.plan_cut_percent}% — ${s.plan} plan)`} value={`-$${s.platform_fee.toFixed(2)}`} color="#F44336" />
                <FeeRow label="Net Streaming Revenue" value={`$${s.net_revenue.toFixed(2)}`} color="#7C4DFF" />
                {hasKalmori && <FeeRow label={`Kalmori Earnings (${k.artist_split_pct}% split)`} value={`+$${k.your_take.toFixed(2)}`} color="#FFD700" />}
                {s.collab_payouts > 0 && <FeeRow label="Collaborator Splits" value={`-$${s.collab_payouts.toFixed(2)}`} color="#E040FB" />}
                <div className="border-t border-white/10 pt-3">
                  <FeeRow label="Your Total Take-Home" value={`$${(s.artist_take + k.your_take).toFixed(2)}`} color="#1DB954" bold />
                </div>
              </div>
            </div>

            {/* Collaborator Splits */}
            {data.collaborator_splits.length > 0 && (
              <div className="bg-[#111] border border-white/10 rounded-2xl p-6" data-testid="collab-splits">
                <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <UsersThree className="w-5 h-5 text-[#E040FB]" /> Collaborator Royalty Splits
                </h2>
                <div className="space-y-3">
                  {data.collaborator_splits.map((c, i) => (
                    <div key={i} className="flex items-center justify-between bg-[#0a0a0a] border border-white/5 rounded-xl p-4" data-testid={`split-row-${i}`}>
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-[#E040FB]/10 flex items-center justify-center text-[#E040FB] font-bold text-sm">
                          {c.collaborator.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">{c.collaborator}</p>
                          <p className="text-xs text-gray-500">{c.role}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold text-[#E040FB]">${c.estimated_amount.toFixed(2)}</p>
                        <p className="text-xs text-gray-500">{c.split_percentage}% split</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Rate Explainer */}
            <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
              <h2 className="text-base font-bold text-white mb-3">Per-Stream Rate Guide</h2>
              <p className="text-xs text-gray-500 mb-4">Industry average per-stream payout rates. Actual rates vary by listener location, subscription type, and platform terms.</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {Object.entries(PLATFORM_COLORS).filter(([k]) => k !== 'Other').map(([name, color]) => {
                  const rate = { 'Spotify': 0.004, 'Apple Music': 0.008, 'YouTube Music': 0.002, 'Amazon Music': 0.004, 'Tidal': 0.012, 'Deezer': 0.003, 'Pandora': 0.002, 'SoundCloud': 0.003 }[name] || 0.004;
                  return (
                    <div key={name} className="bg-[#0a0a0a] border border-white/5 rounded-lg p-3" data-testid={`rate-${name.replace(/\s+/g, '-').toLowerCase()}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
                        <span className="text-xs text-gray-300 font-medium">{name}</span>
                      </div>
                      <p className="text-lg font-bold font-mono text-white">${rate.toFixed(4)}</p>
                      <p className="text-[10px] text-gray-600">per stream</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

        {/* =========== KALMORI TAB =========== */}
        {activeTab === 'kalmori' && hasKalmori && (
          <>
            {/* Kalmori Header */}
            <div className="bg-gradient-to-br from-[#1a1000] to-[#111] border border-[#FFD700]/20 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-12 h-12 rounded-xl bg-[#FFD700]/20 flex items-center justify-center">
                  <Bank className="w-6 h-6 text-[#FFD700]" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">Kalmori Distribution</h2>
                  <p className="text-xs text-gray-400">Earnings from distributor reports uploaded by your admin</p>
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4" data-testid="kalmori-summary">
                <KalmoriStat label="Total Revenue" value={`$${k.total_revenue.toFixed(2)}`} />
                <KalmoriStat label="Your Take" value={`$${k.your_take.toFixed(2)}`} sub={`${k.artist_split_pct}% split`} />
                <KalmoriStat label="Streams" value={k.total_streams.toLocaleString()} />
                <KalmoriStat label="Reports Processed" value={k.entries_count.toString()} />
              </div>
            </div>

            {/* Kalmori Platform Breakdown */}
            {k.platforms.length > 0 && (
              <div className="bg-[#111] border border-white/10 rounded-2xl p-6" data-testid="kalmori-platform-breakdown">
                <h2 className="text-base font-bold text-white mb-4">Kalmori Earnings by Platform</h2>
                <div className="h-48 mb-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={k.platforms.slice(0, 8)} layout="vertical">
                      <XAxis type="number" tick={{ fill: '#666', fontSize: 10 }} tickFormatter={v => `$${v}`} />
                      <YAxis type="category" dataKey="platform" tick={{ fill: '#ccc', fontSize: 11 }} width={120} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="revenue" name="Revenue" radius={[0, 4, 4, 0]}>
                        {k.platforms.slice(0, 8).map((p, i) => (
                          <Cell key={i} fill={PLATFORM_COLORS[p.platform] || '#FFD700'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm" data-testid="kalmori-platform-table">
                    <thead>
                      <tr className="text-gray-500 text-xs border-b border-white/10">
                        <th className="text-left py-2 font-medium">Platform</th>
                        <th className="text-right py-2 font-medium">Streams</th>
                        <th className="text-right py-2 font-medium">Revenue</th>
                        <th className="text-right py-2 font-medium">Your Take ({k.artist_split_pct}%)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {k.platforms.map((p, i) => (
                        <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]" data-testid={`kalmori-row-${i}`}>
                          <td className="py-2.5 flex items-center gap-2">
                            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PLATFORM_COLORS[p.platform] || '#FFD700' }} />
                            <span className="text-white font-medium">{p.platform}</span>
                          </td>
                          <td className="py-2.5 text-right text-gray-300 font-mono">{p.streams.toLocaleString()}</td>
                          <td className="py-2.5 text-right text-gray-300 font-mono">${p.revenue.toFixed(2)}</td>
                          <td className="py-2.5 text-right text-[#FFD700] font-mono font-bold">${(p.revenue * k.artist_split_pct / 100).toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr className="border-t border-white/10">
                        <td className="py-2.5 text-sm text-gray-400 font-medium">Total</td>
                        <td className="py-2.5 text-right text-white font-mono font-bold">{k.total_streams.toLocaleString()}</td>
                        <td className="py-2.5 text-right text-white font-mono font-bold">${k.total_revenue.toFixed(2)}</td>
                        <td className="py-2.5 text-right text-[#FFD700] font-mono font-bold">${k.your_take.toFixed(2)}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            )}

            {/* Kalmori Monthly Trend */}
            <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
              <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                <ChartLineUp className="w-5 h-5 text-[#FFD700]" /> Kalmori Monthly Trend
              </h2>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={k.monthly_trend.map(m => ({ ...m, month: m.month.slice(5) }))}>
                    <defs>
                      <linearGradient id="kalGrad2" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#FFD700" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#FFD700" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="month" tick={{ fill: '#666', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#666', fontSize: 11 }} tickFormatter={v => `$${v}`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="revenue" stroke="#FFD700" fill="url(#kalGrad2)" strokeWidth={2} name="Kalmori Revenue" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Attribution Note */}
            <div className="bg-[#0a0a0a] border border-white/5 rounded-xl px-5 py-4 flex items-start gap-3">
              <Bank className="w-5 h-5 text-[#FFD700] mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-gray-300 font-medium">About Kalmori Distribution Earnings</p>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                  These earnings are derived from verified distributor reports processed through Kalmori Distribution. Your revenue share is calculated based on your agreed split terms. Contact your admin for any discrepancies.
                </p>
              </div>
            </div>
          </>
        )}

        {/* =========== CALCULATOR TAB =========== */}
        {activeTab === 'calculator' && (
          <div className="bg-gradient-to-br from-[#0a1a0a] to-[#111] border border-[#1DB954]/30 rounded-2xl p-6" data-testid="revenue-calculator">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-[#1DB954]/20 flex items-center justify-center">
                <Calculator className="w-5 h-5 text-[#1DB954]" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">What-If Revenue Calculator</h2>
                <p className="text-xs text-gray-400">Estimate earnings for any number of streams across platforms</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Total Streams</label>
                <input
                  type="number"
                  value={calcStreams}
                  onChange={e => setCalcStreams(Math.max(0, parseInt(e.target.value) || 0))}
                  className="w-full sm:w-48 bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white font-mono focus:border-[#1DB954]/50 focus:outline-none"
                  data-testid="calc-streams-input"
                />
              </div>

              <div>
                <label className="text-xs text-gray-400 mb-2 block">Platform Mix (%)</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                  {Object.entries(calcMix).map(([platform, pct]) => (
                    <div key={platform}>
                      <div className="flex items-center gap-1.5 mb-1">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: PLATFORM_COLORS[platform] || '#666' }} />
                        <span className="text-xs text-gray-400">{platform}</span>
                      </div>
                      <input
                        type="number"
                        value={pct}
                        onChange={e => updateMix(platform, e.target.value)}
                        className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-2 py-1.5 text-sm text-white font-mono text-center focus:border-[#1DB954]/50 focus:outline-none"
                        data-testid={`calc-mix-${platform.replace(/\s+/g, '-').toLowerCase()}`}
                      />
                    </div>
                  ))}
                </div>
                {Object.values(calcMix).reduce((a, b) => a + b, 0) !== 100 && (
                  <p className="text-xs text-yellow-500 mt-1">Total: {Object.values(calcMix).reduce((a, b) => a + b, 0)}% (should be 100%)</p>
                )}
              </div>

              <button
                onClick={runCalculator}
                disabled={calcLoading}
                className="px-6 py-3 bg-gradient-to-r from-[#1DB954] to-[#1ED760] text-black font-semibold rounded-xl hover:opacity-90 transition-opacity flex items-center gap-2 disabled:opacity-50"
                data-testid="calc-run-btn"
              >
                {calcLoading ? <SpinnerGap className="w-5 h-5 animate-spin" /> : <Calculator className="w-5 h-5" />}
                Calculate Earnings
              </button>
            </div>

            {calcResult && (
              <div className="mt-6 space-y-4" data-testid="calc-results">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <ResultCard label="Gross Revenue" value={`$${calcResult.gross_revenue.toFixed(2)}`} color="#1DB954" />
                  <ResultCard label="Platform Fee" value={`-$${calcResult.platform_fee.toFixed(2)}`} color="#F44336" />
                  <ResultCard label="Net Revenue" value={`$${calcResult.net_revenue.toFixed(2)}`} color="#7C4DFF" />
                  <ResultCard label="Your Take" value={`$${calcResult.artist_take.toFixed(2)}`} color="#FFD700" />
                </div>

                <div className="bg-[#0a0a0a] border border-white/10 rounded-xl overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-gray-500 text-xs border-b border-white/10">
                        <th className="text-left p-3 font-medium">Platform</th>
                        <th className="text-right p-3 font-medium">Streams</th>
                        <th className="text-right p-3 font-medium">Rate</th>
                        <th className="text-right p-3 font-medium">Revenue</th>
                      </tr>
                    </thead>
                    <tbody>
                      {calcResult.platform_breakdown.map((p, i) => (
                        <tr key={i} className="border-b border-white/5" data-testid={`calc-row-${i}`}>
                          <td className="p-3 flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: PLATFORM_COLORS[p.platform] || '#666' }} />
                            <span className="text-white">{p.platform}</span>
                          </td>
                          <td className="p-3 text-right text-gray-300 font-mono">{p.streams.toLocaleString()}</td>
                          <td className="p-3 text-right text-gray-500 font-mono">${p.rate.toFixed(4)}</td>
                          <td className="p-3 text-right text-white font-mono font-bold">${p.gross.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {calcResult.collaborator_splits?.length > 0 && (
                  <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-4">
                    <h4 className="text-xs font-semibold text-gray-400 mb-2">Collaborator Splits Applied</h4>
                    {calcResult.collaborator_splits.map((c, i) => (
                      <div key={i} className="flex items-center justify-between text-sm py-1">
                        <span className="text-gray-300">{c.name} ({c.percentage}%)</span>
                        <span className="text-[#E040FB] font-mono font-bold">${c.amount.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

function SummaryCard({ label, value, sub, color, icon }) {
  return (
    <div className="bg-[#111] border border-white/10 rounded-2xl p-5" data-testid={`summary-${label.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
          {icon}
        </div>
        <div>
          <p className="text-xl sm:text-2xl font-bold font-mono" style={{ color }}>{value}</p>
          <p className="text-xs text-gray-400">{label}</p>
          <p className="text-[10px] text-gray-600">{sub}</p>
        </div>
      </div>
    </div>
  );
}

function ResultCard({ label, value, color }) {
  return (
    <div className="bg-[#111] border border-white/10 rounded-xl p-3 text-center">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-lg font-bold font-mono" style={{ color }}>{value}</p>
    </div>
  );
}

function KalmoriStat({ label, value, sub }) {
  return (
    <div className="bg-black/30 border border-[#FFD700]/10 rounded-xl p-4 text-center">
      <p className="text-xl sm:text-2xl font-bold font-mono text-[#FFD700]">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{label}</p>
      {sub && <p className="text-[10px] text-gray-600 mt-0.5">{sub}</p>}
    </div>
  );
}

function FeeRow({ label, value, color, bold }) {
  return (
    <div className="flex items-center justify-between">
      <span className={`text-sm ${bold ? 'text-white font-semibold' : 'text-gray-400'}`}>{label}</span>
      <span className={`text-sm font-mono ${bold ? 'font-bold text-lg' : 'font-medium'}`} style={color ? { color } : { color: '#fff' }}>{value}</span>
    </div>
  );
}

function StreamingTable({ platforms }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm" data-testid="platform-table">
        <thead>
          <tr className="text-gray-500 text-xs border-b border-white/10">
            <th className="text-left py-2 font-medium">Platform</th>
            <th className="text-right py-2 font-medium">Streams</th>
            <th className="text-right py-2 font-medium">Rate</th>
            <th className="text-right py-2 font-medium">Gross</th>
            <th className="text-right py-2 font-medium">Net</th>
          </tr>
        </thead>
        <tbody>
          {platforms.map((p, i) => (
            <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]" data-testid={`platform-row-${i}`}>
              <td className="py-2.5 flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PLATFORM_COLORS[p.platform] || '#666' }} />
                <span className="text-white font-medium">{p.platform}</span>
              </td>
              <td className="py-2.5 text-right text-gray-300 font-mono">{p.streams.toLocaleString()}</td>
              <td className="py-2.5 text-right text-gray-500 font-mono">${p.rate_per_stream.toFixed(4)}</td>
              <td className="py-2.5 text-right text-gray-300 font-mono">${p.gross_revenue.toFixed(2)}</td>
              <td className="py-2.5 text-right text-white font-mono font-bold">${p.net_revenue.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
