import React from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { MusicNote, ChartLineUp, ShieldCheck, Megaphone, Check, ArrowRight } from '@phosphor-icons/react';

const services = [
  { icon: <MusicNote className="w-7 h-7" />, title: 'Music Distribution', color: '#7C4DFF', desc: 'Get your music on Spotify, Apple Music, and 150+ platforms worldwide. One upload, global reach.', items: ['All major streaming platforms', 'Social media platforms', 'Digital download stores', 'Free ISRC & UPC codes'], link: '/pricing' },
  { icon: <ChartLineUp className="w-7 h-7" />, title: 'Analytics & Insights', color: '#E040FB', desc: 'Track your streams, downloads, and earnings across all platforms with detailed real-time analytics.', items: ['Stream & download tracking', 'Revenue analytics', 'Audience demographics', 'Growth reports'], link: '/dashboard' },
  { icon: <Megaphone className="w-7 h-7" />, title: 'Promotion Services', color: '#FF4081', desc: 'Professional promotion services to boost your music career and reach new fans worldwide.', items: ['Social media promotion', 'Playlist pitching', 'Press outreach', 'Influencer marketing'], link: '/promoting' },
  { icon: <ShieldCheck className="w-7 h-7" />, title: 'Publishing & Royalties', color: '#FFD700', desc: 'Collect all the royalties you\'re owed from streaming, radio, and live performances.', items: ['Song registration', 'Royalty collection', 'Sync licensing', 'Copyright protection'], link: '/publishing' },
];

export default function ServicesPage() {
  const navigate = useNavigate();
  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto" data-testid="services-page">
        {/* Hero */}
        <div className="py-10 px-6 text-center">
          <p className="text-xs font-bold text-[#E040FB] tracking-[3px] mb-3">OUR SERVICES</p>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-wide">Everything You Need to <span className="text-[#E040FB]">Succeed</span></h1>
          <p className="text-gray-400 mt-4 leading-relaxed max-w-md mx-auto">From distribution to promotion, we provide all the tools independent artists need to build their career.</p>
        </div>

        {/* Service Cards */}
        <div className="px-4 space-y-4 pb-8">
          {services.map((s, i) => (
            <div key={i} className="bg-[#0a0a0a] border-b border-[#222] p-6 text-center" data-testid={`service-${i}`}>
              <div className="w-14 h-14 rounded-full mx-auto mb-4 flex items-center justify-center" style={{ backgroundColor: `${s.color}20`, color: s.color }}>
                {s.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-2 tracking-wider">{s.title}</h3>
              <p className="text-sm text-gray-300 leading-relaxed mb-4">{s.desc}</p>
              <div className="space-y-2.5 mb-5">
                {s.items.map((item, j) => (
                  <div key={j} className="flex items-center gap-2.5 justify-center">
                    <Check className="w-4 h-4 flex-shrink-0" weight="bold" style={{ color: s.color }} />
                    <span className="text-sm text-white">{item}</span>
                  </div>
                ))}
              </div>
              <button onClick={() => navigate(s.link)}
                className="px-6 py-3 rounded-full text-sm font-bold tracking-wider text-white" style={{ backgroundColor: s.color }}
                data-testid={`service-cta-${i}`}>
                LEARN MORE <ArrowRight className="w-4 h-4 inline ml-1" />
              </button>
            </div>
          ))}
        </div>

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
