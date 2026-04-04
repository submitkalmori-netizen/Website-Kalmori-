import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { CurrencyDollar, MusicNote, User, ArrowRight, ChartLineUp, TrendUp, Wallet } from '@phosphor-icons/react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const LICENSE_COLORS = {
  basic_lease: '#7C4DFF', premium_lease: '#E040FB', unlimited_lease: '#FF4081', exclusive: '#FFD700',
};

export default function RoyaltySplitsPage() {
  const [splits, setSplits] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedSplit, setExpandedSplit] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [splitsRes, summaryRes] = await Promise.all([
          axios.get(`${API}/api/royalty-splits`, { withCredentials: true }),
          axios.get(`${API}/api/royalty-splits/summary`, { withCredentials: true }),
        ]);
        setSplits(splitsRes.data.splits || []);
        setSummary(summaryRes.data);
      } catch (err) { console.error(err); }
      setLoading(false);
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="royalty-splits-page">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white">Royalty Splits</h1>
          <p className="text-gray-500 text-sm mt-1">Track revenue distribution from beat licenses</p>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <ChartLineUp className="w-4 h-4 text-[#7C4DFF]" />
                <p className="text-xs text-gray-500">Active Splits</p>
              </div>
              <p className="text-2xl font-bold text-white" data-testid="active-splits-count">{summary.active_splits}</p>
            </div>
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendUp className="w-4 h-4 text-[#E040FB]" />
                <p className="text-xs text-gray-500">Earned as Producer</p>
              </div>
              <p className="text-2xl font-bold text-[#E040FB]" data-testid="earned-as-producer">${summary.total_as_producer.toFixed(2)}</p>
            </div>
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <MusicNote className="w-4 h-4 text-[#7C4DFF]" />
                <p className="text-xs text-gray-500">Earned as Artist</p>
              </div>
              <p className="text-2xl font-bold text-[#7C4DFF]" data-testid="earned-as-artist">${summary.total_as_artist.toFixed(2)}</p>
            </div>
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Wallet className="w-4 h-4 text-[#4CAF50]" />
                <p className="text-xs text-gray-500">Total Earned</p>
              </div>
              <p className="text-2xl font-bold text-[#4CAF50]" data-testid="total-earned">${summary.total_earned.toFixed(2)}</p>
            </div>
          </div>
        )}

        {/* Active Splits */}
        {splits.length === 0 ? (
          <div className="bg-[#111] border border-white/10 rounded-xl p-12 text-center">
            <CurrencyDollar className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400 font-medium">No royalty splits yet</p>
            <p className="text-gray-600 text-sm mt-1">Splits are automatically created when beats are licensed through the marketplace</p>
          </div>
        ) : (
          <div className="space-y-3">
            <h2 className="text-sm font-bold text-[#E040FB] tracking-[2px]">ACTIVE SPLITS</h2>
            {splits.map(split => {
              const licColor = LICENSE_COLORS[split.license_type] || '#7C4DFF';
              const expanded = expandedSplit === split.id;
              return (
                <div key={split.id} className="bg-[#111] border border-white/10 rounded-xl overflow-hidden" data-testid={`split-${split.id}`}>
                  <button onClick={() => setExpandedSplit(expanded ? null : split.id)}
                    className="w-full p-4 flex items-center gap-4 text-left hover:bg-white/[0.02] transition">
                    {/* Beat Icon */}
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center shrink-0" style={{ backgroundColor: `${licColor}15` }}>
                      <MusicNote className="w-6 h-6" style={{ color: licColor }} />
                    </div>
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-semibold text-sm truncate">{split.beat_title}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold" style={{ backgroundColor: `${licColor}20`, color: licColor }}>
                          {split.license_type?.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">
                          {split.is_producer ? 'You are producer' : 'You are artist'}
                        </span>
                      </div>
                    </div>
                    {/* Split Visual */}
                    <div className="hidden sm:flex items-center gap-2 shrink-0">
                      <div className="text-center">
                        <p className="text-xs text-gray-500">Producer</p>
                        <p className="text-sm font-bold text-[#E040FB]">{split.producer_split}%</p>
                      </div>
                      <div className="w-20 h-2 rounded-full bg-[#1a1a1a] overflow-hidden flex">
                        <div className="h-full bg-[#E040FB] rounded-l-full" style={{ width: `${split.producer_split}%` }} />
                        <div className="h-full bg-[#7C4DFF] rounded-r-full" style={{ width: `${split.artist_split}%` }} />
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-500">Artist</p>
                        <p className="text-sm font-bold text-[#7C4DFF]">{split.artist_split}%</p>
                      </div>
                    </div>
                    {/* Total Earned */}
                    <div className="text-right shrink-0">
                      <p className="text-lg font-bold text-white">${split.total_earned.toFixed(2)}</p>
                      <p className="text-[10px] text-gray-500">your share</p>
                    </div>
                    <ArrowRight className={`w-4 h-4 text-gray-500 shrink-0 transition-transform ${expanded ? 'rotate-90' : ''}`} />
                  </button>
                  {/* Expanded Details */}
                  {expanded && (
                    <div className="border-t border-[#222] p-4 bg-[#0a0a0a]">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                        <div>
                          <p className="text-[10px] text-gray-500 mb-0.5">Producer</p>
                          <p className="text-sm text-white">{split.producer_name}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-gray-500 mb-0.5">Artist</p>
                          <p className="text-sm text-white">{split.artist_name}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-gray-500 mb-0.5">Status</p>
                          <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            split.status === 'active' ? 'bg-[#4CAF50]/15 text-[#4CAF50]' : 'bg-[#FFD700]/15 text-[#FFD700]'
                          }`}>{split.status?.toUpperCase()}</span>
                        </div>
                        <div>
                          <p className="text-[10px] text-gray-500 mb-0.5">Contract</p>
                          <p className="text-xs text-gray-400 font-mono">{split.contract_id || 'N/A'}</p>
                        </div>
                      </div>
                      {/* Earnings History */}
                      {split.earnings_history?.length > 0 ? (
                        <div>
                          <p className="text-xs font-bold text-gray-500 tracking-wider mb-2">EARNINGS HISTORY</p>
                          <div className="space-y-1.5">
                            {split.earnings_history.map(e => (
                              <div key={e.id} className="flex items-center justify-between py-2 px-3 bg-[#111] rounded-lg">
                                <span className="text-xs text-gray-400">{e.period}</span>
                                <span className="text-xs text-gray-500">{e.streams?.toLocaleString()} streams</span>
                                <span className="text-xs text-gray-500">${e.gross_revenue?.toFixed(2)} gross</span>
                                <span className="text-sm font-bold text-[#4CAF50]">${e.amount?.toFixed(2)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-gray-600 text-center py-4">No earnings distributed yet. Splits are calculated monthly.</p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* How It Works */}
        <div className="bg-[#111] border border-white/10 rounded-xl p-5">
          <h3 className="text-sm font-bold text-white mb-3">How Royalty Splits Work</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-[#7C4DFF]/15 flex items-center justify-center shrink-0">
                <span className="text-[#7C4DFF] text-xs font-bold">1</span>
              </div>
              <div>
                <p className="text-xs font-medium text-white">Beat Licensed</p>
                <p className="text-[11px] text-gray-500">When an artist purchases a beat license, a royalty split is auto-created based on the license type.</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-[#E040FB]/15 flex items-center justify-center shrink-0">
                <span className="text-[#E040FB] text-xs font-bold">2</span>
              </div>
              <div>
                <p className="text-xs font-medium text-white">Revenue Tracked</p>
                <p className="text-[11px] text-gray-500">Streaming revenue from releases using the beat is tracked and allocated based on split percentages.</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-[#4CAF50]/15 flex items-center justify-center shrink-0">
                <span className="text-[#4CAF50] text-xs font-bold">3</span>
              </div>
              <div>
                <p className="text-xs font-medium text-white">Auto-Distributed</p>
                <p className="text-[11px] text-gray-500">Each month, earnings are calculated and credited to both parties' wallets automatically.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
