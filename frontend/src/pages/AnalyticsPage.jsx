import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { 
  ChartLineUp, 
  Play, 
  CurrencyDollar,
  Globe,
  TrendUp,
  Sparkle
} from '@phosphor-icons/react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';
import { toast } from 'sonner';

const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [insights, setInsights] = useState('');
  const [loading, setLoading] = useState(true);
  const [insightsLoading, setInsightsLoading] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/analytics/overview`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAIInsights = async () => {
    setInsightsLoading(true);
    try {
      const response = await axios.get(`${API}/ai/analytics-insights`);
      setInsights(response.data.insights);
      toast.success('AI insights generated!');
    } catch (error) {
      toast.error('Failed to generate insights');
    } finally {
      setInsightsLoading(false);
    }
  };

  const COLORS = ['#FF3B30', '#FFCC00', '#007AFF', '#22C55E', '#A855F7'];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#141414] border border-white/10 p-3 rounded-md">
          <p className="text-xs text-[#A1A1AA]">{label}</p>
          <p className="text-sm font-mono text-white">{payload[0].value.toLocaleString()}</p>
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

  const storeData = analytics?.streams_by_store 
    ? Object.entries(analytics.streams_by_store).map(([name, value]) => ({ name, value }))
    : [];

  const countryData = analytics?.streams_by_country
    ? Object.entries(analytics.streams_by_country).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="analytics-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Analytics</h1>
            <p className="text-[#A1A1AA] mt-1">Track your streaming performance</p>
          </div>
          <Button 
            onClick={fetchAIInsights}
            disabled={insightsLoading}
            className="bg-[#FFCC00] hover:bg-[#FFCC00]/90 text-black"
            data-testid="ai-insights-btn"
          >
            {insightsLoading ? (
              <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <Sparkle className="w-4 h-4 mr-2" />
                Get AI Insights
              </>
            )}
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#141414] border border-white/10 p-5 rounded-md">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-[#FF3B30]/10 rounded-md flex items-center justify-center text-[#FF3B30]">
                <Play className="w-5 h-5" />
              </div>
              <span className="text-xs text-[#22C55E] font-mono">+12.5%</span>
            </div>
            <p className="text-2xl font-bold font-mono">{analytics?.total_streams?.toLocaleString() || '0'}</p>
            <p className="text-sm text-[#A1A1AA] mt-1">Total Streams</p>
          </div>

          <div className="bg-[#141414] border border-white/10 p-5 rounded-md">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-[#22C55E]/10 rounded-md flex items-center justify-center text-[#22C55E]">
                <CurrencyDollar className="w-5 h-5" />
              </div>
              <span className="text-xs text-[#22C55E] font-mono">+8.2%</span>
            </div>
            <p className="text-2xl font-bold font-mono">${analytics?.total_earnings?.toFixed(2) || '0.00'}</p>
            <p className="text-sm text-[#A1A1AA] mt-1">Total Earnings</p>
          </div>

          <div className="bg-[#141414] border border-white/10 p-5 rounded-md">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-[#FFCC00]/10 rounded-md flex items-center justify-center text-[#FFCC00]">
                <TrendUp className="w-5 h-5" />
              </div>
            </div>
            <p className="text-2xl font-bold font-mono">{analytics?.total_downloads?.toLocaleString() || '0'}</p>
            <p className="text-sm text-[#A1A1AA] mt-1">Downloads</p>
          </div>

          <div className="bg-[#141414] border border-white/10 p-5 rounded-md">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-[#007AFF]/10 rounded-md flex items-center justify-center text-[#007AFF]">
                <Globe className="w-5 h-5" />
              </div>
            </div>
            <p className="text-2xl font-bold font-mono">{analytics?.release_count || '0'}</p>
            <p className="text-sm text-[#A1A1AA] mt-1">Releases</p>
          </div>
        </div>

        {/* AI Insights */}
        {insights && (
          <div className="bg-[#FFCC00]/10 border border-[#FFCC00]/30 rounded-md p-6">
            <h2 className="text-lg font-medium mb-4 flex items-center gap-2 text-[#FFCC00]">
              <Sparkle className="w-5 h-5" />
              AI Insights
            </h2>
            <div className="prose prose-invert max-w-none text-sm whitespace-pre-wrap">
              {insights}
            </div>
          </div>
        )}

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Streams Over Time */}
          <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
            <h2 className="text-lg font-medium mb-6 flex items-center gap-2">
              <ChartLineUp className="w-5 h-5 text-[#FF3B30]" />
              Streams Over Time
            </h2>
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

          {/* Streams by Platform */}
          <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
            <h2 className="text-lg font-medium mb-6">Streams by Platform</h2>
            <div className="h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={storeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {storeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-[#141414] border border-white/10 p-3 rounded-md">
                            <p className="text-xs text-[#A1A1AA]">{payload[0].name}</p>
                            <p className="text-sm font-mono text-white">{payload[0].value.toLocaleString()}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap justify-center gap-4 mt-4">
              {storeData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-2 text-xs">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                  <span className="text-[#A1A1AA]">{entry.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Streams by Country */}
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
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AnalyticsPage;
