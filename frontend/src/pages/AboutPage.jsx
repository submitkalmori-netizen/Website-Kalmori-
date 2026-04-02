import React from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { Heart, ShieldCheck, Lightning, Users, ArrowRight } from '@phosphor-icons/react';

const values = [
  { icon: <Heart className="w-7 h-7" />, title: 'Artist First', desc: 'Every decision we make puts artists first', color: '#E53935' },
  { icon: <ShieldCheck className="w-7 h-7" />, title: 'Transparency', desc: 'No hidden fees, no surprises', color: '#7C4DFF' },
  { icon: <Lightning className="w-7 h-7" />, title: 'Innovation', desc: 'Always improving our platform', color: '#FFD700' },
  { icon: <Users className="w-7 h-7" />, title: 'Community', desc: 'Building a family of artists', color: '#E040FB' },
];

export default function AboutPage() {
  const navigate = useNavigate();
  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto" data-testid="about-page">
        {/* Hero */}
        <div className="py-10 px-6 text-center bg-gradient-to-b from-[#7C4DFF]/10 to-transparent">
          <p className="text-xs font-bold text-[#E040FB] tracking-[3px] mb-3">ABOUT KALMORI</p>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white">Empowering Artists <span className="text-[#E040FB]">Worldwide</span></h1>
          <p className="text-gray-300 mt-4 leading-relaxed max-w-md mx-auto">We believe every artist deserves to be heard. Kalmori was founded to give independent musicians the tools they need to succeed.</p>
          <div className="flex gap-3 justify-center mt-6">
            <button onClick={() => navigate('/register')} className="px-6 py-3 rounded-lg bg-[#7C4DFF] text-white text-sm font-bold tracking-wider" data-testid="about-get-started">GET STARTED</button>
            <button onClick={() => navigate('/contact')} className="px-6 py-3 rounded-lg border border-[#7C4DFF] text-[#7C4DFF] text-sm font-bold tracking-wider">CONTACT US</button>
          </div>
        </div>

        {/* Mission */}
        <div className="p-6 bg-[#0a0a0a]">
          <h2 className="text-xl font-bold text-white mb-4 tracking-wider">OUR MISSION</h2>
          <p className="text-[15px] text-gray-300 leading-relaxed">To democratize music distribution and empower artists to reach their full potential without giving up their rights or royalties. We provide the platform, you keep the ownership.</p>
        </div>

        {/* Values */}
        <div className="p-6">
          <h2 className="text-xl font-bold text-white mb-5 tracking-wider text-center">OUR VALUES</h2>
          <div className="grid grid-cols-2 gap-4">
            {values.map((v, i) => (
              <div key={i} className="bg-[#111] rounded-xl p-4 text-center" data-testid={`value-${i}`}>
                <div className="w-14 h-14 rounded-full mx-auto mb-3 flex items-center justify-center" style={{ backgroundColor: `${v.color}20`, color: v.color }}>
                  {v.icon}
                </div>
                <h3 className="text-base font-bold text-white mb-1">{v.title}</h3>
                <p className="text-[13px] text-gray-400 leading-relaxed">{v.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="p-10 bg-[#111] text-center">
          <h2 className="text-2xl font-extrabold text-white">Ready to Join?</h2>
          <p className="text-sm text-gray-400 mt-2">Start distributing your music worldwide today</p>
          <button onClick={() => navigate('/register')} className="mt-6 px-8 py-4 rounded-lg bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white font-bold tracking-wider" data-testid="about-join-cta">
            JOIN KALMORI <ArrowRight className="w-5 h-5 inline ml-2" />
          </button>
        </div>

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
