import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { MusicNote, Lightning, ShieldCheck, Headset, Check, Star, PaperPlaneTilt } from '@phosphor-icons/react';

const licenseTiers = [
  { id: 'basic_lease', name: 'Basic Lease', price: 29.99, desc: 'Perfect for demos and mixtapes', features: ['MP3 File (320kbps)', 'Up to 5,000 streams', 'Non-exclusive license', 'Credit required'], color: '#7C4DFF' },
  { id: 'premium_lease', name: 'Premium Lease', price: 79.99, desc: 'For serious releases', features: ['WAV + MP3 Files', 'Up to 50,000 streams', 'Trackouts included', 'Non-exclusive license', 'Credit required'], color: '#E040FB', popular: true },
  { id: 'unlimited_lease', name: 'Unlimited Lease', price: 149.99, desc: 'Maximum flexibility', features: ['WAV + MP3 + Stems', 'Unlimited streams', 'Music video rights', 'Non-exclusive license', 'Credit required'], color: '#FF4081' },
  { id: 'exclusive', name: 'Exclusive Rights', price: 499.99, desc: 'Full ownership', features: ['All files + Stems', 'Unlimited usage', 'Full ownership', 'Beat removed from catalog', 'No credit required'], color: '#FFD700' },
];

const whyItems = [
  { icon: <MusicNote className="w-6 h-6" />, title: 'Industry Quality', desc: 'Professional studio-quality beats mixed and mastered to perfection', color: '#7C4DFF' },
  { icon: <Lightning className="w-6 h-6" />, title: 'Fast Delivery', desc: 'Get your beats delivered within 24-48 hours after purchase', color: '#E040FB' },
  { icon: <ShieldCheck className="w-6 h-6" />, title: '100% Original', desc: 'All beats are original compositions with no samples', color: '#FF4081' },
  { icon: <Headset className="w-6 h-6" />, title: 'Support', desc: 'Direct communication with the producer for revisions', color: '#FFD700' },
];

const genres = ['Hip-Hop/Rap', 'R&B/Soul', 'Afrobeats', 'Dancehall', 'Reggae', 'Pop', 'Trap', 'Drill', 'Gospel', 'Electronic/EDM', 'Latin', 'Other'];
const moods = ['Energetic/Hype', 'Chill/Laid-back', 'Dark/Moody', 'Emotional/Sad', 'Happy/Uplifting', 'Romantic', 'Aggressive', 'Party/Club'];

export default function InstrumentalsPage() {
  const navigate = useNavigate();
  const [selectedLicense, setSelectedLicense] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [selectedMood, setSelectedMood] = useState('');
  const [form, setForm] = useState({ artist_name: '', email: '', phone: '', tempo_range: '', reference_tracks: '', budget: '', additional_notes: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.artist_name || !form.email || !selectedGenre) return;
    setSubmitted(true);
  };

  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto bg-[#0a0a0a]" data-testid="instrumentals-page">
        {/* Hero Card */}
        <div className="mx-4 mt-4 rounded-3xl p-7 text-center bg-gradient-to-br from-[#7C4DFF] via-[#E040FB] to-[#FF4081]">
          <div className="w-[70px] h-[70px] rounded-full bg-white/20 mx-auto mb-5 flex items-center justify-center">
            <MusicNote className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-[28px] font-extrabold text-white mb-3">Need Beats or Instrumentals?</h1>
          <p className="text-[15px] text-white/85 leading-relaxed mb-6">Can't make your own beats? No problem! Get professional instrumentals with full rights or lease options.</p>
          <div className="space-y-3">
            {['Exclusive Rights Available', 'Affordable Lease Options', 'All Genres: Hip-Hop, R&B, Afrobeats, Dancehall', 'Custom Beats on Request'].map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-full bg-white flex items-center justify-center flex-shrink-0">
                  <Check className="w-4 h-4 text-[#7C4DFF]" weight="bold" />
                </div>
                <span className="text-[15px] font-semibold text-white text-left">{f}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Why Choose Us */}
        <div className="p-6 mt-4">
          <h2 className="text-sm font-bold text-[#E040FB] tracking-[3px] text-center mb-6">WHY CHOOSE US</h2>
          <div className="grid grid-cols-2 gap-4">
            {whyItems.map((item, i) => (
              <div key={i} className="bg-[#1a1a1a] rounded-2xl p-5 text-center">
                <div className="w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center" style={{ backgroundColor: `${item.color}20`, color: item.color }}>{item.icon}</div>
                <h3 className="text-sm font-bold text-white mb-2">{item.title}</h3>
                <p className="text-xs text-gray-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* License Tiers */}
        <div className="p-6">
          <h2 className="text-sm font-bold text-[#E040FB] tracking-[3px] text-center mb-2">LICENSING OPTIONS</h2>
          <p className="text-sm text-gray-400 text-center mb-6">Choose the right license for your project</p>
          <div className="space-y-4">
            {licenseTiers.map((tier) => (
              <button key={tier.id} onClick={() => setSelectedLicense(tier.id)}
                className={`w-full bg-[#1a1a1a] rounded-2xl p-6 text-left border-2 relative overflow-hidden transition-all ${selectedLicense === tier.id ? 'border-opacity-100' : 'border-opacity-30'}`}
                style={{ borderColor: tier.color }}
                data-testid={`tier-${tier.id}`}>
                {tier.popular && (
                  <span className="absolute top-0 right-0 px-4 py-1.5 rounded-bl-xl text-[10px] font-bold text-white tracking-wider" style={{ backgroundColor: tier.color }}>MOST POPULAR</span>
                )}
                {selectedLicense === tier.id && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: tier.color }}>
                    <Check className="w-3 h-3" weight="bold" /> SELECTED
                  </span>
                )}
                <h3 className="text-lg font-bold mb-2" style={{ color: tier.color }}>{tier.name}</h3>
                <div className="flex items-start mb-2">
                  <span className="text-xl font-bold text-white mt-1">$</span>
                  <span className="text-5xl font-extrabold text-white leading-none">{Math.floor(tier.price)}</span>
                  <span className="text-xl font-bold text-white mt-1">.{String(Math.round((tier.price % 1) * 100)).padStart(2, '0')}</span>
                </div>
                <p className="text-sm text-gray-400 mb-4">{tier.desc}</p>
                <div className="space-y-2.5">
                  {tier.features.map((f, j) => (
                    <div key={j} className="flex items-center gap-2.5">
                      <Check className="w-4 h-4 flex-shrink-0" style={{ color: tier.color }} weight="bold" />
                      <span className="text-sm text-gray-300">{f}</span>
                    </div>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Request Form */}
        <div className="mx-4 mt-4 mb-8 rounded-3xl p-6 border border-[#333] bg-[#0a0a0a]" data-testid="beat-request-form">
          <div className="text-center mb-2">
            <h2 className="text-xl font-extrabold text-white tracking-[2px]">REQUEST A CUSTOM BEAT</h2>
          </div>
          <p className="text-sm text-gray-400 text-center mb-6">Fill out the form below and we'll get back to you within 24-48 hours</p>

          {submitted ? (
            <div className="text-center py-8" data-testid="request-success">
              <div className="w-[90px] h-[90px] rounded-full bg-gradient-to-r from-[#4CAF50] to-[#2E7D32] mx-auto mb-6 flex items-center justify-center">
                <Check className="w-10 h-10 text-white" weight="bold" />
              </div>
              <h3 className="text-2xl font-extrabold text-white mb-3">Request Submitted!</h3>
              <p className="text-[15px] text-gray-400 leading-relaxed mb-6">We've received your beat request. Our team will review your requirements and contact you within 24-48 hours.</p>
              <button onClick={() => { setSubmitted(false); setForm({ artist_name: '', email: '', phone: '', tempo_range: '', reference_tracks: '', budget: '', additional_notes: '' }); setSelectedGenre(''); setSelectedMood(''); }}
                className="px-7 py-3.5 rounded-full bg-[#333] text-white text-sm font-bold tracking-wider">
                SUBMIT ANOTHER REQUEST
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <h3 className="text-base font-bold text-[#E040FB] mb-4">Your Information</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Artist/Producer Name *</label>
                    <input type="text" value={form.artist_name} onChange={(e) => setForm({ ...form, artist_name: e.target.value })}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white" data-testid="req-artist-name" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Email Address *</label>
                    <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white" data-testid="req-email" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Phone Number (Optional)</label>
                    <input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white" />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-base font-bold text-[#E040FB] mb-4">Beat Requirements</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Genre *</label>
                    <div className="flex flex-wrap gap-2.5">
                      {genres.map((g) => (
                        <button type="button" key={g} onClick={() => setSelectedGenre(g)}
                          className={`px-4 py-2.5 rounded-full text-[13px] font-medium border transition-all ${selectedGenre === g ? 'bg-[#7C4DFF] border-[#7C4DFF] text-white' : 'bg-[#111] border-[#333] text-gray-400'}`}
                          data-testid={`genre-${g.toLowerCase().replace(/[^a-z]/g, '-')}`}>
                          {g}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Mood/Vibe</label>
                    <div className="flex flex-wrap gap-2.5">
                      {moods.map((m) => (
                        <button type="button" key={m} onClick={() => setSelectedMood(m)}
                          className={`px-4 py-2.5 rounded-full text-[13px] font-medium border transition-all ${selectedMood === m ? 'bg-[#E040FB] border-[#E040FB] text-white' : 'bg-[#111] border-[#333] text-gray-400'}`}>
                          {m}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Tempo Range (BPM)</label>
                    <input type="text" value={form.tempo_range} onChange={(e) => setForm({ ...form, tempo_range: e.target.value })} placeholder="e.g., 120-140"
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white placeholder-gray-600" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Reference Tracks</label>
                    <textarea value={form.reference_tracks} onChange={(e) => setForm({ ...form, reference_tracks: e.target.value })} placeholder="Share links or names of tracks with a similar vibe" rows={3}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white placeholder-gray-600 resize-none" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Budget Range</label>
                    <input type="text" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} placeholder="e.g., $100-$300"
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white placeholder-gray-600" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Additional Notes</label>
                    <textarea value={form.additional_notes} onChange={(e) => setForm({ ...form, additional_notes: e.target.value })} placeholder="Any specific requirements..." rows={3}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white placeholder-gray-600 resize-none" />
                  </div>
                </div>
              </div>

              {selectedLicense && (
                <div className="flex items-center gap-2.5 p-4 rounded-xl bg-[#4CAF50]/10 border border-[#4CAF50]/30">
                  <Check className="w-5 h-5 text-[#4CAF50]" weight="bold" />
                  <span className="text-sm text-[#4CAF50] font-semibold">Selected: {licenseTiers.find(t => t.id === selectedLicense)?.name}</span>
                </div>
              )}

              <button type="submit"
                className="w-full py-4.5 rounded-full bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white font-bold tracking-wider flex items-center justify-center gap-2"
                data-testid="submit-beat-request">
                <PaperPlaneTilt className="w-5 h-5" /> SUBMIT REQUEST
              </button>
            </form>
          )}
        </div>

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
