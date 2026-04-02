import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { Check, ArrowRight, Star } from '@phosphor-icons/react';

const defaultPlans = [
  { id: 'free', name: 'Free', price: 0, period: '', description: 'Start distributing for free with revenue share', badge: 'FREE', badge_color: 'green', highlight: false, features: ['1 release per year', '15-20% revenue share', 'Basic analytics', 'Standard support', 'Free ISRC codes'] },
  { id: 'single', name: 'Unlimited Single', price: 20, period: '/year', description: 'Perfect for single releases', badge: 'UNLIMITED', badge_color: 'purple', highlight: false, features: ['Up to 3 tracks', '100% royalties', 'All 150+ stores', 'Free ISRC & UPC codes', 'Basic analytics', 'Standard support'] },
  { id: 'album', name: 'Album', price: 75, period: '/year', description: 'Best value for full albums', badge: 'BEST DEAL', badge_color: 'gold', highlight: true, features: ['7+ tracks per release', '100% royalties', 'All 150+ stores', 'Free ISRC & UPC codes', 'Advanced analytics', 'Priority support', 'Spotify playlist pitching'] },
];

const badgeGradients = { gold: 'from-[#FFD700] to-[#FFA500]', green: 'from-[#4CAF50] to-[#2E7D32]', purple: 'from-[#7C4DFF] to-[#E040FB]', red: 'from-[#E53935] to-[#FF6B35]' };

export default function PricingPage() {
  const navigate = useNavigate();
  const [plans, setPlans] = useState(defaultPlans);

  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto" data-testid="pricing-page">
        {/* Header */}
        <div className="p-6 text-center">
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-[4px] bg-gradient-to-r from-[#7C4DFF] via-[#E040FB] to-[#FF4081] bg-clip-text text-transparent">PRICING</h1>
          <p className="text-gray-400 mt-2">Choose the plan that fits your music career</p>
        </div>

        {/* Plans */}
        <div className="px-4 space-y-5 pb-8">
          {plans.map((plan, i) => (
            <div key={plan.id} className={`bg-[#111] rounded-2xl overflow-hidden border-2 ${plan.highlight ? 'border-[#FFD700]' : 'border-[#222]'}`} data-testid={`plan-${plan.id}`}>
              {plan.badge && (
                <div className={`py-2 px-4 text-center bg-gradient-to-r ${badgeGradients[plan.badge_color] || badgeGradients.purple}`}>
                  <span className="text-xs font-extrabold text-white tracking-wider">{plan.badge}</span>
                </div>
              )}
              <div className="p-6 text-center">
                <h3 className="text-2xl font-extrabold tracking-[2px] text-white mb-4">{plan.name.toUpperCase()}</h3>
                {plan.price > 0 ? (
                  <div className="flex items-baseline justify-center mb-3">
                    <span className="text-2xl font-semibold text-[#E040FB]">$</span>
                    <span className="text-5xl font-extrabold text-white">{plan.price}</span>
                    <span className="text-base text-gray-400 ml-1">{plan.period}</span>
                  </div>
                ) : (
                  <p className="text-5xl font-extrabold text-white mb-3">FREE</p>
                )}
                <p className="text-sm text-gray-400 mb-6">{plan.description}</p>
                <div className="space-y-3 mb-6">
                  {plan.features.map((f, j) => (
                    <div key={j} className="flex items-center gap-2.5 justify-center">
                      <Check className="w-4 h-4 text-[#4CAF50] flex-shrink-0" weight="bold" />
                      <span className="text-sm text-gray-300">{f}</span>
                    </div>
                  ))}
                </div>
                <button onClick={() => navigate('/register')}
                  className={`px-8 py-3.5 rounded-full text-sm font-bold tracking-wider text-white bg-gradient-to-r ${plan.highlight ? 'from-[#FFD700] to-[#FFA500]' : 'from-[#7C4DFF] to-[#E040FB]'}`}
                  data-testid={`plan-cta-${plan.id}`}>
                  GET STARTED
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="p-8 text-center">
          <h2 className="text-xl font-bold text-white mb-2">Ready to distribute your music?</h2>
          <p className="text-sm text-gray-400 mb-6">Join thousands of artists who trust Kalmori</p>
          <button onClick={() => navigate('/register')}
            className="w-full max-w-xs mx-auto py-4 rounded-xl bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white font-bold tracking-wider flex items-center justify-center gap-2"
            data-testid="pricing-start-now">
            <Star className="w-5 h-5" weight="fill" /> START NOW
          </button>
        </div>

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
