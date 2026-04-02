import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Users, Globe, ChartLineUp, Clock, TrendUp, MusicNote, Lightning, CalendarBlank, MapPin, Rocket, Star, Target, ArrowRight, SpinnerGap, FloppyDisk, Trash, ArrowsLeftRight, X, CaretDown, CaretUp, BookmarkSimple, FilePdf } from '@phosphor-icons/react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { toast } from 'sonner';

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
  const [strategy, setStrategy] = useState(null);
  const [strategyLoading, setStrategyLoading] = useState(false);
  const [strategyError, setStrategyError] = useState(null);
  const [releaseTitle, setReleaseTitle] = useState('');
  const [genre, setGenre] = useState('');
  const [savedStrategies, setSavedStrategies] = useState([]);
  const [showSaved, setShowSaved] = useState(false);
  const [compareMode, setCompareMode] = useState(false);
  const [compareA, setCompareA] = useState(null);
  const [compareB, setCompareB] = useState(null);
  const [saving, setSaving] = useState(false);
  const [smartInsights, setSmartInsights] = useState([]);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [lastAnalyzed, setLastAnalyzed] = useState(null);

  useEffect(() => { fetchData(); fetchSavedStrategies(); fetchSmartInsights(); }, []);

  const fetchData = async () => {
    try {
      const res = await axios.get(`${API}/fan-analytics/overview`, { withCredentials: true });
      setData(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const fetchSavedStrategies = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/ai/strategies`, { withCredentials: true });
      setSavedStrategies(res.data.strategies || []);
    } catch (err) { console.error(err); }
  }, []);

  const fetchSmartInsights = async () => {
    try {
      const res = await axios.get(`${API}/ai/smart-insights`, { withCredentials: true });
      const insights = res.data.insights || [];
      setSmartInsights(insights);
      if (insights.length > 0) setLastAnalyzed(insights[0].created_at);
    } catch (err) { console.error(err); }
  };

  const generateSmartInsights = async () => {
    setInsightsLoading(true);
    try {
      const res = await axios.post(`${API}/ai/smart-insights`, {}, { withCredentials: true });
      const newInsights = res.data.insights || [];
      setSmartInsights(prev => [...newInsights, ...prev].slice(0, 20));
      setLastAnalyzed(res.data.generated_at);
      toast.success(`${newInsights.length} new insights generated!`);
    } catch (err) {
      console.error(err);
      toast.error('Failed to generate insights');
    } finally {
      setInsightsLoading(false);
    }
  };

  const generateStrategy = async () => {
    setStrategyLoading(true);
    setStrategyError(null);
    try {
      const res = await axios.post(`${API}/ai/release-strategy`, {
        release_title: releaseTitle || null,
        genre: genre || null,
      }, { withCredentials: true });
      setStrategy(res.data);
    } catch (err) {
      console.error(err);
      setStrategyError('Failed to generate strategy. Please try again.');
    } finally {
      setStrategyLoading(false);
    }
  };

  const saveStrategy = async (label) => {
    if (!strategy) return;
    setSaving(true);
    try {
      await axios.post(`${API}/ai/strategies/save`, {
        strategy: strategy.strategy,
        data_summary: strategy.data_summary,
        release_title: releaseTitle || null,
        genre: genre || null,
        label: label || null,
      }, { withCredentials: true });
      toast.success('Strategy saved!');
      fetchSavedStrategies();
    } catch (err) {
      console.error(err);
      toast.error('Failed to save strategy');
    } finally {
      setSaving(false);
    }
  };

  const deleteStrategy = async (id) => {
    try {
      await axios.delete(`${API}/ai/strategies/${id}`, { withCredentials: true });
      toast.success('Strategy deleted');
      setSavedStrategies(prev => prev.filter(s => s.id !== id));
      if (compareA?.id === id) setCompareA(null);
      if (compareB?.id === id) setCompareB(null);
    } catch (err) {
      toast.error('Failed to delete');
    }
  };

  const exportPdf = async (strategyData, dataSummary, title, genreVal, labelVal) => {
    try {
      const res = await axios.post(`${API}/ai/strategies/export-pdf`, {
        strategy: strategyData,
        data_summary: dataSummary,
        release_title: title || null,
        genre: genreVal || null,
        label: labelVal || null,
      }, { withCredentials: true, responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      const safeLabel = (labelVal || title || 'strategy').replace(/[^a-zA-Z0-9 _-]/g, '').replace(/\s+/g, '_');
      link.setAttribute('download', `Kalmori_Strategy_${safeLabel}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('PDF downloaded!');
    } catch (err) {
      console.error(err);
      toast.error('Failed to export PDF');
    }
  };

  const selectForCompare = (strat) => {
    if (!compareA) { setCompareA(strat); return; }
    if (compareA.id === strat.id) { setCompareA(null); return; }
    if (!compareB) { setCompareB(strat); return; }
    if (compareB.id === strat.id) { setCompareB(null); return; }
    setCompareB(strat);
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
              {data.top_countries?.slice(0, 8).map((c) => (
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

        {/* AI Smart Insights Section */}
        <div className="bg-gradient-to-br from-[#0a1628] to-[#111] border border-[#E040FB]/20 rounded-2xl p-6" data-testid="smart-insights-section">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center">
                <Lightning className="w-5 h-5 text-white" weight="fill" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Smart Insights</h2>
                <p className="text-xs text-gray-400">AI-powered growth coaching based on your streaming trends</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {lastAnalyzed && (
                <span className="text-[10px] text-gray-500 hidden sm:block">
                  Last analyzed {new Date(lastAnalyzed).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              )}
              <button
                onClick={generateSmartInsights}
                disabled={insightsLoading}
                className="px-4 py-2 bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white text-sm font-semibold rounded-lg hover:opacity-90 transition-opacity flex items-center gap-1.5 disabled:opacity-50"
                data-testid="analyze-trends-btn"
              >
                {insightsLoading ? (
                  <><SpinnerGap className="w-4 h-4 animate-spin" /> Analyzing...</>
                ) : (
                  <><Lightning className="w-4 h-4" weight="fill" /> Analyze Trends</>
                )}
              </button>
            </div>
          </div>

          {smartInsights.length === 0 && !insightsLoading && (
            <div className="text-center py-8">
              <Lightning className="w-8 h-8 text-gray-600 mx-auto mb-2" />
              <p className="text-sm text-gray-500">No insights yet. Click "Analyze Trends" to get AI-powered recommendations.</p>
            </div>
          )}

          {smartInsights.length > 0 && (
            <div className="space-y-3" data-testid="insights-list">
              {smartInsights.slice(0, 5).map((insight, i) => (
                <SmartInsightCard key={insight.id || i} insight={insight} />
              ))}
              {smartInsights.length > 5 && (
                <p className="text-xs text-gray-500 text-center pt-1">
                  + {smartInsights.length - 5} more insights in your notification bell
                </p>
              )}
            </div>
          )}
        </div>

        {/* AI Release Strategy Section */}
        <div className="bg-gradient-to-br from-[#1a0a2e] to-[#111] border border-[#7C4DFF]/30 rounded-2xl p-6" data-testid="ai-strategy-section">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#7C4DFF]/20 flex items-center justify-center">
                <Lightning className="w-5 h-5 text-[#7C4DFF]" weight="fill" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">AI Release Strategy</h2>
                <p className="text-xs text-gray-400">Get personalized release recommendations powered by your fan data</p>
              </div>
            </div>
            {savedStrategies.length > 0 && (
              <button
                onClick={() => { setShowSaved(!showSaved); setCompareMode(false); setCompareA(null); setCompareB(null); }}
                className="flex items-center gap-1.5 text-sm text-[#7C4DFF] hover:text-[#E040FB] transition-colors"
                data-testid="toggle-saved-btn"
              >
                <BookmarkSimple className="w-4 h-4" weight="fill" />
                Saved ({savedStrategies.length})
                {showSaved ? <CaretUp className="w-3 h-3" /> : <CaretDown className="w-3 h-3" />}
              </button>
            )}
          </div>

          {/* Generate Form */}
          {!strategy && !showSaved && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Upcoming Release Title (optional)</label>
                  <input
                    type="text" value={releaseTitle} onChange={e => setReleaseTitle(e.target.value)}
                    placeholder="e.g. My New Single"
                    className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:border-[#7C4DFF]/50 focus:outline-none transition-colors"
                    data-testid="strategy-release-title"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Target Genre (optional)</label>
                  <input
                    type="text" value={genre} onChange={e => setGenre(e.target.value)}
                    placeholder="e.g. Hip-Hop, R&B"
                    className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 focus:border-[#7C4DFF]/50 focus:outline-none transition-colors"
                    data-testid="strategy-genre"
                  />
                </div>
              </div>
              <button
                onClick={generateStrategy} disabled={strategyLoading}
                className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white font-semibold rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50"
                data-testid="generate-strategy-btn"
              >
                {strategyLoading ? (
                  <><SpinnerGap className="w-5 h-5 animate-spin" /> Analyzing your audience data...</>
                ) : (
                  <><Rocket className="w-5 h-5" /> Generate AI Strategy</>
                )}
              </button>
              {strategyError && <p className="text-red-400 text-sm" data-testid="strategy-error">{strategyError}</p>}
            </div>
          )}

          {/* Current Strategy Results */}
          {strategy && !showSaved && (
            <AIStrategyResults
              strategy={strategy}
              onReset={() => setStrategy(null)}
              onSave={saveStrategy}
              saving={saving}
              onExport={() => exportPdf(strategy.strategy, strategy.data_summary, releaseTitle, genre, null)}
            />
          )}

          {/* Saved Strategies Panel */}
          {showSaved && (
            <SavedStrategiesPanel
              strategies={savedStrategies}
              onDelete={deleteStrategy}
              onExport={(strat) => exportPdf(strat.strategy, strat.data_summary, strat.release_title, strat.genre, strat.label)}
              compareMode={compareMode}
              setCompareMode={setCompareMode}
              compareA={compareA}
              compareB={compareB}
              selectForCompare={selectForCompare}
              setCompareA={setCompareA}
              setCompareB={setCompareB}
            />
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

/* ===================== STRATEGY RESULTS ===================== */
function AIStrategyResults({ strategy, onReset, onSave, saving, onExport }) {
  const s = strategy.strategy;
  const summary = strategy.data_summary;
  const [label, setLabel] = useState('');
  const [showSaveInput, setShowSaveInput] = useState(false);

  const priorityColor = (p) => {
    if (p === 'high') return 'text-green-400 bg-green-400/10';
    if (p === 'medium') return 'text-yellow-400 bg-yellow-400/10';
    return 'text-gray-400 bg-gray-400/10';
  };

  return (
    <div className="space-y-5" data-testid="strategy-results">
      {summary && <DataSummaryBar summary={summary} />}
      <StrategyContent s={s} priorityColor={priorityColor} />

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-3 pt-2">
        {!showSaveInput ? (
          <button
            onClick={() => setShowSaveInput(true)}
            className="px-4 py-2 bg-[#7C4DFF]/10 border border-[#7C4DFF]/30 text-[#7C4DFF] rounded-lg text-sm font-medium hover:bg-[#7C4DFF]/20 transition-colors flex items-center gap-2"
            data-testid="save-strategy-btn"
          >
            <FloppyDisk className="w-4 h-4" /> Save Strategy
          </button>
        ) : (
          <div className="flex items-center gap-2 flex-1 sm:flex-none" data-testid="save-strategy-form">
            <input
              type="text" value={label} onChange={e => setLabel(e.target.value)}
              placeholder="Label (e.g. Hip-Hop Q2 Plan)"
              className="bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-[#7C4DFF]/50 focus:outline-none w-52"
              data-testid="save-strategy-label"
            />
            <button
              onClick={() => { onSave(label); setShowSaveInput(false); setLabel(''); }}
              disabled={saving}
              className="px-4 py-2 bg-[#7C4DFF] text-white rounded-lg text-sm font-medium hover:bg-[#7C4DFF]/80 transition-colors flex items-center gap-1 disabled:opacity-50"
              data-testid="confirm-save-btn"
            >
              {saving ? <SpinnerGap className="w-4 h-4 animate-spin" /> : <FloppyDisk className="w-4 h-4" />}
              Save
            </button>
            <button onClick={() => setShowSaveInput(false)} className="text-gray-500 hover:text-gray-300">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
        <button
          onClick={onReset}
          className="text-sm text-gray-400 hover:text-[#E040FB] transition-colors flex items-center gap-1"
          data-testid="regenerate-strategy-btn"
        >
          <Lightning className="w-4 h-4" /> New Strategy
        </button>
        <button
          onClick={onExport}
          className="px-4 py-2 bg-[#E040FB]/10 border border-[#E040FB]/30 text-[#E040FB] rounded-lg text-sm font-medium hover:bg-[#E040FB]/20 transition-colors flex items-center gap-2"
          data-testid="export-pdf-btn"
        >
          <FilePdf className="w-4 h-4" /> Export PDF
        </button>
      </div>
    </div>
  );
}

/* ===================== SAVED STRATEGIES PANEL ===================== */
function SavedStrategiesPanel({ strategies, onDelete, onExport, compareMode, setCompareMode, compareA, compareB, selectForCompare, setCompareA, setCompareB }) {
  if (strategies.length === 0) {
    return <p className="text-gray-500 text-sm py-4">No saved strategies yet. Generate and save one above.</p>;
  }

  return (
    <div className="space-y-4" data-testid="saved-strategies-panel">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-400">{strategies.length} saved {strategies.length === 1 ? 'strategy' : 'strategies'}</p>
        {strategies.length >= 2 && (
          <button
            onClick={() => { setCompareMode(!compareMode); setCompareA(null); setCompareB(null); }}
            className={`flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg transition-colors ${compareMode ? 'bg-[#E040FB]/20 text-[#E040FB] border border-[#E040FB]/30' : 'text-gray-400 hover:text-white border border-white/10 hover:border-white/20'}`}
            data-testid="compare-toggle-btn"
          >
            <ArrowsLeftRight className="w-4 h-4" />
            {compareMode ? 'Cancel Compare' : 'Compare'}
          </button>
        )}
      </div>

      {compareMode && (
        <p className="text-xs text-[#E040FB]">
          {!compareA ? 'Select the first strategy to compare' : !compareB ? 'Now select the second strategy' : 'Comparing two strategies below'}
        </p>
      )}

      {/* Strategy Cards */}
      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
        {strategies.map(strat => {
          const isSelectedA = compareA?.id === strat.id;
          const isSelectedB = compareB?.id === strat.id;
          const isSelected = isSelectedA || isSelectedB;
          return (
            <div
              key={strat.id}
              className={`bg-[#0a0a0a] border rounded-xl p-4 transition-colors ${isSelected ? 'border-[#E040FB]/50 bg-[#E040FB]/5' : 'border-white/10 hover:border-white/20'}`}
              data-testid={`saved-strategy-${strat.id}`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-semibold text-white truncate">{strat.label}</h4>
                    {isSelectedA && <span className="text-[10px] bg-[#7C4DFF] text-white px-1.5 py-0.5 rounded">A</span>}
                    {isSelectedB && <span className="text-[10px] bg-[#E040FB] text-white px-1.5 py-0.5 rounded">B</span>}
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                    <span>{new Date(strat.created_at).toLocaleDateString()}</span>
                    {strat.release_title && <span>| {strat.release_title}</span>}
                    {strat.genre && <span>| {strat.genre}</span>}
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2 text-xs">
                    <span className="text-[#7C4DFF]">{strat.strategy?.optimal_release_day}</span>
                    <span className="text-gray-600">|</span>
                    <span className="text-[#E040FB]">{strat.strategy?.optimal_release_time}</span>
                    {strat.data_summary?.total_streams > 0 && (
                      <><span className="text-gray-600">|</span><span className="text-gray-400">{strat.data_summary.total_streams.toLocaleString()} streams</span></>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {compareMode && (
                    <button
                      onClick={() => selectForCompare(strat)}
                      className={`p-1.5 rounded-lg transition-colors ${isSelected ? 'text-[#E040FB]' : 'text-gray-500 hover:text-white'}`}
                      data-testid={`compare-select-${strat.id}`}
                    >
                      <ArrowsLeftRight className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => onExport(strat)}
                    className="p-1.5 text-gray-600 hover:text-[#E040FB] rounded-lg transition-colors"
                    data-testid={`export-strategy-${strat.id}`}
                    title="Export as PDF"
                  >
                    <FilePdf className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onDelete(strat.id)}
                    className="p-1.5 text-gray-600 hover:text-red-400 rounded-lg transition-colors"
                    data-testid={`delete-strategy-${strat.id}`}
                  >
                    <Trash className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Compare View */}
      {compareMode && compareA && compareB && (
        <CompareView a={compareA} b={compareB} />
      )}
    </div>
  );
}

/* ===================== COMPARE VIEW ===================== */
function CompareView({ a, b }) {
  const priorityColor = (p) => {
    if (p === 'high') return 'text-green-400';
    if (p === 'medium') return 'text-yellow-400';
    return 'text-gray-400';
  };

  const diff = (valA, valB) => {
    if (valA === valB) return 'text-gray-400';
    return 'text-[#E040FB]';
  };

  return (
    <div className="mt-4 space-y-4" data-testid="compare-view">
      <div className="flex items-center gap-2 text-sm font-semibold text-white">
        <ArrowsLeftRight className="w-5 h-5 text-[#E040FB]" />
        Strategy Comparison
      </div>

      {/* Header */}
      <div className="grid grid-cols-3 gap-2 text-xs">
        <div className="text-gray-500 font-medium" />
        <div className="bg-[#7C4DFF]/10 border border-[#7C4DFF]/20 rounded-lg p-2 text-center">
          <span className="text-[#7C4DFF] font-semibold">A: </span>
          <span className="text-gray-300 truncate">{a.label}</span>
          <p className="text-gray-600 mt-0.5">{new Date(a.created_at).toLocaleDateString()}</p>
        </div>
        <div className="bg-[#E040FB]/10 border border-[#E040FB]/20 rounded-lg p-2 text-center">
          <span className="text-[#E040FB] font-semibold">B: </span>
          <span className="text-gray-300 truncate">{b.label}</span>
          <p className="text-gray-600 mt-0.5">{new Date(b.created_at).toLocaleDateString()}</p>
        </div>
      </div>

      {/* Release Window */}
      <CompareRow
        label="Best Day"
        valA={a.strategy?.optimal_release_day}
        valB={b.strategy?.optimal_release_day}
        diff={diff}
      />
      <CompareRow
        label="Best Time"
        valA={a.strategy?.optimal_release_time}
        valB={b.strategy?.optimal_release_time}
        diff={diff}
      />
      <CompareRow
        label="Streams Analyzed"
        valA={a.data_summary?.total_streams?.toLocaleString()}
        valB={b.data_summary?.total_streams?.toLocaleString()}
        diff={diff}
      />
      <CompareRow
        label="Top Platform"
        valA={a.data_summary?.top_platform || 'N/A'}
        valB={b.data_summary?.top_platform || 'N/A'}
        diff={diff}
      />
      <CompareRow
        label="Top Country"
        valA={a.data_summary?.top_country || 'N/A'}
        valB={b.data_summary?.top_country || 'N/A'}
        diff={diff}
      />
      <CompareRow
        label="Est. First Week"
        valA={a.strategy?.estimated_first_week_range || 'N/A'}
        valB={b.strategy?.estimated_first_week_range || 'N/A'}
        diff={diff}
      />

      {/* Platform Priorities */}
      <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-4">
        <h4 className="text-xs font-semibold text-gray-400 mb-3">Platform Priorities</h4>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div />
          <div className="space-y-1">
            {(a.strategy?.target_platforms || []).map((p, i) => (
              <div key={i} className="flex items-center gap-1">
                <span className={priorityColor(p.priority)}>{p.priority}</span>
                <span className="text-gray-300">{p.platform}</span>
              </div>
            ))}
          </div>
          <div className="space-y-1">
            {(b.strategy?.target_platforms || []).map((p, i) => (
              <div key={i} className="flex items-center gap-1">
                <span className={priorityColor(p.priority)}>{p.priority}</span>
                <span className="text-gray-300">{p.platform}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Timeline Comparison */}
      <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-4">
        <h4 className="text-xs font-semibold text-gray-400 mb-3">Pre-Release Timeline Steps</h4>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div />
          <div className="text-center">
            <span className="text-[#7C4DFF] font-bold">{a.strategy?.pre_release_timeline?.length || 0}</span>
            <span className="text-gray-500 ml-1">steps</span>
          </div>
          <div className="text-center">
            <span className="text-[#E040FB] font-bold">{b.strategy?.pre_release_timeline?.length || 0}</span>
            <span className="text-gray-500 ml-1">steps</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function CompareRow({ label, valA, valB, diff }) {
  return (
    <div className="grid grid-cols-3 gap-2 text-xs items-center" data-testid={`compare-row-${label.toLowerCase().replace(/\s+/g, '-')}`}>
      <span className="text-gray-500 font-medium">{label}</span>
      <span className={`text-center font-semibold ${diff(valA, valB)}`}>{valA}</span>
      <span className={`text-center font-semibold ${diff(valA, valB)}`}>{valB}</span>
    </div>
  );
}

/* ===================== SHARED COMPONENTS ===================== */
function DataSummaryBar({ summary }) {
  return (
    <div className="flex flex-wrap gap-3 text-xs">
      {summary.total_streams > 0 && (
        <span className="bg-[#7C4DFF]/10 text-[#7C4DFF] px-3 py-1 rounded-full">{summary.total_streams.toLocaleString()} streams analyzed</span>
      )}
      {summary.top_platform && (
        <span className="bg-[#1DB954]/10 text-[#1DB954] px-3 py-1 rounded-full">Top: {summary.top_platform}</span>
      )}
      {summary.top_country && (
        <span className="bg-[#E040FB]/10 text-[#E040FB] px-3 py-1 rounded-full">Top Market: {summary.top_country}</span>
      )}
      {summary.peak_hour !== null && summary.peak_hour !== undefined && (
        <span className="bg-[#FFD700]/10 text-[#FFD700] px-3 py-1 rounded-full">Peak: {summary.peak_hour}:00 UTC</span>
      )}
    </div>
  );
}

function StrategyContent({ s, priorityColor }) {
  return (
    <>
      {/* Optimal Release Timing */}
      <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <CalendarBlank className="w-5 h-5 text-[#7C4DFF]" />
          <h3 className="font-semibold text-white">Optimal Release Window</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-3">
          <div className="bg-[#7C4DFF]/5 border border-[#7C4DFF]/20 rounded-lg p-3">
            <p className="text-xs text-gray-400">Best Day</p>
            <p className="text-lg font-bold text-[#7C4DFF]" data-testid="optimal-day">{s.optimal_release_day}</p>
          </div>
          <div className="bg-[#E040FB]/5 border border-[#E040FB]/20 rounded-lg p-3">
            <p className="text-xs text-gray-400">Best Time</p>
            <p className="text-lg font-bold text-[#E040FB]" data-testid="optimal-time">{s.optimal_release_time}</p>
          </div>
        </div>
        <p className="text-sm text-gray-300">{s.release_day_reasoning}</p>
      </div>

      {/* Target Platforms */}
      {s.target_platforms?.length > 0 && (
        <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-5 h-5 text-[#1DB954]" />
            <h3 className="font-semibold text-white">Platform Strategy</h3>
          </div>
          <div className="space-y-3">
            {s.target_platforms.map((p, i) => (
              <div key={i} className="flex items-start gap-3 bg-[#111] border border-white/5 rounded-lg p-3" data-testid={`platform-strategy-${i}`}>
                <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full mt-0.5 ${priorityColor(p.priority)}`}>{p.priority}</span>
                <div>
                  <p className="text-sm font-semibold text-white">{p.platform}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{p.tactic}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Geographic Strategy */}
      {s.geographic_strategy?.length > 0 && (
        <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <MapPin className="w-5 h-5 text-[#E040FB]" />
            <h3 className="font-semibold text-white">Geographic Targeting</h3>
          </div>
          <div className="space-y-2">
            {s.geographic_strategy.map((g, i) => (
              <div key={i} className="flex items-start gap-2" data-testid={`geo-strategy-${i}`}>
                <ArrowRight className="w-4 h-4 text-[#E040FB] mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-sm font-medium text-white">{g.region}:</span>
                  <span className="text-sm text-gray-400 ml-1">{g.tactic}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pre-Release Timeline */}
      {s.pre_release_timeline?.length > 0 && (
        <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Rocket className="w-5 h-5 text-[#FFD700]" />
            <h3 className="font-semibold text-white">Pre-Release Timeline</h3>
          </div>
          <div className="relative">
            <div className="absolute left-[18px] top-2 bottom-2 w-px bg-gradient-to-b from-[#7C4DFF] via-[#E040FB] to-[#FFD700]" />
            <div className="space-y-4">
              {[...s.pre_release_timeline].sort((a, b) => b.days_before - a.days_before).map((t, i) => (
                <div key={i} className="flex items-start gap-4 pl-1" data-testid={`timeline-${i}`}>
                  <div className="w-9 h-9 rounded-full bg-[#1a1a1a] border-2 border-[#7C4DFF] flex items-center justify-center flex-shrink-0 z-10">
                    <span className="text-[10px] font-bold text-[#7C4DFF]">
                      {t.days_before === 0 ? 'D' : `-${t.days_before}`}
                    </span>
                  </div>
                  <div className="pt-1.5">
                    <p className="text-xs text-gray-500 font-mono">{t.days_before === 0 ? 'Release Day' : `${t.days_before} days before`}</p>
                    <p className="text-sm text-white">{t.action}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Promotion Tips */}
      {s.promotion_tips?.length > 0 && (
        <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Star className="w-5 h-5 text-[#FFD700]" weight="fill" />
            <h3 className="font-semibold text-white">Promotion Tips</h3>
          </div>
          <ul className="space-y-2">
            {s.promotion_tips.map((tip, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300" data-testid={`promo-tip-${i}`}>
                <span className="text-[#FFD700] mt-1 flex-shrink-0">*</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Estimated Range + Confidence */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {s.estimated_first_week_range && (
          <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-4">
            <p className="text-xs text-gray-400 mb-1">Estimated First Week</p>
            <p className="text-base font-bold text-white" data-testid="estimated-range">{s.estimated_first_week_range}</p>
          </div>
        )}
        {s.confidence_note && (
          <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-4">
            <p className="text-xs text-gray-400 mb-1">Confidence Note</p>
            <p className="text-xs text-gray-300" data-testid="confidence-note">{s.confidence_note}</p>
          </div>
        )}
      </div>
    </>
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

const CATEGORY_CONFIG = {
  growth: { color: '#1DB954', label: 'Growth' },
  geographic: { color: '#E040FB', label: 'Geographic' },
  platform: { color: '#7C4DFF', label: 'Platform' },
  timing: { color: '#FFD700', label: 'Timing' },
  campaign: { color: '#FF6B6B', label: 'Campaign' },
};

function SmartInsightCard({ insight }) {
  const cat = CATEGORY_CONFIG[insight.category] || CATEGORY_CONFIG.growth;
  const priorityBorder = insight.priority === 'high' ? 'border-l-green-400' : insight.priority === 'medium' ? 'border-l-yellow-400' : 'border-l-gray-500';

  return (
    <div
      className={`bg-[#0a0a0a] border border-white/10 rounded-xl p-4 border-l-4 ${priorityBorder} hover:bg-white/[0.02] transition-colors`}
      data-testid={`insight-card-${insight.id || ''}`}
    >
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full" style={{ color: cat.color, backgroundColor: `${cat.color}15` }}>
              {cat.label}
            </span>
            {insight.metric_value && (
              <span className="text-[10px] font-bold text-[#FFD700] bg-[#FFD700]/10 px-2 py-0.5 rounded-full">{insight.metric_value}</span>
            )}
            <span className={`text-[10px] font-bold uppercase ${insight.priority === 'high' ? 'text-green-400' : insight.priority === 'medium' ? 'text-yellow-400' : 'text-gray-500'}`}>
              {insight.priority}
            </span>
          </div>
          <p className="text-sm text-white leading-snug">{insight.message}</p>
          {insight.action_suggestion && (
            <p className="text-xs text-[#7C4DFF] mt-1.5 flex items-center gap-1">
              <ArrowRight className="w-3 h-3 flex-shrink-0" />
              {insight.action_suggestion}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
