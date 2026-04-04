import React, { useState, useEffect, useCallback } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Users, Gift, Trophy, ArrowUp } from '@phosphor-icons/react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function AdminReferralsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/admin/referral/overview`, { headers });
      if (res.ok) setData(await res.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <AdminLayout><div className="flex items-center justify-center h-64 text-gray-500">Loading...</div></AdminLayout>;

  return (
    <AdminLayout>
      <div className="max-w-4xl mx-auto space-y-6" data-testid="admin-referrals">
        <div>
          <h1 className="text-2xl font-bold text-white" data-testid="admin-referrals-title">Referral Program</h1>
          <p className="text-gray-400 text-sm mt-1">Overview of all referral activity</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#111] border border-[#222] rounded-xl p-5" data-testid="total-referrals">
            <div className="flex items-center gap-3">
              <Users className="w-8 h-8 text-[#7C4DFF]" />
              <div>
                <p className="text-3xl font-bold text-white">{data?.total_referrals || 0}</p>
                <p className="text-sm text-gray-500">Total Referral Sign-ups</p>
              </div>
            </div>
          </div>
          <div className="bg-[#111] border border-[#222] rounded-xl p-5" data-testid="total-referrers">
            <div className="flex items-center gap-3">
              <Gift className="w-8 h-8 text-[#E040FB]" />
              <div>
                <p className="text-3xl font-bold text-white">{data?.total_referrers || 0}</p>
                <p className="text-sm text-gray-500">Active Referrers</p>
              </div>
            </div>
          </div>
        </div>

        {/* Top Referrers */}
        <div className="bg-[#111] border border-[#222] rounded-xl overflow-hidden" data-testid="top-referrers">
          <div className="p-4 border-b border-[#222]">
            <h3 className="text-white font-semibold flex items-center gap-2">
              <Trophy className="w-5 h-5 text-[#FFD700]" /> Top Referrers
            </h3>
          </div>
          {data?.top_referrers?.length > 0 ? (
            <div className="divide-y divide-[#1a1a1a]">
              {data.top_referrers.map((ref, i) => (
                <div key={ref.id} className="flex items-center gap-4 px-4 py-3">
                  <span className={`w-6 text-center font-bold ${i === 0 ? 'text-[#FFD700]' : i === 1 ? 'text-gray-300' : i === 2 ? 'text-amber-600' : 'text-gray-500'}`}>
                    #{i + 1}
                  </span>
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium">{ref.artist_name || ref.email}</p>
                    <p className="text-xs text-gray-500">{ref.email}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-bold">{ref.successful_referrals}</p>
                    <p className="text-xs text-gray-500">referrals</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[#E040FB] font-bold">{ref.rewards_earned}</p>
                    <p className="text-xs text-gray-500">months earned</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500 text-sm">No referrals yet</div>
          )}
        </div>

        {/* Recent Sign-ups */}
        <div className="bg-[#111] border border-[#222] rounded-xl overflow-hidden" data-testid="recent-signups">
          <div className="p-4 border-b border-[#222]">
            <h3 className="text-white font-semibold flex items-center gap-2">
              <ArrowUp className="w-5 h-5 text-[#22C55E]" /> Recent Referral Sign-ups
            </h3>
          </div>
          {data?.recent_signups?.length > 0 ? (
            <div className="divide-y divide-[#1a1a1a]">
              {data.recent_signups.map(s => (
                <div key={s.id} className="flex items-center justify-between px-4 py-3">
                  <div>
                    <p className="text-white text-sm">{s.referred_name || 'User'}</p>
                    <p className="text-xs text-gray-500">{s.referred_email}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">via <span className="text-[#7C4DFF] font-mono">{s.referral_code}</span></p>
                    <p className="text-xs text-gray-500">{new Date(s.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500 text-sm">No referral sign-ups yet</div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
}
