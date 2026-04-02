import React from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { InstagramLogo, TiktokLogo, Envelope, MusicNote, Check, ArrowRight } from '@phosphor-icons/react';

const packages = [
  { name: 'Starter', price: 99, features: ['Social media promotion', 'Basic playlist pitching', '1 week campaign'], color: '#7C4DFF' },
  { name: 'Professional', price: 299, features: ['Advanced playlist pitching', 'Press outreach', '2 week campaign', 'Social media ads'], color: '#E040FB', highlight: true },
  { name: 'Premium', price: 599, features: ['VIP playlist placement', 'Full press campaign', '4 week campaign', 'Influencer marketing', 'Music video promotion'], color: '#FFD700' },
];

const channels = [
  { icon: <InstagramLogo className="w-7 h-7" />, title: 'Instagram', desc: 'Stories, Reels & Posts', color: '#E4405F' },
  { icon: <TiktokLogo className="w-7 h-7" />, title: 'TikTok', desc: 'Viral Marketing', color: '#00F2EA' },
  { icon: <Envelope className="w-7 h-7" />, title: 'Email', desc: 'Curator Outreach', color: '#FFD700' },
  { icon: <MusicNote className="w-7 h-7" />, title: 'Playlists', desc: 'Editorial Pitching', color: '#1DB954' },
];

export default function PromotingPage() {
  const navigate = useNavigate();
  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto" data-testid="promoting-page">
        {/* Hero */}
        <div className="py-10 px-6 text-center">
          <p className="text-xs font-bold text-[#E040FB] tracking-[3px] mb-3">PROMOTION SERVICES</p>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white">Get Your Music <span className="text-[#E040FB]">Heard</span></h1>
          <p className="text-gray-400 mt-4 max-w-md mx-auto leading-relaxed">Professional promotion services to boost your music career.</p>
        </div>

        {/* Channels */}
        <div className="px-4 grid grid-cols-2 gap-3 mb-8">
          {channels.map((ch, i) => (
            <div key={i} className="bg-[#111] rounded-xl p-4 text-center border border-[#222]">
              <div className="w-12 h-12 rounded-full mx-auto mb-2 flex items-center justify-center" style={{ backgroundColor: `${ch.color}20`, color: ch.color }}>{ch.icon}</div>
              <p className="text-sm font-bold text-white">{ch.title}</p>
              <p className="text-xs text-gray-400">{ch.desc}</p>
            </div>
          ))}
        </div>

        {/* Packages */}
        <div className="px-4 space-y-4 pb-8">
          <h2 className="text-xl font-bold text-white text-center tracking-wider mb-4">PROMOTION PACKAGES</h2>
          {packages.map((pkg, i) => (
            <div key={i} className={`bg-[#111] rounded-2xl p-6 text-center border-2 ${pkg.highlight ? 'border-[#E040FB]' : 'border-[#222]'}`} data-testid={`promo-${pkg.name.toLowerCase()}`}>
              <h3 className="text-lg font-bold text-white mb-2">{pkg.name}</h3>
              <p className="text-4xl font-extrabold mb-4" style={{ color: pkg.color }}>${pkg.price}</p>
              <div className="space-y-2.5 mb-5">
                {pkg.features.map((f, j) => (
                  <div key={j} className="flex items-center gap-2 justify-center">
                    <Check className="w-4 h-4 text-[#4CAF50]" weight="bold" />
                    <span className="text-sm text-gray-300">{f}</span>
                  </div>
                ))}
              </div>
              <button onClick={() => navigate('/register')} className="px-8 py-3.5 rounded-full text-sm font-bold tracking-wider text-white" style={{ backgroundColor: pkg.color }}
                data-testid={`promo-cta-${pkg.name.toLowerCase()}`}>
                GET STARTED
              </button>
            </div>
          ))}
        </div>

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
