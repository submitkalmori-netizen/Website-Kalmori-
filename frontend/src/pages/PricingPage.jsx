import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { useAuth } from '../App';
import { Check, X, ArrowRight, Star, Crown, Lightning, Rocket, ShieldCheck, CurrencyDollar, ChartLineUp, MusicNote, Sparkle } from '@phosphor-icons/react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const plans = [
  {
    id: 'free', name: 'Free', price: 0, period: '',
    tagline: 'Start distributing your music today',
    badge: 'FREE', badgeStyle: 'bg-[#333] text-white', highlight: false,
    icon: <Lightning className="w-7 h-7" weight="fill" />,
    revenueShare: '20%',
    revenueNote: 'We keep 20% of your royalties',
    color: '#888',
    features: [
      { text: '1 release per year', included: true },
      { text: '150+ streaming platforms', included: true },
      { text: 'Free ISRC codes', included: true },
      { text: 'Basic analytics', included: true },
      { text: 'Standard support', included: true },
      { text: 'Unlimited releases', included: false },
      { text: 'AI Release Strategy', included: false },
      { text: 'Revenue Export (PDF/CSV)', included: false },
      { text: 'YouTube Content ID', included: false },
      { text: 'Spotify Canvas', included: false },
      { text: 'Pre-Save Campaigns', included: false },
      { text: 'Collaborations & Splits', included: false },
    ],
  },
  {
    id: 'rise', name: 'Rise', price: 9.99, period: '/mo',
    tagline: 'Grow your career with more tools',
    badge: 'POPULAR', badgeStyle: 'bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white', highlight: false,
    icon: <Rocket className="w-7 h-7" weight="fill" />,
    revenueShare: '10%',
    revenueNote: 'We keep only 10% of your royalties',
    color: '#7C4DFF',
    features: [
      { text: 'Unlimited releases', included: true },
      { text: '150+ streaming platforms', included: true },
      { text: 'Free ISRC & UPC codes', included: true },
      { text: 'Advanced analytics', included: true },
      { text: 'Revenue dashboard', included: true },
      { text: 'Fan Analytics', included: true },
      { text: 'Goal Tracking', included: true },
      { text: 'Priority support', included: true },
      { text: 'AI Release Strategy', included: false },
      { text: 'YouTube Content ID', included: false },
      { text: 'Spotify Canvas', included: false },
      { text: 'Pre-Save Campaigns', included: false },
    ],
  },
  {
    id: 'pro', name: 'Pro', price: 19.99, period: '/mo',
    tagline: 'Everything you need. Keep 100%.',
    badge: 'BEST VALUE', badgeStyle: 'bg-gradient-to-r from-[#FFD700] to-[#FFA500] text-black', highlight: true,
    icon: <Crown className="w-7 h-7" weight="fill" />,
    revenueShare: '0%',
    revenueNote: 'You keep 100% of your royalties',
    color: '#FFD700',
    features: [
      { text: 'Unlimited releases', included: true },
      { text: '150+ streaming platforms', included: true },
      { text: 'Free ISRC & UPC codes', included: true },
      { text: 'Keep 100% royalties', included: true, highlight: true },
      { text: 'AI Release Strategy', included: true, highlight: true },
      { text: 'Revenue Export (PDF/CSV)', included: true },
      { text: 'YouTube Content ID', included: true },
      { text: 'Spotify Canvas uploads', included: true },
      { text: 'Release Leaderboard', included: true },
      { text: 'Pre-Save Campaigns', included: true },
      { text: 'Collaborations & Splits', included: true },
      { text: 'Dedicated support', included: true },
    ],
  },
];

export default function PricingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [upgrading, setUpgrading] = useState(null);

  const currentPlan = user?.plan || 'free';
  const planOrder = ['free', 'rise', 'pro'];

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const subscription = params.get('subscription');
    const plan = params.get('plan');
    if (subscription === 'success' && plan) {
      const token = document.cookie.split(';').find(c => c.trim().startsWith('access_token='))?.split('=')[1]
        || localStorage.getItem('access_token');
      axios.post(`${API_URL}/api/subscriptions/upgrade?plan=${plan}`, {}, {
        headers: { Authorization: `Bearer ${token}` }, withCredentials: true,
      }).then(() => {
        toast.success(`Successfully upgraded to ${plan.charAt(0).toUpperCase() + plan.slice(1)}!`);
        window.history.replaceState({}, '', '/pricing');
        setTimeout(() => window.location.reload(), 500);
      }).catch(() => toast.error('Failed to activate plan'));
    } else if (subscription === 'cancelled') {
      toast.error('Payment was cancelled');
      window.history.replaceState({}, '', '/pricing');
    }
  }, []);

  const handlePlanAction = async (planId) => {
    if (!user) { navigate('/register'); return; }
    if (planId === currentPlan) return;
    setUpgrading(planId);
    try {
      if (planId !== 'free') {
        const res = await axios.post(`${API_URL}/api/subscriptions/checkout`, {
          plan: planId, origin_url: window.location.origin,
        }, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }, withCredentials: true });
        if (res.data.checkout_url) { window.location.href = res.data.checkout_url; return; }
      }
      const token = document.cookie.split(';').find(c => c.trim().startsWith('access_token='))?.split('=')[1]
        || localStorage.getItem('access_token');
      await axios.post(`${API_URL}/api/subscriptions/upgrade?plan=${planId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }, withCredentials: true,
      });
      toast.success(`Plan changed to ${plans.find(p => p.id === planId)?.name}!`);
      window.location.reload();
    } catch (err) {
      try {
        const token = document.cookie.split(';').find(c => c.trim().startsWith('access_token='))?.split('=')[1]
          || localStorage.getItem('access_token');
        await axios.post(`${API_URL}/api/subscriptions/upgrade?plan=${planId}`, {}, {
          headers: { Authorization: `Bearer ${token}` }, withCredentials: true,
        });
        toast.success(`Plan changed to ${plans.find(p => p.id === planId)?.name}!`);
        window.location.reload();
      } catch { toast.error('Failed to change plan'); }
    } finally { setUpgrading(null); }
  };

  const getButtonText = (planId) => {
    if (!user) return 'GET STARTED';
    if (planId === currentPlan) return 'CURRENT PLAN';
    return planOrder.indexOf(planId) > planOrder.indexOf(currentPlan) ? 'UPGRADE NOW' : 'DOWNGRADE';
  };

  return (
    <PublicLayout>
      <div className="max-w-6xl mx-auto px-4" data-testid="pricing-page">
        {/* Hero Header */}
        <div className="py-12 sm:py-16 text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-tight">
            Choose Your <span className="bg-gradient-to-r from-[#FFD700] to-[#FFA500] bg-clip-text text-transparent">Plan</span>
          </h1>
          <p className="text-base sm:text-lg text-gray-400 mt-4 max-w-xl mx-auto">
            Upload unlimited music to 150+ streaming platforms. The more you invest, the more you keep.
          </p>
          {user && (
            <div className="mt-5 inline-flex items-center gap-2 px-5 py-2 rounded-full bg-white/5 border border-white/10">
              <ShieldCheck className="w-4 h-4 text-[#E040FB]" />
              <span className="text-sm text-gray-300">
                Current plan: <span className="font-bold text-white uppercase">{currentPlan}</span>
              </span>
            </div>
          )}
        </div>

        {/* Revenue Share Comparison Bar */}
        <div className="bg-[#111] border border-white/10 rounded-2xl p-6 mb-10" data-testid="revenue-comparison">
          <h3 className="text-sm font-bold text-white text-center mb-5 flex items-center justify-center gap-2">
            <CurrencyDollar className="w-4 h-4 text-[#1DB954]" /> Revenue Share Comparison
          </h3>
          <div className="flex items-end justify-center gap-6 sm:gap-10">
            {plans.map(p => {
              const keepPct = 100 - parseInt(p.revenueShare);
              return (
                <div key={p.id} className="text-center" data-testid={`revenue-share-${p.id}`}>
                  <div className="relative h-32 w-16 sm:w-20 bg-[#1a1a1a] rounded-lg overflow-hidden mx-auto mb-2">
                    <div
                      className="absolute bottom-0 w-full rounded-b-lg transition-all duration-700"
                      style={{
                        height: `${keepPct}%`,
                        background: p.id === 'pro' ? 'linear-gradient(to top, #FFD700, #FFA500)' :
                                    p.id === 'rise' ? 'linear-gradient(to top, #7C4DFF, #E040FB)' :
                                    'linear-gradient(to top, #444, #666)',
                      }}
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg sm:text-xl font-black text-white drop-shadow-lg">{keepPct}%</span>
                    </div>
                  </div>
                  <p className="text-xs font-bold text-white">{p.name}</p>
                  <p className="text-[10px] text-gray-500">You keep {keepPct}%</p>
                </div>
              );
            })}
          </div>
          <p className="text-center text-xs text-gray-500 mt-4">On $1,000/mo royalties: Free keeps $800 · Rise keeps $900 · Pro keeps <span className="text-[#FFD700] font-bold">$1,000</span></p>
        </div>

        {/* Plan Cards - DistroKid Style */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-12" data-testid="plan-cards">
          {plans.map(plan => {
            const isCurrent = user && plan.id === currentPlan;
            const isPro = plan.id === 'pro';
            return (
              <div
                key={plan.id}
                className={`relative rounded-2xl overflow-hidden transition-all ${
                  isPro ? 'border-2 border-[#FFD700] shadow-lg shadow-[#FFD700]/10 scale-[1.02] md:scale-105' :
                  isCurrent ? 'border-2 border-[#E040FB] shadow-lg shadow-[#E040FB]/10' :
                  'border border-white/10'
                }`}
                data-testid={`plan-${plan.id}`}
              >
                {/* Badge */}
                <div className={`py-2.5 px-4 text-center ${isCurrent ? 'bg-[#E040FB]' : plan.badgeStyle}`}>
                  <span className="text-xs font-black tracking-[3px]">
                    {isCurrent ? 'YOUR CURRENT PLAN' : plan.badge}
                  </span>
                </div>

                <div className="bg-[#111] p-6 sm:p-7">
                  {/* Icon + Name */}
                  <div className="text-center mb-5">
                    <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-3"
                      style={{ backgroundColor: `${plan.color}15`, color: plan.color }}>
                      {plan.icon}
                    </div>
                    <h3 className="text-2xl font-black tracking-[3px] text-white">{plan.name.toUpperCase()}</h3>
                    <p className="text-xs text-gray-500 mt-1">{plan.tagline}</p>
                  </div>

                  {/* Price */}
                  <div className="text-center mb-5">
                    {plan.price > 0 ? (
                      <div className="flex items-baseline justify-center">
                        <span className="text-xl font-bold" style={{ color: plan.color }}>$</span>
                        <span className="text-5xl font-black text-white">{plan.price}</span>
                        <span className="text-sm text-gray-500 ml-1">{plan.period}</span>
                      </div>
                    ) : (
                      <p className="text-5xl font-black text-white">FREE</p>
                    )}
                  </div>

                  {/* Revenue Share Highlight */}
                  <div className="rounded-xl p-3 mb-5 text-center"
                    style={{ backgroundColor: `${plan.color}10`, borderColor: `${plan.color}30`, borderWidth: '1px' }}>
                    <p className="text-sm font-bold" style={{ color: plan.color }}>{plan.revenueNote}</p>
                    <p className="text-[10px] text-gray-500 mt-0.5">Kalmori takes {plan.revenueShare} revenue share</p>
                  </div>

                  {/* CTA Button */}
                  <button
                    onClick={() => handlePlanAction(plan.id)}
                    disabled={isCurrent || upgrading === plan.id}
                    className={`w-full py-3.5 rounded-xl text-sm font-black tracking-[2px] transition-all mb-6 ${
                      isCurrent ? 'bg-white/10 text-gray-400 cursor-default' :
                      isPro ? 'bg-gradient-to-r from-[#FFD700] to-[#FFA500] text-black hover:brightness-110' :
                      plan.id === 'rise' ? 'bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white hover:brightness-110' :
                      'bg-white/10 text-white hover:bg-white/15'
                    }`}
                    data-testid={`plan-cta-${plan.id}`}
                  >
                    {upgrading === plan.id ? (
                      <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin mx-auto" />
                    ) : getButtonText(plan.id)}
                  </button>

                  {/* Features List */}
                  <div className="space-y-2.5">
                    {plan.features.map((f, i) => (
                      <div key={i} className="flex items-center gap-2.5" data-testid={`feature-${plan.id}-${i}`}>
                        {f.included ? (
                          <Check className="w-4 h-4 text-[#4CAF50] flex-shrink-0" weight="bold" />
                        ) : (
                          <X className="w-4 h-4 text-gray-600 flex-shrink-0" weight="bold" />
                        )}
                        <span className={`text-sm ${
                          f.highlight ? 'text-[#FFD700] font-bold' :
                          f.included ? 'text-gray-300' : 'text-gray-600 line-through'
                        }`}>
                          {f.text}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Why Upgrade Section */}
        <div className="bg-gradient-to-br from-[#0a0a0a] to-[#111] border border-white/10 rounded-2xl p-8 mb-10">
          <h3 className="text-lg font-black text-center text-white mb-6 tracking-[2px]">WHY GO PRO?</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <WhyCard
              icon={<CurrencyDollar className="w-6 h-6 text-[#1DB954]" weight="fill" />}
              title="Keep 100% Royalties"
              desc="Free plan takes 20%, Rise takes 10%. Pro? You keep every single penny."
            />
            <WhyCard
              icon={<Sparkle className="w-6 h-6 text-[#FFD700]" weight="fill" />}
              title="AI-Powered Tools"
              desc="Get AI release strategies, smart notifications, and data-driven insights to grow faster."
            />
            <WhyCard
              icon={<ChartLineUp className="w-6 h-6 text-[#E040FB]" weight="fill" />}
              title="Full Analytics Suite"
              desc="Leaderboards, fan analytics, goal tracking, and exportable revenue reports."
            />
          </div>
          <div className="mt-8 text-center">
            <p className="text-gray-400 text-sm">On <span className="text-white font-bold">$1,000</span> monthly royalties:</p>
            <div className="flex items-center justify-center gap-4 sm:gap-8 mt-3">
              <div><p className="text-lg font-bold text-gray-500">$800</p><p className="text-[10px] text-gray-600">Free plan</p></div>
              <ArrowRight className="w-4 h-4 text-gray-600" />
              <div><p className="text-lg font-bold text-[#7C4DFF]">$900</p><p className="text-[10px] text-gray-500">Rise plan</p></div>
              <ArrowRight className="w-4 h-4 text-gray-600" />
              <div><p className="text-2xl font-black text-[#FFD700]">$1,000</p><p className="text-[10px] text-[#FFD700]">Pro plan</p></div>
            </div>
          </div>
        </div>

        {/* Bottom CTA */}
        {!user && (
          <div className="py-12 text-center">
            <h2 className="text-2xl font-bold text-white mb-2">Ready to distribute your music?</h2>
            <p className="text-sm text-gray-400 mb-8">Join thousands of artists who trust Kalmori Distribution</p>
            <button onClick={() => navigate('/register')}
              className="px-10 py-4 rounded-xl bg-gradient-to-r from-[#FFD700] to-[#FFA500] text-black font-black tracking-[2px] text-sm hover:brightness-110 transition-all inline-flex items-center gap-2"
              data-testid="pricing-start-now">
              <Star className="w-5 h-5" weight="fill" /> START FREE — UPGRADE ANYTIME
            </button>
          </div>
        )}

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}

function WhyCard({ icon, title, desc }) {
  return (
    <div className="text-center p-4">
      <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-3">{icon}</div>
      <h4 className="text-sm font-bold text-white mb-1">{title}</h4>
      <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
    </div>
  );
}
