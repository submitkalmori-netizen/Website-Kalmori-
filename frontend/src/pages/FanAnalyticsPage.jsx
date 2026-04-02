import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Users, Globe, ChartLineUp, Clock, TrendUp, MusicNote } from '@phosphor-icons/react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COUNTRY_NAMES = { US: 'United States', UK: 'United Kingdom', NG: 'Nigeria', DE: 'Germany', CA: 'Canada', AU: 'Australia', BR: 'Brazil', JP: 'Japan', FR: 'France', IN: 'India', JM: 'Jamaica', KE: 'Kenya', GH: 'Ghana', ZA: 'South Africa' };
const COUNTRY_FLAGS = { US: '\u{1F1FA}\u{1F1F8}', UK: '\u{1F1EC}\u{1F1E7}', NG: '\u{1F1F3}\u{1F1EC}', DE: '\u{1F1E9}\u{1F1EA}', CA: '\u{1F1E8}\u{1F1E6}', AU: '\u{1F1E6}\u{1F1FA}', BR: '\u{1F1E7}\u{1F1F7}', JP: '\u{1F1EF}\u{1F1F5}', FR: '\u{1F1EB}\u{1F1F7}', IN: '\u{1F1EE}\u{1F1F3}', JM: '\u{1F1EF}\u{1F1F2}', KE: '\u{1F1F0}\u{1F1EA}', GH: '\u{1F1EC}\u{1F1ED}', ZA: '\u{1F1FF}\u{1F1E6}' };

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1a1a1a] border border-white/10 rounded-lg px-3 py-2 shadow-xl">
      <p className="text-xs text-gray-400">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-sm font-bold" style={{ color: p.color }}>{p.value.toLocaleString()}</p>
      ))}
    </div>
  );
};

export default function FanAnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const res = await axios.get(`${API}/fan-analytics/overview`, { withCredentials: true });
      setData(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  if (loading) return (
    <DashboardLayout>
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" />
      </div>
    </DashboardLayout>
  );

  if (!data) return <DashboardLayout><p className="text-gray-400">Failed to load fan analytics.</p></DashboardLayout>;

  const totalStreams = data.platform_engagement.reduce((s, p) => s + p.streams, 0);

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="fan-analytics-page">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Fan Analytics</h1>
          <p className="text-gray-400 mt-1">Understand your audience — where they listen, when, and on which platforms</p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard icon={<Users className="w-5 h-5 text-[#7C4DFF]" />} value={data.total_subscribers} label="Pre-Save Subs" color="#7C4DFF" />
          <StatCard icon={<Globe className="w-5 h-5 text-[#E040FB]" />} value={data.top_countries?.length || 0} label="Countries" color="#E040FB" />
          <StatCard icon={<MusicNote className="w-5 h-5 text-[#1DB954]" />} value={totalStreams.toLocaleString()} label="Total Streams" color="#1DB954" />
          <StatCard icon={<TrendUp className="w-5 h-5 text-[#FFD700]" />} value={data.total_campaigns} label="Campaigns" color="#FFD700" />
        </div>

        {/* Listener Growth Chart */}
        <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
          <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <ChartLineUp className="w-5 h-5 text-[#7C4DFF]" /> Listener Growth (30 Days)
          </h2>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.listener_growth}>
                <defs>
                  <linearGradient id="growthGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7C4DFF" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#7C4DFF" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fill: '#666', fontSize: 10 }} tickFormatter={v => v.slice(5)} />
                <YAxis tick={{ fill: '#666', fontSize: 10 }} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="listeners" stroke="#7C4DFF" fill="url(#growthGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Countries */}
          <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Globe className="w-5 h-5 text-[#E040FB]" /> Top Listener Countries
            </h2>
            <div className="space-y-3">
              {data.top_countries?.slice(0, 8).map((c, i) => (
                <div key={c.country} className="flex items-center gap-3" data-testid={`country-${c.country}`}>
                  <span className="text-lg w-8">{COUNTRY_FLAGS[c.country] || ''}</span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-white font-medium">{COUNTRY_NAMES[c.country] || c.country}</span>
                      <span className="text-xs text-gray-400">{c.percentage}%</span>
                    </div>
                    <div className="w-full h-2 bg-[#1a1a1a] rounded-full overflow-hidden">
                      <div className="h-full rounded-full bg-gradient-to-r from-[#7C4DFF] to-[#E040FB]" style={{ width: `${c.percentage}%` }} />
                    </div>
                  </div>
                  <span className="text-xs text-gray-500 font-mono w-16 text-right">{c.streams.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Platform Engagement */}
          <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <MusicNote className="w-5 h-5 text-[#1DB954]" /> Platform Engagement
            </h2>
            <div className="flex items-center gap-6">
              <div className="w-40 h-40 flex-shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={data.platform_engagement.slice(0, 6)} dataKey="streams" innerRadius={35} outerRadius={70} paddingAngle={2}>
                      {data.platform_engagement.slice(0, 6).map((p, i) => (
                        <Cell key={i} fill={p.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex-1 space-y-2">
                {data.platform_engagement?.slice(0, 6).map(p => (
                  <div key={p.name} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: p.color }} />
                    <span className="text-xs text-gray-300 flex-1">{p.name}</span>
                    <span className="text-xs text-gray-500 font-mono">{p.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Peak Listening Hours */}
        <div className="bg-[#111] border border-white/10 rounded-2xl p-6">
          <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-[#FFD700]" /> Peak Listening Hours (UTC)
          </h2>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.peak_hours}>
                <XAxis dataKey="hour" tick={{ fill: '#666', fontSize: 10 }} tickFormatter={v => `${v}:00`} />
                <YAxis tick={{ fill: '#666', fontSize: 10 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#FFD700" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">Best times to release new music and run campaigns</p>
        </div>
      </div>
    </DashboardLayout>
  );
}

function StatCard({ icon, value, label, color }) {
  return (
    <div className="bg-[#111] border border-white/10 rounded-2xl p-5">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
          {icon}
        </div>
        <div>
          <p className="text-2xl font-bold font-mono">{value}</p>
          <p className="text-sm text-gray-400">{label}</p>
        </div>
      </div>
    </div>
  );
}
