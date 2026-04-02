import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { 
  ChartLineUp, Play, CurrencyDollar, Globe, TrendUp, Sparkle, MusicNote, TiktokLogo, MapPin
} from '@phosphor-icons/react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';
import { toast } from 'sonner';

const PLATFORM_COLORS = { Spotify: '#1DB954', 'Apple Music': '#FC3C44', 'YouTube Music': '#FF0000', 'Amazon Music': '#FF9900', TikTok: '#010101', Tidal: '#00FFFF', Deezer: '#A238FF', SoundCloud: '#FF5500', Other: '#888' };

const COUNTRY_FLAGS = { US: '\u{1F1FA}\u{1F1F8}', UK: '\u{1F1EC}\u{1F1E7}', GB: '\u{1F1EC}\u{1F1E7}', NG: '\u{1F1F3}\u{1F1EC}', DE: '\u{1F1E9}\u{1F1EA}', CA: '\u{1F1E8}\u{1F1E6}', AU: '\u{1F1E6}\u{1F1FA}', BR: '\u{1F1E7}\u{1F1F7}', JP: '\u{1F1EF}\u{1F1F5}', FR: '\u{1F1EB}\u{1F1F7}', IN: '\u{1F1EE}\u{1F1F3}', JM: '\u{1F1EF}\u{1F1F2}', KE: '\u{1F1F0}\u{1F1EA}', GH: '\u{1F1EC}\u{1F1ED}', ZA: '\u{1F1FF}\u{1F1E6}' };

const WORLD_REGIONS = [
  { name: 'United States', code: 'US', streams: 0, lat: 39.8, lng: -98.5 },
  { name: 'United Kingdom', code: 'GB', streams: 0, lat: 55.3, lng: -3.4 },
  { name: 'Germany', code: 'DE', streams: 0, lat: 51.1, lng: 10.4 },
  { name: 'Brazil', code: 'BR', streams: 0, lat: -14.2, lng: -51.9 },
  { name: 'Nigeria', code: 'NG', streams: 0, lat: 9.1, lng: 8.7 },
  { name: 'Japan', code: 'JP', streams: 0, lat: 36.2, lng: 138.2 },
  { name: 'India', code: 'IN', streams: 0, lat: 20.6, lng: 78.9 },
  { name: 'France', code: 'FR', streams: 0, lat: 46.2, lng: 2.2 },
  { name: 'Canada', code: 'CA', streams: 0, lat: 56.1, lng: -106.3 },
  { name: 'Australia', code: 'AU', streams: 0, lat: -25.3, lng: 133.8 },
];

const TIKTOK_TRENDS = [
  { id: 1, sound: 'Original Sound', uses: 0, trend: 'stable', snippet: 'No UGC data yet' },
];

const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [insights, setInsights] = useState('');
  const [platformData, setPlatformData] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [liveFeed, setLiveFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      const [analyticsRes, platformRes, chartRes, feedRes] = await Promise.all([
        axios.get(`${API}/analytics/overview`, { withCredentials: true }),
        axios.get(`${API}/analytics/platform-breakdown`, { withCredentials: true }),
        axios.get(`${API}/analytics/chart-data?days=14`, { withCredentials: true }),
        axios.get(`${API}/analytics/live-feed?limit=20`, { withCredentials: true }).catch(() => ({ data: { events: [] } })),
      ]);
      setAnalytics(analyticsRes.data);
      setPlatformData(platformRes.data);
      setChartData(chartRes.data);
      setLiveFeed(feedRes.data.events || []);
    } catch (error) { console.error('Analytics fetch error:', error); }
    finally { setLoading(false); }
  };

  const fetchAIInsights = async () => {
    setInsightsLoading(true);
    try {
      const res = await axios.get(`${API}/ai/analytics-insights`, { withCredentials: true });
      setInsights(res.data.insights);
      toast.success('AI insights generated!');
    } catch { toast.error('Failed to generate insights'); }
    finally { setInsightsLoading(false); }
  };

  const COLORS = ['#1DB954', '#FC3C44', '#FF0000', '#FF9900', '#00FFFF', '#888'];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload?.length) {
      return (
        <div className="bg-[#141414] border border-white/10 p-3 rounded-md">
          <p className="text-xs text-[#A1A1AA]">{label}</p>
          {payload.map((p, i) => <p key={i} className="text-sm font-mono text-white">{p.name}: {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}</p>)}
        </div>
      );
    }
    return null;
  };

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'live', label: 'Live Activity' },
    { id: 'audience', label: 'Audience Map' },
    { id: 'tiktok', label: 'TikTok UGC' },
    { id: 'platforms', label: 'Platforms' },
  ];

  if (loading) return <DashboardLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#FF3B30] border-t-transparent rounded-full animate-spin" /></div></DashboardLayout>;

  const storeData = analytics?.streams_by_store ? Object.entries(analytics.streams_by_store).map(([name, value]) => ({ name, value })) : [];
  const countryData = analytics?.streams_by_country ? Object.entries(analytics.streams_by_country).map(([name, value]) => ({ name, value })) : [];

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="analytics-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Analytics</h1>
            <p className="text-[#A1A1AA] mt-1">Track your streaming performance</p>
          </div>
          <Button onClick={fetchAIInsights} disabled={insightsLoading} className="bg-[#FFCC00] hover:bg-[#FFCC00]/90 text-black" data-testid="ai-insights-btn">
            {insightsLoading ? <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" /> : <><Sparkle className="w-4 h-4 mr-2" />Get AI Insights</>}
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-[#141414] rounded-lg p-1 border border-white/10">
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-4 py-2.5 rounded-md text-sm font-medium transition-all ${activeTab === tab.id ? 'bg-[#7C4DFF] text-white' : 'text-gray-400 hover:text-white'}`}
              data-testid={`tab-${tab.id}`}>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: <Play className="w-5 h-5" />, value: analytics?.total_streams?.toLocaleString() || '0', label: 'Total Streams', color: '#FF3B30', change: '+12.5%' },
            { icon: <CurrencyDollar className="w-5 h-5" />, value: `$${analytics?.total_earnings?.toFixed(2) || '0.00'}`, label: 'Total Earnings', color: '#22C55E', change: '+8.2%' },
            { icon: <TrendUp className="w-5 h-5" />, value: analytics?.total_downloads?.toLocaleString() || '0', label: 'Downloads', color: '#FFCC00' },
            { icon: <Globe className="w-5 h-5" />, value: analytics?.release_count || '0', label: 'Releases', color: '#007AFF' },
          ].map((stat, i) => (
            <div key={i} className="bg-[#141414] border border-white/10 p-5 rounded-md">
              <div className="flex items-center justify-between mb-3">
                <div className="w-10 h-10 rounded-md flex items-center justify-center" style={{ backgroundColor: `${stat.color}15`, color: stat.color }}>{stat.icon}</div>
                {stat.change && <span className="text-xs text-[#22C55E] font-mono">{stat.change}</span>}
              </div>
              <p className="text-2xl font-bold font-mono">{stat.value}</p>
              <p className="text-sm text-[#A1A1AA] mt-1">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* AI Insights */}
        {insights && (
          <div className="bg-[#FFCC00]/10 border border-[#FFCC00]/30 rounded-md p-6" data-testid="ai-insights-panel">
            <h2 className="text-lg font-medium mb-4 flex items-center gap-2 text-[#FFCC00]"><Sparkle className="w-5 h-5" />AI Insights</h2>
            <div className="prose prose-invert max-w-none text-sm whitespace-pre-wrap">{insights}</div>
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
              <h2 className="text-lg font-medium mb-6 flex items-center gap-2"><ChartLineUp className="w-5 h-5 text-[#FF3B30]" />Streams Over Time</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData.length ? chartData : analytics?.daily_streams || []}>
                    <defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#FF3B30" stopOpacity={0.3}/><stop offset="95%" stopColor="#FF3B30" stopOpacity={0}/></linearGradient></defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="date" tick={{ fill: '#71717A', fontSize: 10 }} axisLine={{ stroke: 'rgba(255,255,255,0.1)' }} />
                    <YAxis tick={{ fill: '#71717A', fontSize: 10 }} axisLine={{ stroke: 'rgba(255,255,255,0.1)' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey={chartData.length ? "plays" : "streams"} stroke="#FF3B30" strokeWidth={2} fill="url(#sg)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
              <h2 className="text-lg font-medium mb-6">Revenue Over Time</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs><linearGradient id="rg" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#22C55E" stopOpacity={0.3}/><stop offset="95%" stopColor="#22C55E" stopOpacity={0}/></linearGradient></defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="date" tick={{ fill: '#71717A', fontSize: 10 }} />
                    <YAxis tick={{ fill: '#71717A', fontSize: 10 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="revenue" stroke="#22C55E" strokeWidth={2} fill="url(#rg)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Live Activity Tab */}
        {activeTab === 'live' && (
          <div className="space-y-6">
            <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-medium flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-[#4CAF50] animate-pulse" />
                  Live Streaming Feed
                </h2>
                <button onClick={fetchAll} className="text-xs text-[#7C4DFF] hover:underline" data-testid="refresh-feed-btn">Refresh</button>
              </div>
              {liveFeed.length === 0 ? (
                <div className="text-center py-12">
                  <Play className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-sm text-[#A1A1AA]">No streaming events yet. Distribute your music to start seeing data!</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {liveFeed.map((event, i) => (
                    <div key={event.id || i} className="flex items-center gap-3 p-3 rounded-lg bg-[#0a0a0a] hover:bg-white/5 transition-colors animate-fadeInUp" style={{ animationDelay: `${i * 0.03}s` }} data-testid={`stream-event-${i}`}>
                      <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${PLATFORM_COLORS[event.platform] || '#888'}20` }}>
                        <MusicNote className="w-4 h-4" style={{ color: PLATFORM_COLORS[event.platform] || '#888' }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-white truncate">{event.release_title || 'Track'}</span>
                          <span className="text-xs text-gray-500">on</span>
                          <span className="text-xs font-medium" style={{ color: PLATFORM_COLORS[event.platform] || '#888' }}>{event.platform}</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span>{COUNTRY_FLAGS[event.country] || ''} {event.country}</span>
                          <span>{event.timestamp ? new Date(event.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : ''}</span>
                        </div>
                      </div>
                      <span className="text-xs font-mono text-[#4CAF50]">+${(event.revenue || 0).toFixed(4)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Platform stats summary */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {(platformData.length ? platformData.slice(0, 4) : []).map(p => (
                <div key={p.name} className="bg-[#141414] border border-white/10 p-4 rounded-md text-center">
                  <div className="w-10 h-10 rounded-full mx-auto mb-2 flex items-center justify-center" style={{ backgroundColor: `${p.color || '#888'}20` }}>
                    <MusicNote className="w-5 h-5" style={{ color: p.color || '#888' }} />
                  </div>
                  <p className="text-sm font-bold font-mono">{(p.streams || 0).toLocaleString()}</p>
                  <p className="text-xs text-[#A1A1AA]">{p.name}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Audience Map Tab */}
        {activeTab === 'audience' && (
          <div className="space-y-6">
            <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
              <h2 className="text-lg font-medium mb-6 flex items-center gap-2"><MapPin className="w-5 h-5 text-[#007AFF]" />Audience Map</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* World Map Visualization */}
                <div className="relative bg-[#0a0a0a] rounded-lg p-6 h-[400px] flex items-center justify-center overflow-hidden">
                  <svg viewBox="0 0 800 400" className="w-full h-full opacity-30">
                    <ellipse cx="400" cy="200" rx="380" ry="180" fill="none" stroke="#333" strokeWidth="1"/>
                    <ellipse cx="400" cy="200" rx="250" ry="120" fill="none" stroke="#333" strokeWidth="0.5"/>
                    <line x1="20" y1="200" x2="780" y2="200" stroke="#333" strokeWidth="0.5"/>
                    <line x1="400" y1="20" x2="400" y2="380" stroke="#333" strokeWidth="0.5"/>
                  </svg>
                  {(countryData.length ? countryData.map(c => WORLD_REGIONS.find(r => r.name === c.name) || WORLD_REGIONS[0]).filter(Boolean) : WORLD_REGIONS).map((region, i) => (
                    <div key={region.code} className="absolute group" style={{
                      left: `${((region.lng + 180) / 360) * 100}%`,
                      top: `${((90 - region.lat) / 180) * 100}%`,
                      transform: 'translate(-50%, -50%)'
                    }}>
                      <div className={`w-3 h-3 rounded-full bg-[#7C4DFF] animate-pulse`} style={{ animationDelay: `${i * 0.2}s` }}/>
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block bg-[#141414] border border-white/10 p-2 rounded text-xs whitespace-nowrap z-10">
                        <p className="font-medium">{region.name}</p>
                        <p className="text-[#A1A1AA]">{region.streams.toLocaleString()} streams</p>
                      </div>
                    </div>
                  ))}
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <p className="text-[#A1A1AA]/50 text-sm">Audience data populates as you get streams</p>
                  </div>
                </div>

                {/* Top Countries */}
                <div className="space-y-3">
                  <h3 className="text-sm font-medium text-[#A1A1AA] uppercase tracking-wider mb-4">Top Countries</h3>
                  {(countryData.length ? countryData : WORLD_REGIONS.slice(0, 8)).map((country, i) => {
                    const name = country.name;
                    const streams = country.value || country.streams || 0;
                    const maxStreams = Math.max(...(countryData.length ? countryData.map(c => c.value) : [1]));
                    const pct = maxStreams > 0 ? (streams / maxStreams) * 100 : 0;
                    return (
                      <div key={name} className="flex items-center gap-3">
                        <span className="text-sm font-mono w-6 text-[#A1A1AA]">{i + 1}</span>
                        <div className="flex-1">
                          <div className="flex justify-between mb-1">
                            <span className="text-sm">{name}</span>
                            <span className="text-xs font-mono text-[#A1A1AA]">{streams.toLocaleString()}</span>
                          </div>
                          <div className="w-full bg-[#1a1a1a] rounded-full h-1.5">
                            <div className="h-full rounded-full bg-gradient-to-r from-[#7C4DFF] to-[#E040FB]" style={{ width: `${pct}%` }}/>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TikTok UGC Tab */}
        {activeTab === 'tiktok' && (
          <div className="space-y-6">
            <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
              <h2 className="text-lg font-medium mb-2 flex items-center gap-2"><TiktokLogo className="w-5 h-5" />TikTok UGC Trends</h2>
              <p className="text-sm text-[#A1A1AA] mb-6">Track how your music is being used in TikTok videos</p>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <div className="bg-[#0a0a0a] rounded-lg p-5 text-center">
                  <p className="text-3xl font-bold font-mono">0</p>
                  <p className="text-sm text-[#A1A1AA] mt-1">Total UGC Videos</p>
                </div>
                <div className="bg-[#0a0a0a] rounded-lg p-5 text-center">
                  <p className="text-3xl font-bold font-mono">0</p>
                  <p className="text-sm text-[#A1A1AA] mt-1">Total Views</p>
                </div>
                <div className="bg-[#0a0a0a] rounded-lg p-5 text-center">
                  <p className="text-3xl font-bold font-mono text-[#22C55E]">--</p>
                  <p className="text-sm text-[#A1A1AA] mt-1">Trend Direction</p>
                </div>
              </div>

              {/* Trending Sounds */}
              <h3 className="text-sm font-medium text-[#A1A1AA] uppercase tracking-wider mb-4">Your Sounds</h3>
              {TIKTOK_TRENDS.map(trend => (
                <div key={trend.id} className="bg-[#0a0a0a] rounded-lg p-4 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-[#E040FB] to-[#FF4081] flex items-center justify-center">
                    <MusicNote className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{trend.sound}</p>
                    <p className="text-xs text-[#A1A1AA]">{trend.uses.toLocaleString()} videos using this sound</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${trend.trend === 'up' ? 'bg-green-400/10 text-green-400' : trend.trend === 'down' ? 'bg-red-400/10 text-red-400' : 'bg-gray-400/10 text-gray-400'}`}>
                    {trend.trend === 'up' ? 'Trending' : trend.trend === 'down' ? 'Declining' : 'No data yet'}
                  </div>
                </div>
              ))}

              <div className="mt-6 p-4 bg-[#7C4DFF]/10 border border-[#7C4DFF]/30 rounded-lg">
                <p className="text-sm text-[#A1A1AA]">TikTok UGC data will populate once your distributed tracks are used in TikTok videos. Distribute your music to start tracking!</p>
              </div>
            </div>
          </div>
        )}

        {/* Platforms Tab */}
        {activeTab === 'platforms' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
              <h2 className="text-lg font-medium mb-6">Platform Distribution</h2>
              <div className="h-64 flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={platformData.length ? platformData.map(p => ({name: p.name, value: p.percentage || p.streams || 0})) : storeData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      {(platformData.length ? platformData : storeData).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={PLATFORM_COLORS[entry.name] || COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {(platformData.length ? platformData : storeData).map((entry) => (
                  <div key={entry.name} className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: PLATFORM_COLORS[entry.name] || '#888' }} />
                    <span className="text-[#A1A1AA]">{entry.name}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
              <h2 className="text-lg font-medium mb-6">Platform Details</h2>
              <div className="space-y-4">
                {(platformData.length ? platformData : []).map(platform => (
                  <div key={platform.name} className="flex items-center justify-between p-3 bg-[#0a0a0a] rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: `${platform.color || '#888'}20`, color: platform.color || '#888' }}>
                        <MusicNote className="w-4 h-4" />
                      </div>
                      <span className="text-sm font-medium">{platform.name}</span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-mono">{(platform.streams || platform.percentage || 0).toLocaleString()}</p>
                      <p className="text-xs text-[#A1A1AA]">${(platform.revenue || 0).toFixed(2)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {countryData.length > 0 && (
              <div className="bg-[#141414] border border-white/10 p-6 rounded-md lg:col-span-2">
                <h2 className="text-lg font-medium mb-6">Streams by Country</h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={countryData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis type="number" tick={{ fill: '#71717A', fontSize: 10 }} />
                      <YAxis dataKey="name" type="category" tick={{ fill: '#71717A', fontSize: 10 }} width={60} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="value" fill="#FF3B30" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default AnalyticsPage;
