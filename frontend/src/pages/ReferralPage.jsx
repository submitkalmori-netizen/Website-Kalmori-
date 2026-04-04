import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Link as LinkIcon, Copy, CheckCircle, Users, Gift, Trophy, ArrowRight, ShareNetwork } from '@phosphor-icons/react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

export default function ReferralPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  const token = localStorage.getItem('token') || localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    try {
      const [linkRes, statsRes] = await Promise.all([
        fetch(`${API}/api/referral/my-link`, { headers }),
        fetch(`${API}/api/referral/stats`, { headers }),
      ]);
      const linkData = await linkRes.json();
      const statsData = await statsRes.json();
      setData({ ...linkData, ...statsData });
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const referralLink = data?.referral_code
    ? `${window.location.origin}/register?ref=${data.referral_code}`
    : '';

  const copyLink = () => {
    navigator.clipboard.writeText(referralLink);
    setCopied(true);
    toast.success('Referral link copied!');
    setTimeout(() => setCopied(false), 3000);
  };

  const copyCode = () => {
    navigator.clipboard.writeText(data?.referral_code || '');
    toast.success('Referral code copied!');
  };

  const shareLink = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Join Kalmori',
        text: 'Distribute your music to 150+ platforms. Use my referral link to get a free month of Rise!',
        url: referralLink,
      });
    } else {
      copyLink();
    }
  };

  if (loading) return (
    <DashboardLayout>
      <div className="flex items-center justify-center h-64 text-gray-500">Loading...</div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto space-y-6" data-testid="referral-page">
        <div>
          <h1 className="text-2xl font-bold text-white" data-testid="referral-title">Referral Program</h1>
          <p className="text-gray-400 text-sm mt-1">Invite friends and both earn a free month of Rise!</p>
        </div>

        {/* Hero Banner */}
        <div className="bg-gradient-to-br from-[#7C4DFF]/20 to-[#E040FB]/20 border border-[#7C4DFF]/30 rounded-2xl p-6 text-center" data-testid="referral-hero">
          <Gift className="w-12 h-12 text-[#E040FB] mx-auto mb-3" weight="fill" />
          <h2 className="text-xl font-bold text-white mb-2">Give a Month, Get a Month</h2>
          <p className="text-gray-300 text-sm max-w-md mx-auto mb-4">
            Share your unique link. When someone signs up, <strong className="text-[#E040FB]">you both get a free month of Rise</strong> — unlimited releases, advanced analytics, and priority support.
          </p>
          <div className="flex items-center gap-2 max-w-lg mx-auto">
            <div className="flex-1 bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-sm font-mono text-gray-300 truncate" data-testid="referral-link-display">
              {referralLink}
            </div>
            <button
              onClick={copyLink}
              className="px-4 py-3 rounded-lg bg-[#7C4DFF] text-white text-sm font-medium hover:brightness-110 flex items-center gap-2 whitespace-nowrap"
              data-testid="copy-link-btn"
            >
              {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button
              onClick={shareLink}
              className="px-4 py-3 rounded-lg bg-[#E040FB] text-white text-sm font-medium hover:brightness-110 flex items-center gap-2"
              data-testid="share-btn"
            >
              <ShareNetwork className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Code Display */}
        <div className="bg-[#111] border border-[#222] rounded-xl p-5 flex items-center justify-between" data-testid="referral-code-card">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-[#7C4DFF] mb-1">Your Referral Code</p>
            <p className="text-2xl font-mono font-black text-white tracking-[4px]" data-testid="referral-code">{data?.referral_code}</p>
          </div>
          <button onClick={copyCode} className="text-gray-500 hover:text-white transition" data-testid="copy-code-btn">
            <Copy className="w-5 h-5" />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-[#111] border border-[#222] rounded-xl p-5 text-center" data-testid="stat-referrals">
            <Users className="w-6 h-6 text-[#7C4DFF] mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">{data?.total_referrals || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Total Referrals</p>
          </div>
          <div className="bg-[#111] border border-[#222] rounded-xl p-5 text-center" data-testid="stat-successful">
            <CheckCircle className="w-6 h-6 text-[#22C55E] mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">{data?.successful_referrals || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Successful</p>
          </div>
          <div className="bg-[#111] border border-[#222] rounded-xl p-5 text-center" data-testid="stat-rewards">
            <Gift className="w-6 h-6 text-[#E040FB] mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">{data?.rewards_earned || 0}</p>
            <p className="text-xs text-gray-500 mt-1">Months Earned</p>
          </div>
        </div>

        {/* Referred Users */}
        {data?.referred_users?.length > 0 && (
          <div className="bg-[#111] border border-[#222] rounded-xl overflow-hidden" data-testid="referred-users">
            <div className="p-4 border-b border-[#222]">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Trophy className="w-5 h-5 text-[#FFD700]" /> Your Referrals
              </h3>
            </div>
            <div className="divide-y divide-[#1a1a1a]">
              {data.referred_users.map(r => (
                <div key={r.id} className="flex items-center justify-between px-4 py-3">
                  <div>
                    <p className="text-white text-sm font-medium">{r.referred_name || 'User'}</p>
                    <p className="text-xs text-gray-500">{new Date(r.created_at).toLocaleDateString()}</p>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-500/20 text-green-400 border border-green-500/30">
                    {r.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* How It Works */}
        <div className="bg-[#111] border border-[#222] rounded-xl p-5" data-testid="how-it-works">
          <h3 className="text-white font-semibold mb-4">How It Works</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { step: '1', title: 'Share Your Link', desc: 'Send your unique referral link to friends and fellow artists' },
              { step: '2', title: 'They Sign Up', desc: 'When they create an account using your link, both accounts are linked' },
              { step: '3', title: 'Both Get Rewarded', desc: 'You both receive a free month of Rise with unlimited releases!' },
            ].map(s => (
              <div key={s.step} className="text-center">
                <div className="w-8 h-8 rounded-full bg-[#7C4DFF]/20 text-[#7C4DFF] font-bold text-sm flex items-center justify-center mx-auto mb-2">
                  {s.step}
                </div>
                <p className="text-white text-sm font-medium">{s.title}</p>
                <p className="text-gray-500 text-xs mt-1">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
