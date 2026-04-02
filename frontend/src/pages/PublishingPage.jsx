import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { MusicNote, CurrencyDollar, Television, ShieldCheck, Check, Star } from '@phosphor-icons/react';

const services = [
  { title: 'Song Registration', desc: 'Register your songs with performance rights organizations worldwide', icon: <MusicNote className="w-7 h-7" />, color: '#FFD700', features: ['ASCAP/BMI Registration', 'Global PRO Coverage', 'Metadata Management'] },
  { title: 'Royalty Collection', desc: 'Collect all the royalties you\'re owed from streaming, radio, and live performances', icon: <CurrencyDollar className="w-7 h-7" />, color: '#4CAF50', features: ['Mechanical Royalties', 'Performance Royalties', 'Digital Royalties'] },
  { title: 'Sync Licensing', desc: 'Get your music placed in TV shows, movies, commercials, and video games', icon: <Television className="w-7 h-7" />, color: '#00B0FF', features: ['TV & Film Placements', 'Commercial Licensing', 'Video Game Sync'] },
  { title: 'Copyright Protection', desc: 'Protect your intellectual property and monitor unauthorized use', icon: <ShieldCheck className="w-7 h-7" />, color: '#E53935', features: ['Copyright Registration', 'Content ID Monitoring', 'Takedown Services'] },
];

const stats = [
  { value: '$75', label: 'One-time Fee' },
  { value: '20%', label: 'More Royalties' },
  { value: '150+', label: 'Countries' },
];

export default function PublishingPage() {
  const navigate = useNavigate();
  const [showPopup, setShowPopup] = useState(false);

  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto" data-testid="publishing-page">
        {/* Hero */}
        <div className="mx-4 mt-4 rounded-2xl p-8 text-center bg-gradient-to-br from-[#7C4DFF] to-[#E040FB]">
          <MusicNote className="w-16 h-16 text-white mx-auto mb-4" />
          <h1 className="text-3xl font-extrabold text-white">Your Songs. Your Money.</h1>
          <p className="text-white/90 mt-3 leading-relaxed">Every play on Spotify, YouTube, TikTok generates publishing royalties. Collect up to 20% more.</p>
        </div>

        {/* Stats */}
        <div className="mx-4 mt-4 bg-[#111] rounded-2xl flex justify-around py-6">
          {stats.map((s, i) => (
            <div key={i} className="text-center">
              <p className="text-3xl font-extrabold text-[#FFD700]">{s.value}</p>
              <p className="text-xs text-gray-300 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Services */}
        <div className="p-4 space-y-4 mt-4">
          <h2 className="text-xl font-bold text-white text-center mb-4">Publishing Services</h2>
          {services.map((s, i) => (
            <div key={i} className="bg-[#111] rounded-2xl p-5 text-center" data-testid={`pub-service-${i}`}>
              <div className="w-14 h-14 rounded-2xl mx-auto mb-3 flex items-center justify-center" style={{ backgroundColor: `${s.color}20`, color: s.color }}>{s.icon}</div>
              <h3 className="text-lg font-bold text-white mb-2">{s.title}</h3>
              <p className="text-sm text-gray-300 leading-relaxed mb-3">{s.desc}</p>
              <div className="space-y-1.5">
                {s.features.map((f, j) => (
                  <div key={j} className="flex items-center gap-2 justify-center">
                    <Check className="w-4 h-4 flex-shrink-0" style={{ color: s.color }} weight="bold" />
                    <span className="text-[13px] text-gray-300">{f}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mx-4 my-6 p-6 bg-[#1a1a1a] rounded-2xl text-center">
          <h2 className="text-[22px] font-extrabold text-white mb-2">Start Collecting Today</h2>
          <p className="text-sm text-gray-300 mb-5">Get lifetime access to publishing administration for just $75</p>
          <button onClick={() => setShowPopup(true)}
            className="px-8 py-3.5 rounded-full bg-[#FFD700] text-black font-bold tracking-wider inline-flex items-center gap-2"
            data-testid="pub-signup-btn">
            <Star className="w-5 h-5" weight="fill" /> SIGN UP NOW
          </button>
        </div>

        {/* Popup */}
        {showPopup && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/85" data-testid="pub-popup">
            <div className="w-full max-w-md rounded-3xl overflow-hidden bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] p-10 text-center">
              <Star className="w-16 h-16 text-[#FFD700] mx-auto" weight="fill" />
              <h2 className="text-2xl font-extrabold text-white mt-6 tracking-wider">WE WILL SOON BE YOUR PUBLISHER</h2>
              <p className="text-white/90 mt-3 leading-relaxed">Stay tuned for our upcoming publishing services!</p>
              <button onClick={() => setShowPopup(false)} className="mt-8 px-12 py-3.5 rounded-full border-2 border-white text-white font-bold tracking-[2px]">GOT IT</button>
            </div>
          </div>
        )}

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
