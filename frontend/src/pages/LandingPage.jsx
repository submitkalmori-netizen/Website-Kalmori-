import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { DynamicPageRenderer } from '../components/DynamicPageRenderer';
import { ArrowRight, Check, SpotifyLogo, AppleLogo, YoutubeLogo, TiktokLogo, InstagramLogo, TwitterLogo, Envelope, MusicNote, MusicNotes, Playlist, Rocket, CheckCircle, Headset, Globe, CurrencyDollar, ShieldCheck, Star, Quotes, Play, Pause, Lightning, ChartLineUp, Brain, Users, Trophy, Target, ShareNetwork, ChatCircleDots, FileText, Waveform, HandCoins, Palette, QrCode, Copy } from '@phosphor-icons/react';
import axios from 'axios';
import { API } from '../App';

// Hero images
const heroSlideImages = [
  'https://customer-assets.emergentagent.com/job_9d65d3d0-8e4c-4ca7-97e3-3472b806edee/artifacts/oldly27j_vecteezy_professional-microphone-on-stage-in-a-bar-in-the-pink-rays_46833147_1.jpg',
  'https://customer-assets.emergentagent.com/job_9d65d3d0-8e4c-4ca7-97e3-3472b806edee/artifacts/3rjo6nvi_large-vecteezy_music-recording-studio-with-professional-equipment-and_34430986_large.jpg',
];

// Promotion card images
const promoImages = {
  instagram: 'https://images.pexels.com/photos/8488289/pexels-photo-8488289.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
  tiktok: 'https://images.pexels.com/photos/17781869/pexels-photo-17781869.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
  email: 'https://images.unsplash.com/photo-1705484228982-fd9655904a07?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwyfHxlbWFpbCUyMGtleWJvYXJkJTIwbGV0dGVycyUyMHNjcmFiYmxlfGVufDB8fHx8MTc3NTExNTQ2OHww&ixlib=rb-4.1.0&q=85',
  playlists: 'https://images.unsplash.com/photo-1748781208325-18107f54fa57?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjY2NzN8MHwxfHNlYXJjaHwyfHx2aW55bCUyMHJlY29yZCUyMHR1cm50YWJsZSUyMGNsb3NlJTIwdXB8ZW58MHx8fHwxNzc1MTE1NDY4fDA&ixlib=rb-4.1.0&q=85',
};
const studioImage = 'https://images.pexels.com/photos/7586656/pexels-photo-7586656.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940';

// Animated Color Text (purple/magenta/pink cycling) — KALMORI branding
const AnimatedColorText = ({ children, className = '' }) => (
  <span className={`animate-color-cycle ${className}`}>{children}</span>
);

// Typewriter for hero — large layout
const HeroTypewriterSequence = () => {
  const [charIndex, setCharIndex] = useState(0);
  const [desc, setDesc] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [descPhase, setDescPhase] = useState(false);
  const FULL_TEXT = "The G.O.A.T In Music Distribution";
  const DESC = "Get your music on Spotify, Apple Music, TikTok, YouTube, Tidal and more. Keep 100% ownership of your music and stay in control of your career.";

  useEffect(() => {
    let timeout;
    if (!descPhase) {
      if (charIndex < FULL_TEXT.length) timeout = setTimeout(() => setCharIndex(charIndex + 1), 80);
      else timeout = setTimeout(() => setDescPhase(true), 500);
    } else {
      if (!isDeleting) {
        if (desc.length < DESC.length) timeout = setTimeout(() => setDesc(DESC.slice(0, desc.length + 1)), 30);
        else timeout = setTimeout(() => setIsDeleting(true), 3000);
      } else {
        if (desc.length > 0) timeout = setTimeout(() => setDesc(DESC.slice(0, desc.length - 1)), 15);
        else timeout = setTimeout(() => setIsDeleting(false), 1000);
      }
    }
    return () => clearTimeout(timeout);
  }, [charIndex, desc, isDeleting, descPhase]);

  const typed = FULL_TEXT.slice(0, charIndex);
  // Split into line1 = "The G.O.A.T In" and line2 = "Music Distribution"
  const splitAt = 14; // "The G.O.A.T In" = 14 chars
  const line1 = typed.slice(0, Math.min(typed.length, splitAt));
  const line2 = typed.length > splitAt ? typed.slice(splitAt + 1) : '';

  const renderLine1 = () => {
    // "The" (0-2) = white, " " (3), "G.O.A.T" (4-10) = animated, " " (11), "In" (12-13) = white
    const parts = [];
    const thePart = line1.slice(0, Math.min(line1.length, 3));
    if (thePart) parts.push(<span key="the" className="text-white">{thePart}</span>);
    if (line1.length > 3) parts.push(<span key="s1" className="text-white"> </span>);
    const goat = line1.length > 4 ? line1.slice(4, Math.min(line1.length, 11)) : '';
    if (goat) parts.push(<AnimatedColorText key="goat">{goat}</AnimatedColorText>);
    if (line1.length > 11) parts.push(<span key="s2" className="text-white"> </span>);
    const inPart = line1.length > 12 ? line1.slice(12) : '';
    if (inPart) parts.push(<span key="in" className="text-white">{inPart}</span>);
    return parts;
  };

  const renderLine2 = () => {
    if (!line2) return null;
    return <AnimatedColorText>{line2}</AnimatedColorText>;
  };

  return (
    <div className="text-left">
      <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black leading-[0.95] tracking-tight mb-4">
        {renderLine1()}
        {!descPhase && charIndex <= splitAt && <span className="animate-blink text-[#7C4DFF]">|</span>}
      </h1>
      {(line2 || charIndex > splitAt) && (
        <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black leading-[0.95] tracking-tight mb-8">
          {renderLine2()}
          {!descPhase && charIndex > splitAt && <span className="animate-blink text-[#7C4DFF]">|</span>}
        </h2>
      )}
      <p className="text-base sm:text-lg text-gray-300 leading-relaxed max-w-xl min-h-[60px]">
        {desc}<span className={`animate-blink text-[#7C4DFF] ${!descPhase ? 'hidden' : ''}`}>|</span>
      </p>
    </div>
  );
};

// AnimatedButton component
const AnimatedButton = ({ children, onClick, className = '' }) => (
  <button onClick={onClick} className={`animate-btn-gradient text-white font-bold py-4 px-8 rounded-full flex items-center gap-3 tracking-[1px] hover:brightness-110 transition-all ${className}`}>
    {children}
  </button>
);

// Platform data
const platforms = [
  { name: 'Spotify', icon: <SpotifyLogo className="w-10 h-10" weight="fill" />, color: '#1DB954' },
  { name: 'Apple Music', icon: <AppleLogo className="w-10 h-10" weight="fill" />, color: '#FC3C44' },
  { name: 'YouTube', icon: <YoutubeLogo className="w-10 h-10" weight="fill" />, color: '#FF0000' },
  { name: 'TikTok', icon: <TiktokLogo className="w-10 h-10" weight="fill" />, color: '#00F2EA' },
  { name: 'Amazon', icon: <MusicNote className="w-10 h-10" weight="fill" />, color: '#00A8E1' },
  { name: 'Deezer', icon: <MusicNote className="w-10 h-10" weight="fill" />, color: '#FEAA2D' },
];

// Promotion channels
const promoChannels = [
  { name: 'Instagram', desc: 'Stories, Reels & Posts', icon: <InstagramLogo className="w-7 h-7" weight="fill" />, color: '#E4405F', image: promoImages.instagram },
  { name: 'TikTok', desc: 'Viral Marketing', icon: <TiktokLogo className="w-7 h-7" weight="fill" />, color: '#00F2EA', image: promoImages.tiktok },
  { name: 'Email', desc: 'Curator Outreach', icon: <Envelope className="w-7 h-7" weight="fill" />, color: '#FFD700', image: promoImages.email },
  { name: 'Playlists', desc: 'Editorial Pitching', icon: <Playlist className="w-7 h-7" weight="fill" />, color: '#1DB954', image: promoImages.playlists },
];

// Artist testimonials
const testimonials = [
  { name: 'Rising Star', quote: "Kalmori changed my life. I can distribute my music on my own terms, keeping 100% of my rights and earnings.", avatar: 'RS' },
  { name: 'Indie Producer', quote: "The best platform for independent artists. The analytics and AI features help me understand my audience better.", avatar: 'IP' },
  { name: 'Beat Maker', quote: "I recommend Kalmori to every artist I meet. They make distribution easy and manageable.", avatar: 'BM' },
];

const LandingPage = () => {
  const navigate = useNavigate();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [zoomScale, setZoomScale] = useState(1);
  const [featuredBeats, setFeaturedBeats] = useState([]);
  const [playingBeatId, setPlayingBeatId] = useState(null);
  const [customPage, setCustomPage] = useState(null);
  const [checkingCustom, setCheckingCustom] = useState(true);
  const audioRef = React.useRef(null);

  useEffect(() => {
    // Check for custom published layout first
    fetch(`${API}/pages/landing`)
      .then(r => r.json())
      .then(data => { if (data.published && data.blocks?.length) setCustomPage(data); })
      .catch(() => {})
      .finally(() => setCheckingCustom(false));

    axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/beats?limit=4`)
      .then(res => setFeaturedBeats(res.data.beats?.slice(0, 4) || []))
      .catch(() => {});
    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, []);

  const toggleBeat = (beat) => {
    if (playingBeatId === beat.id) {
      audioRef.current?.pause();
      audioRef.current = null;
      setPlayingBeatId(null);
    } else {
      audioRef.current?.pause();
      if (beat.audio_url) {
        const audio = new Audio(`${process.env.REACT_APP_BACKEND_URL}/api/beats/${beat.id}/stream`);
        audio.play().catch(() => {});
        audio.onended = () => setPlayingBeatId(null);
        audioRef.current = audio;
      }
      setPlayingBeatId(beat.id);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => setCurrentSlide((p) => (p + 1) % heroSlideImages.length), 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (currentSlide === 1) {
      setZoomScale(1);
      const zoomInterval = setInterval(() => setZoomScale(prev => Math.min(prev + 0.009, 1.25)), 1000);
      return () => clearInterval(zoomInterval);
    } else setZoomScale(1);
  }, [currentSlide]);

  // If a custom layout is published, render it instead of the default
  if (!checkingCustom && customPage) {
    return (
      <PublicLayout>
        <DynamicPageRenderer slug="landing" />
        <GlobalFooter />
      </PublicLayout>
    );
  }

  return (
    <PublicLayout>
      {/* CSS Animations */}
      <style>{`
        @keyframes colorCycle { 0%{color:#7C4DFF} 33%{color:#E040FB} 66%{color:#FF4081} 100%{color:#7C4DFF} }
        @keyframes taglineCycle { 0%{color:#FF4444} 50%{color:#FFD700} 100%{color:#FF4444} }
        @keyframes btnGradient { 0%{background:#7C4DFF} 33%{background:#E040FB} 66%{background:#FF4081} 100%{background:#7C4DFF} }
        @keyframes outlineCycle { 0%{border-color:#7C4DFF} 33%{border-color:#E040FB} 66%{border-color:#FF4081} 100%{border-color:#7C4DFF} }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes floatUp { 0%{opacity:0;transform:translateY(40px)} 100%{opacity:1;transform:translateY(0)} }
        .animate-color-cycle { animation: colorCycle 6s ease-in-out infinite; }
        .animate-tagline-cycle { animation: taglineCycle 4s ease-in-out infinite; }
        .animate-btn-gradient { animation: btnGradient 6s ease-in-out infinite; }
        .animate-blink { animation: blink 1s step-end infinite; }
        .float-up { animation: floatUp 0.8s ease-out forwards; }
        .float-up-d1 { animation: floatUp 0.8s ease-out 0.15s forwards; opacity:0; }
        .float-up-d2 { animation: floatUp 0.8s ease-out 0.3s forwards; opacity:0; }
        .float-up-d3 { animation: floatUp 0.8s ease-out 0.45s forwards; opacity:0; }
      `}</style>

      {/* ===== HERO SECTION — Full-Width Large Typography ===== */}
      <section className="relative min-h-screen overflow-hidden" data-testid="hero-section">
        {heroSlideImages.map((img, i) => (
          <div key={i} className="absolute inset-0 transition-opacity duration-[2000ms]" style={{ opacity: currentSlide === i ? 1 : 0 }}>
            <img src={img} alt="" className="w-full h-full object-cover transition-transform duration-[30000ms]"
              style={{ transform: currentSlide === i ? `scale(${i === 1 ? zoomScale : 1.1})` : 'scale(1)' }} />
          </div>
        ))}
        <div className="absolute inset-0 bg-gradient-to-r from-black via-black/80 to-black/40" />
        <div className="relative z-10 max-w-7xl mx-auto flex items-center min-h-screen px-6 sm:px-12 lg:px-20 py-20">
          <div className="max-w-3xl">
            <HeroTypewriterSequence />
            <div className="mt-10 flex flex-wrap gap-4 float-up-d2">
              <Link to="/register">
                <button className="animate-btn-gradient px-10 py-4 rounded-full text-white font-bold text-sm tracking-[2px] flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/20" data-testid="hero-cta-btn">
                  DISTRIBUTE MY MUSIC ONLINE <ArrowRight className="w-5 h-5" />
                </button>
              </Link>
            </div>
            <p className="mt-6 text-sm text-gray-400 float-up-d3">Unlimited Releases starting at $20/year. Keep 100% of your royalties.</p>
            {/* Slide dots */}
            <div className="mt-8 flex gap-2">
              {heroSlideImages.map((_, i) => (
                <button key={i} onClick={() => setCurrentSlide(i)}
                  className={`h-1 rounded-full transition-all ${currentSlide === i ? 'bg-[#E53935] w-12' : 'bg-white/30 w-6'}`} />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===== UNLIMITED DISTRIBUTION BANNER ===== */}
      <section className="py-24 px-6 bg-black" data-testid="distribution-section">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-[1.05] tracking-tight text-white mb-6">
                Unlimited Distribution Starting at <AnimatedColorText>$20/year</AnimatedColorText>
              </h2>
              <p className="text-lg text-gray-400 leading-relaxed mb-8 max-w-xl">
                Increase the reach of your music across the most popular stores & platforms. Empower yourself with unlimited distribution and get your music heard by a global audience.
              </p>
              <p className="text-base text-gray-300 font-medium">
                Keep <span className="text-[#E040FB] font-bold">100% ownership</span> of your music, maintaining creative control and authority in your music career.
              </p>
            </div>
            {/* Platform Logos Grid */}
            <div>
              <div className="grid grid-cols-3 gap-4">
                {platforms.map((p, i) => (
                  <div key={i} className="bg-[#111] rounded-2xl py-8 px-4 flex flex-col items-center gap-3 border border-white/5 hover:border-white/20 transition-all group" data-testid={`platform-${p.name.toLowerCase().replace(' ', '-')}`}>
                    <div style={{ color: p.color }} className="group-hover:scale-110 transition-transform">{p.icon}</div>
                    <span className="text-sm font-semibold text-white">{p.name}</span>
                  </div>
                ))}
              </div>
              <div className="text-center mt-6">
                <button onClick={() => navigate('/stores')} className="text-[#E040FB] text-sm font-bold tracking-wider inline-flex items-center gap-2 hover:gap-3 transition-all" data-testid="view-all-stores-btn">
                  VIEW ALL 150+ STORES <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== WHAT IS KALMORI — Large Text Block ===== */}
      <section className="py-24 px-6 bg-[#0a0a0a]" data-testid="what-is-section">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-4xl">
            <p className="text-xs font-bold text-[#E040FB] tracking-[4px] mb-4">ABOUT US</p>
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-[1.05] tracking-tight text-white mb-8">
              What is <AnimatedColorText>Kalmori?</AnimatedColorText>
            </h2>
            <h3 className="text-xl sm:text-2xl font-bold text-gray-300 mb-6">Your Independent Music Distribution Company</h3>
            <p className="text-lg text-gray-400 leading-relaxed mb-6">
              Kalmori is a leading global platform empowering independent artists to build sustainable careers. Through innovative technology and artist-first services, we offer distribution, publishing administration, and promotional tools that help musicians grow their audience and revenue.
            </p>
            <p className="text-lg text-gray-400 leading-relaxed mb-10">
              As a pioneer in indie music distribution, Kalmori is dedicated to making music accessible while keeping artists in full control of their creative work.
            </p>
            <button onClick={() => navigate('/pricing')} className="px-10 py-4 rounded-full animate-btn-gradient text-white text-sm font-bold tracking-[2px] inline-flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/20" data-testid="see-plans-btn">
              SEE OUR DISTRIBUTION PLANS <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* ===== WHY CHOOSE KALMORI — Two Column ===== */}
      <section className="py-24 px-6 bg-black" data-testid="why-choose-section">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
            <div>
              <p className="text-xs font-bold text-[#E53935] tracking-[4px] mb-4">WHY CHOOSE US</p>
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-[1.05] tracking-tight text-white mb-4">
                Why Choose <AnimatedColorText>Kalmori</AnimatedColorText>
              </h2>
              <h3 className="text-xl sm:text-2xl font-bold text-gray-300 mb-10">
                Best Choice of Music Distribution Companies
              </h3>

              <div className="space-y-6">
                {[
                  'Unlimited music distribution worldwide',
                  'Direct access to 150+ digital stores and streaming services',
                  'Keep 100% ownership and control of your master recordings',
                  'Get paid directly with transparent royalty reporting and no hidden fees',
                  'Free ISRC and UPC codes included with every release',
                  'AI-powered metadata suggestions and analytics insights',
                  'Dedicated support team available to help you succeed',
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-4 group">
                    <div className="w-6 h-6 rounded-full bg-[#E040FB] flex items-center justify-center flex-shrink-0 mt-0.5 group-hover:scale-110 transition-transform">
                      <Check className="w-3.5 h-3.5 text-white" weight="bold" />
                    </div>
                    <p className="text-base text-gray-300 leading-relaxed">{item}</p>
                  </div>
                ))}
              </div>

              <div className="mt-10">
                <button onClick={() => navigate('/services')} className="px-10 py-4 rounded-full animate-btn-gradient text-white text-sm font-bold tracking-[2px] inline-flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/20" data-testid="all-services-btn">
                  ALL OUR SERVICES <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Image Side */}
            <div className="relative hidden lg:block">
              <div className="rounded-3xl overflow-hidden shadow-2xl shadow-[#7C4DFF]/10">
                <img src={studioImage} alt="Recording studio" className="w-full h-[600px] object-cover" />
              </div>
              <div className="absolute -bottom-6 -left-6 bg-[#111] border border-white/10 rounded-2xl p-6 shadow-xl">
                <p className="text-3xl font-black text-[#E040FB]">150+</p>
                <p className="text-sm text-gray-400">Streaming Platforms</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== STREAM & DISTRIBUTE — Full Width Text ===== */}
      <section className="py-24 px-6 bg-[#0a0a0a]" data-testid="stream-distribute-section">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="order-2 lg:order-1">
              <div className="rounded-3xl overflow-hidden">
                <img src={heroSlideImages[1]} alt="Distribution" className="w-full h-[450px] object-cover" />
              </div>
            </div>
            <div className="order-1 lg:order-2">
              <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white mb-4">
                Stream & Distribute Your Music <AnimatedColorText>Without a Label</AnimatedColorText>
              </h2>
              <h3 className="text-xl font-bold text-gray-300 mb-6">Sell Your Music Online Worldwide</h3>
              <p className="text-lg text-gray-400 leading-relaxed mb-8">
                Before platforms like Kalmori, artists needed a label to get their music sold online. We changed that. Choose an unlimited distribution plan, upload your music, and we'll do the rest. Your music will hit top digital stores in no time.
              </p>
              <button onClick={() => navigate('/register')} className="px-10 py-4 rounded-full animate-btn-gradient text-white text-sm font-bold tracking-[2px] inline-flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/20" data-testid="sell-music-btn">
                SELL YOUR MUSIC <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ===== ARTIST TESTIMONIALS ===== */}
      <section className="py-24 px-6 bg-black" data-testid="testimonials-section">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-xs font-bold text-[#E040FB] tracking-[4px] mb-4">TESTIMONIALS</p>
            <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white">
              What Are Artists Saying About <AnimatedColorText>Kalmori?</AnimatedColorText>
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <div key={i} className="bg-[#111] rounded-3xl p-8 border border-white/5 hover:border-[#E040FB]/30 transition-all group">
                <Quotes className="w-8 h-8 text-[#7C4DFF] mb-6 group-hover:text-[#E040FB] transition-colors" weight="fill" />
                <p className="text-base text-gray-300 leading-relaxed mb-8">"{t.quote}"</p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center text-white font-bold text-sm">
                    {t.avatar}
                  </div>
                  <div>
                    <p className="font-bold text-white">{t.name}</p>
                    <p className="text-xs text-gray-500">Kalmori Artist</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== POWERFUL FEATURES ===== */}
      <section className="py-24 px-6 bg-[#0a0a0a]" data-testid="features-section">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-xs font-bold text-[#7C4DFF] tracking-[4px] mb-4">ALL-IN-ONE PLATFORM</p>
            <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white mb-4">
              Everything You Need to <AnimatedColorText>Win</AnimatedColorText>
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              More than just distribution. Kalmori gives you AI-powered tools, deep analytics, and everything to build a real music career.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: <Brain className="w-7 h-7" weight="fill" />, color: '#E040FB', title: 'AI Release Strategy', desc: 'Get AI-powered release plans with optimal timing, playlist targeting, and marketing recommendations tailored to your genre.' },
              { icon: <ChartLineUp className="w-7 h-7" weight="fill" />, color: '#1DB954', title: 'Real-Time Analytics', desc: 'Track streams, revenue, fan demographics, peak listening hours, and geographic data across all platforms in one dashboard.' },
              { icon: <CurrencyDollar className="w-7 h-7" weight="fill" />, color: '#FFD700', title: 'Revenue & Royalty Calculator', desc: 'See exactly what you earn per stream on each platform. Model different scenarios with our what-if royalty calculator.' },
              { icon: <MusicNotes className="w-7 h-7" weight="fill" />, color: '#9C27B0', title: 'Beat Marketplace', desc: 'Browse, preview, and purchase professional instrumentals with 4-tier licensing. Producers sell beats with auto-generated contracts.' },
              { icon: <FileText className="w-7 h-7" weight="fill" />, color: '#FF6B6B', title: 'Digital Contracts & E-Sign', desc: 'Every beat purchase generates a legally-binding PDF contract with e-signatures. Full admin tracking and audit trail.' },
              { icon: <Waveform className="w-7 h-7" weight="fill" />, color: '#00BCD4', title: 'AI Audio Watermarking', desc: 'AI-generated voice tags automatically overlaid on beat previews. Clean versions unlock after purchase for full protection.' },
              { icon: <ChatCircleDots className="w-7 h-7" weight="fill" />, color: '#2196F3', title: 'In-App Messaging', desc: 'Real-time chat with file sharing, audio messages, read receipts, and typing indicators. Collaborate without leaving the platform.' },
              { icon: <HandCoins className="w-7 h-7" weight="fill" />, color: '#FF9800', title: 'Producer Royalty Splits', desc: 'Auto-calculated royalty splits between producers and artists on every beat stream and purchase. Credited directly to wallets.' },
              { icon: <Users className="w-7 h-7" weight="fill" />, color: '#E040FB', title: 'Collaboration Hub', desc: 'Post collaboration opportunities, find vocalists, producers, and engineers. Build your network and create together.' },
              { icon: <ShareNetwork className="w-7 h-7" weight="fill" />, color: '#00BCD4', title: 'Artist Public Profile', desc: 'Your shareable link-in-bio page with audio previews, custom theme colors, QR code sharing, and pre-save campaigns.' },
              { icon: <Trophy className="w-7 h-7" weight="fill" />, color: '#FF6B6B', title: 'Release Leaderboard', desc: 'See how your releases stack up. Track momentum, hot streaks, and compete with your own catalog.' },
              { icon: <Target className="w-7 h-7" weight="fill" />, color: '#7C4DFF', title: 'Goal Tracking & Milestones', desc: 'Set stream goals, revenue targets, and geographic reach milestones. Watch your progress and celebrate achievements.' },
            ].map((f, i) => (
              <div key={i} className="bg-[#111] rounded-2xl p-7 border border-white/5 hover:border-white/15 transition-all group" data-testid={`feature-card-${i}`}>
                <div className="w-12 h-12 rounded-xl mb-5 flex items-center justify-center group-hover:scale-110 transition-transform"
                  style={{ backgroundColor: `${f.color}15`, color: f.color }}>
                  {f.icon}
                </div>
                <h3 className="text-base font-bold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== PLATFORM HIGHLIGHTS — Detailed Feature Showcase ===== */}
      <section className="py-24 px-6 bg-black" data-testid="highlights-section">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-xs font-bold text-[#E040FB] tracking-[4px] mb-4">WHAT SETS US APART</p>
            <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white">
              Features That <AnimatedColorText>Actually Matter</AnimatedColorText>
            </h2>
          </div>

          {/* Highlight 1: Beat Marketplace */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-24">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#9C27B0]/10 border border-[#9C27B0]/30 rounded-full text-[#9C27B0] text-xs font-bold mb-4">
                <MusicNotes className="w-3.5 h-3.5" weight="fill" /> BEAT MARKETPLACE
              </div>
              <h3 className="text-3xl sm:text-4xl font-black text-white mb-4 leading-tight">
                Buy & Sell Beats with<br/><span className="text-[#E040FB]">Full Legal Protection</span>
              </h3>
              <p className="text-base text-gray-400 leading-relaxed mb-6">
                Our marketplace handles the entire beat licensing workflow — from preview to purchase. Every transaction generates a legally-binding PDF contract with digital signatures, auto-calculated royalty splits, and AI-powered audio watermarks to protect your work.
              </p>
              <div className="space-y-3">
                {['4-tier licensing (Basic, Premium, Exclusive, Unlimited)', 'AI-generated voice tag watermarks on previews', 'Auto PDF contracts with e-signatures', 'Producer royalty splits on every stream & sale'].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-[#E040FB] flex-shrink-0" weight="fill" />
                    <p className="text-sm text-gray-300">{item}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="rounded-2xl overflow-hidden border border-white/10 bg-[#111] p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-[#9C27B0] to-[#E040FB] flex items-center justify-center"><MusicNote className="w-7 h-7 text-white" weight="fill" /></div>
                  <div>
                    <p className="text-white font-bold">Midnight Vibes</p>
                    <p className="text-xs text-gray-500">120 BPM &middot; Am &middot; Hip-Hop/R&B</p>
                  </div>
                  <div className="ml-auto text-right">
                    <p className="text-[#FFD700] font-bold text-lg">$29.99</p>
                    <p className="text-[10px] text-gray-500">Basic Lease</p>
                  </div>
                </div>
                <div className="h-12 bg-[#0A0A0A] rounded-lg flex items-center px-4 gap-1 mb-4">
                  {[...Array(40)].map((_, i) => (
                    <div key={i} className="w-1 bg-[#E040FB] rounded-full" style={{ height: `${6 + Math.random() * 26}px`, opacity: 0.3 + Math.random() * 0.7 }} />
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-[#0A0A0A] rounded-lg p-3 border border-white/5">
                    <FileText className="w-5 h-5 text-[#FF6B6B] mb-1" weight="fill" />
                    <p className="text-xs font-bold text-white">Auto Contract</p>
                    <p className="text-[10px] text-gray-500">PDF + E-Sign</p>
                  </div>
                  <div className="bg-[#0A0A0A] rounded-lg p-3 border border-white/5">
                    <Waveform className="w-5 h-5 text-[#00BCD4] mb-1" weight="fill" />
                    <p className="text-xs font-bold text-white">Voice Tag</p>
                    <p className="text-[10px] text-gray-500">AI Watermark</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Highlight 2: Collaboration + Messaging */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-24">
            <div className="order-2 lg:order-1">
              <div className="rounded-2xl overflow-hidden border border-white/10 bg-[#111] p-5">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#2196F3] to-[#00BCD4] flex items-center justify-center text-white text-xs font-bold">JT</div>
                  <div className="flex-1">
                    <p className="text-xs font-bold text-white">Jay Turner</p>
                    <p className="text-[10px] text-[#1DB954]">Online</p>
                  </div>
                </div>
                <div className="space-y-3 mb-4">
                  <div className="flex justify-start"><div className="bg-[#1a1a1a] rounded-2xl rounded-tl-sm px-4 py-2 max-w-[75%]"><p className="text-xs text-gray-300">Hey, I heard your latest beat. Let's collab!</p><p className="text-[9px] text-gray-600 mt-1">2:34 PM</p></div></div>
                  <div className="flex justify-end"><div className="bg-[#7C4DFF] rounded-2xl rounded-tr-sm px-4 py-2 max-w-[75%]"><p className="text-xs text-white">Definitely! I'll send the stems now</p><p className="text-[9px] text-white/50 mt-1">2:35 PM &middot; Read</p></div></div>
                  <div className="flex justify-start"><div className="bg-[#1a1a1a] rounded-2xl rounded-tl-sm px-4 py-2"><div className="flex items-center gap-2"><div className="w-8 h-8 rounded-lg bg-[#E040FB]/20 flex items-center justify-center"><MusicNote className="w-4 h-4 text-[#E040FB]" weight="fill" /></div><div><p className="text-xs text-white font-medium">collab_track.wav</p><p className="text-[9px] text-gray-500">3.2 MB</p></div></div></div></div>
                </div>
                <div className="bg-[#0A0A0A] rounded-full px-4 py-2 flex items-center gap-2">
                  <span className="text-xs text-gray-500 flex-1">Type a message...</span>
                  <div className="w-6 h-6 rounded-full bg-[#7C4DFF] flex items-center justify-center"><ArrowRight className="w-3 h-3 text-white" /></div>
                </div>
              </div>
            </div>
            <div className="order-1 lg:order-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#2196F3]/10 border border-[#2196F3]/30 rounded-full text-[#2196F3] text-xs font-bold mb-4">
                <ChatCircleDots className="w-3.5 h-3.5" weight="fill" /> COLLABORATION
              </div>
              <h3 className="text-3xl sm:text-4xl font-black text-white mb-4 leading-tight">
                Connect, Chat &<br/><span className="text-[#2196F3]">Create Together</span>
              </h3>
              <p className="text-base text-gray-400 leading-relaxed mb-6">
                Find collaborators in the Collab Hub, then work together seamlessly with built-in real-time messaging. Share files, audio clips, and ideas — all without leaving Kalmori.
              </p>
              <div className="space-y-3">
                {['Real-time chat with read receipts & typing indicators', 'File and audio sharing in conversations', 'Collab Hub to find producers, vocalists & engineers', 'Direct messaging from any profile'].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-[#2196F3] flex-shrink-0" weight="fill" />
                    <p className="text-sm text-gray-300">{item}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Highlight 3: Artist Profile */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#00BCD4]/10 border border-[#00BCD4]/30 rounded-full text-[#00BCD4] text-xs font-bold mb-4">
                <Palette className="w-3.5 h-3.5" weight="fill" /> ARTIST PROFILES
              </div>
              <h3 className="text-3xl sm:text-4xl font-black text-white mb-4 leading-tight">
                Your Link-in-Bio,<br/><span className="text-[#00BCD4]">Powered by Music</span>
              </h3>
              <p className="text-base text-gray-400 leading-relaxed mb-6">
                Every artist on Kalmori gets a beautiful, shareable public profile page. Fans can preview your music, pre-save upcoming releases, and find all your social links in one place. Customize your theme color and share via QR code.
              </p>
              <div className="space-y-3">
                {['Inline audio previews for all releases', 'Custom theme colors to match your brand', 'QR code generator for merch & social', 'Pre-save campaigns to build hype'].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-[#00BCD4] flex-shrink-0" weight="fill" />
                    <p className="text-sm text-gray-300">{item}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="rounded-2xl overflow-hidden border border-white/10 bg-[#111] p-6 max-w-xs mx-auto">
                <div className="flex flex-col items-center text-center mb-4">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#00BCD4] to-[#E040FB] flex items-center justify-center text-white text-2xl font-extrabold mb-3">A</div>
                  <p className="text-lg font-extrabold text-white">Artist Name</p>
                  <p className="text-[10px] uppercase tracking-[0.15em] text-gray-500">Hip-Hop &middot; Atlanta</p>
                </div>
                <div className="flex justify-center gap-2 mb-4">
                  {[SpotifyLogo, InstagramLogo, TwitterLogo].map((Icon, i) => (
                    <div key={i} className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center"><Icon className="w-4 h-4 text-white/60" weight="fill" /></div>
                  ))}
                </div>
                <div className="space-y-2 mb-4">
                  {['Latest Single', 'Album Drop'].map((t, i) => (
                    <div key={i} className="flex items-center gap-3 bg-[#0A0A0A] rounded-xl p-2.5">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#7C4DFF]/30 to-[#E040FB]/30 flex items-center justify-center flex-shrink-0"><MusicNote className="w-4 h-4 text-[#E040FB]" weight="fill" /></div>
                      <div className="flex-1 min-w-0"><p className="text-xs font-semibold text-white truncate">{t}</p><div className="h-1 bg-white/10 rounded-full mt-1 overflow-hidden"><div className="h-full bg-[#00BCD4] rounded-full" style={{ width: `${30 + i * 25}%` }} /></div></div>
                      <Play className="w-3.5 h-3.5 text-white/40" weight="fill" />
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-center gap-2">
                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 rounded-full text-[10px] text-white/60"><Copy className="w-3 h-3" /> Share</div>
                  <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#00BCD4]/10 border border-[#00BCD4]/30 rounded-full text-[10px] text-[#00BCD4]"><QrCode className="w-3 h-3" /> QR Code</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== PROMOTION SERVICES ===== */}
      <section className="py-24 px-6 bg-[#0a0a0a]" data-testid="promotion-section">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
            <div>
              <p className="text-xs font-bold text-[#E040FB] tracking-[4px] mb-4">PROMOTION SERVICES</p>
              <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white mb-6">
                Promotion <AnimatedColorText>Services</AnimatedColorText>
              </h2>
              <p className="text-lg text-gray-400 leading-relaxed mb-8">
                Boost your reach with our professional promotion services. Get your music in front of the right audience across all major social platforms.
              </p>
              <button onClick={() => navigate('/promoting')} className="text-[#E040FB] text-sm font-bold tracking-[2px] inline-flex items-center gap-2 hover:gap-3 transition-all" data-testid="learn-promo-link">
                LEARN MORE ABOUT PROMOTION <ArrowRight className="w-4 h-4" />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {promoChannels.map((ch, i) => (
                <div key={i} className="bg-[#111] rounded-2xl overflow-hidden border border-white/5 hover:border-white/20 transition-all group" data-testid={`promo-card-${ch.name.toLowerCase()}`}>
                  <div className="h-32 overflow-hidden relative">
                    <img src={ch.image} alt={ch.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#111] to-transparent" />
                  </div>
                  <div className="p-5 text-center">
                    <div className="w-10 h-10 rounded-full mx-auto mb-3 flex items-center justify-center" style={{ backgroundColor: `${ch.color}15`, color: ch.color }}>
                      {ch.icon}
                    </div>
                    <h3 className="text-base font-bold text-white">{ch.name}</h3>
                    <p className="text-sm text-gray-400 mt-1">{ch.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===== NEED BEATS / INSTRUMENTALS ===== */}
      <section className="py-24 px-6 bg-black" data-testid="need-beats-section">
        <div className="max-w-7xl mx-auto">
          <div className="rounded-3xl overflow-hidden relative" style={{ background: 'linear-gradient(135deg, #9C27B0 0%, #E040FB 50%, #7C4DFF 100%)' }}>
            <div className="absolute inset-0 bg-black/10" />
            <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center p-10 sm:p-16">
              <div>
                <MusicNotes className="w-16 h-16 text-white mb-6" weight="fill" />
                <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white mb-6">
                  Need Beats or Instrumentals?
                </h2>
                <p className="text-lg text-white/80 leading-relaxed mb-8">
                  Can't make your own beats? No problem! Get professional instrumentals with full rights or lease options.
                </p>
                <Link to="/instrumentals">
                  <button className="bg-white px-10 py-4 rounded-full font-bold text-sm tracking-[2px] flex items-center gap-3 text-[#9C27B0] hover:brightness-95 transition-all shadow-lg" data-testid="request-beat-btn">
                    REQUEST A BEAT <ArrowRight className="w-5 h-5" />
                  </button>
                </Link>
              </div>
              <div className="space-y-5">
                {[
                  'Exclusive Rights Available',
                  'Affordable Lease Options',
                  'All Genres: Hip-Hop, R&B, Afrobeats, Dancehall',
                  'Custom Beats on Request',
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
                      <Check className="w-4 h-4 text-white" weight="bold" />
                    </div>
                    <p className="text-lg text-white font-medium">{item}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== MAXIMIZE EARNINGS — Publishing ===== */}
      <section className="py-24 px-6 bg-black" data-testid="publishing-section">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white mb-6">
                Maximize Your Earnings with Music <AnimatedColorText>Publishing</AnimatedColorText>
              </h2>
              <p className="text-lg text-gray-400 leading-relaxed mb-8">
                Distribution isn't the only way to make money. Your original songs generate publishing revenue with every stream, video creation, view, or live performance worldwide.
              </p>
              <div className="space-y-4 mb-10">
                {[
                  'Collecting your royalties globally/worldwide',
                  'Tracking publishing royalties from Spotify, YouTube, TikTok, Radio',
                  'Offering advanced analytics on royalty sources',
                  'All while you keep 100% of your copyrights',
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-[#E040FB] flex-shrink-0" weight="bold" />
                    <p className="text-base text-gray-300">{item}</p>
                  </div>
                ))}
              </div>
              <button onClick={() => navigate('/publishing')} className="px-10 py-4 rounded-full animate-btn-gradient text-white text-sm font-bold tracking-[2px] inline-flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/20" data-testid="publishing-btn">
                LEARN MORE <ArrowRight className="w-5 h-5" />
              </button>
            </div>
            <div className="rounded-3xl overflow-hidden shadow-2xl shadow-[#E040FB]/10">
              <img src={heroSlideImages[0]} alt="Publishing" className="w-full h-[450px] object-cover" />
            </div>
          </div>
        </div>
      </section>

      {/* ===== ACCELERATOR — Reach More Fans ===== */}
      <section className="py-24 px-6 bg-[#0a0a0a]" data-testid="accelerator-section">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="order-2 lg:order-1">
              <div className="rounded-3xl overflow-hidden">
                <img src={studioImage} alt="Accelerator" className="w-full h-[450px] object-cover" />
              </div>
            </div>
            <div className="order-1 lg:order-2">
              <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white mb-4">
                Reach More Fans.<br/>Increase Your Streams.<br/>Grow Your Music <AnimatedColorText>Career.</AnimatedColorText>
              </h2>
              <h3 className="text-xl font-bold text-gray-300 mb-6">Join Kalmori and speed up your success!</h3>
              <p className="text-lg text-gray-400 leading-relaxed mb-8">
                Kalmori leverages innovative, in-house tools to elevate the ideal tracks for greater audience reach. Our comprehensive suite of tools, analytics, and promotion services gives you everything you need.
              </p>
              <div className="flex flex-wrap gap-4">
                <button onClick={() => navigate('/register')} className="px-10 py-4 rounded-full animate-btn-gradient text-white text-sm font-bold tracking-[2px] inline-flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/20" data-testid="accelerator-signup-btn">
                  SIGN UP <ArrowRight className="w-5 h-5" />
                </button>
                <button onClick={() => navigate('/about')} className="px-10 py-4 rounded-full border-2 border-[#7C4DFF] text-white text-sm font-bold tracking-[2px] hover:brightness-110 transition-all" style={{ animation: 'outlineCycle 6s ease-in-out infinite' }} data-testid="accelerator-report-btn">
                  READ MORE
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== BUILT FOR YOUNG ARTISTS — with stats ===== */}
      <section className="py-24 px-6 bg-black" data-testid="young-artists-section">
        <div className="max-w-7xl mx-auto">
          {/* Stats row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 mb-20">
            {[
              { value: '150+', label: 'Streaming Platforms', color: '#E040FB' },
              { value: '100%', label: 'Your Royalties', color: '#1DB954' },
              { value: '24/7', label: 'Analytics Dashboard', color: '#7C4DFF' },
              { value: 'AI', label: 'Powered Strategy', color: '#FFD700' },
            ].map((s, i) => (
              <div key={i} className="text-center p-6 bg-[#111] rounded-2xl border border-white/5" data-testid={`stat-card-${i}`}>
                <p className="text-4xl sm:text-5xl font-black" style={{ color: s.color }}>{s.value}</p>
                <p className="text-sm text-gray-400 mt-2 font-medium">{s.label}</p>
              </div>
            ))}
          </div>

          <div className="text-center max-w-3xl mx-auto">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center mx-auto mb-8 shadow-lg shadow-[#7C4DFF]/30">
              <Rocket className="w-10 h-10 text-white" weight="fill" />
            </div>
            <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white mb-6">Built for Young Artists & Producers</h2>
            <p className="text-lg text-gray-400 leading-relaxed mb-4">
              Whether you're just starting out or ready to take your career to the next level, Kalmori provides the tools, distribution, and support you need to succeed in the music industry.
            </p>
            <p className="text-base text-gray-500 leading-relaxed">
              Upload your first track, get AI-powered release strategies, build your fanbase with real-time analytics, and share your artist profile with the world. All from one platform.
            </p>
          </div>
        </div>
      </section>

      {/* ===== FEATURED BEATS ===== */}
      {featuredBeats.length > 0 && (
        <section className="py-20 px-6 bg-black" data-testid="featured-beats-section">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12">
              <p className="text-xs font-bold text-[#E040FB] tracking-[4px] mb-4">FROM OUR CATALOG</p>
              <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-white leading-[1.1]">Featured Beats</h2>
              <p className="text-gray-400 mt-3 text-base">Preview our latest instrumentals — tap to play</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
              {featuredBeats.map((beat) => (
                <div key={beat.id} className="bg-[#111] rounded-2xl p-5 border border-white/5 hover:border-[#E040FB]/30 transition-all group" data-testid={`featured-beat-${beat.id}`}>
                  <div className="flex items-center gap-3 mb-4">
                    <button onClick={() => toggleBeat(beat)}
                      className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-all ${
                        playingBeatId === beat.id ? 'bg-[#E040FB] scale-110' : 'bg-white/10 group-hover:bg-white/20'
                      }`} data-testid={`play-featured-${beat.id}`}>
                      {playingBeatId === beat.id ? <Pause className="w-4 h-4 text-white" weight="fill" /> : <Play className="w-4 h-4 text-white" weight="fill" />}
                    </button>
                    <div className="min-w-0">
                      <h4 className="text-sm font-bold text-white truncate">{beat.title}</h4>
                      <p className="text-xs text-gray-500">{beat.genre}</p>
                    </div>
                  </div>
                  {playingBeatId === beat.id && (
                    <div className="flex items-end gap-[3px] h-6 mb-3 justify-center">
                      {[...Array(12)].map((_, i) => (
                        <div key={i} className="w-1.5 bg-[#E040FB] rounded-full animate-pulse"
                          style={{ height: `${8 + Math.random() * 16}px`, animationDelay: `${i * 0.05}s`, animationDuration: `${0.3 + Math.random() * 0.4}s` }} />
                      ))}
                    </div>
                  )}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{beat.bpm} BPM &middot; {beat.key}</span>
                    <span className="text-[#E040FB] font-semibold">${beat.prices?.basic_lease || '29.99'}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="text-center">
              <button onClick={() => navigate('/instrumentals')} className="px-10 py-4 rounded-full animate-btn-gradient text-white text-sm font-bold tracking-[2px] inline-flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/20" data-testid="browse-all-beats-btn">
                BROWSE ALL BEATS <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </section>
      )}

      {/* ===== PRICING QUICK SECTION ===== */}
      <section className="py-24 px-6 bg-[#0a0a0a]" data-testid="pricing-section">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-xs font-bold text-[#E040FB] tracking-[4px] mb-4">SIMPLE PRICING</p>
            <h2 className="text-4xl sm:text-5xl font-black leading-[1.05] tracking-tight text-white">
              Plans That <AnimatedColorText>Scale</AnimatedColorText> With You
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              { name: 'FREE', price: '$0', desc: 'Start distributing with revenue share', color: '#4CAF50', features: ['All platforms', '15-20% rev share', 'Basic analytics'] },
              { name: 'SINGLE', price: '$20/yr', desc: 'Perfect for single releases', color: '#7C4DFF', features: ['Up to 3 tracks', '100% royalties', 'Free ISRC codes'] },
              { name: 'ALBUM', price: '$75/yr', desc: 'Best value for full albums', color: '#FFD700', highlight: true, features: ['7+ tracks', 'Priority support', 'Free ISRC & UPC'] },
            ].map((plan, i) => (
              <div key={i} className={`bg-[#111] rounded-3xl p-8 border-2 ${plan.highlight ? 'border-[#FFD700] relative' : 'border-white/5'} hover:border-[#E040FB]/30 transition-all`} data-testid={`home-plan-${plan.name.toLowerCase().replace(/\s/g, '-')}`}>
                {plan.highlight && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-[#FFD700] text-black text-xs font-bold tracking-wider">
                    BEST DEAL
                  </div>
                )}
                <div className="text-center mb-6">
                  <p className="text-4xl font-black" style={{ color: plan.color }}>{plan.price}</p>
                  <h3 className="text-lg font-bold text-white mt-2">{plan.name}</h3>
                  <p className="text-sm text-gray-400 mt-1">{plan.desc}</p>
                </div>
                <div className="space-y-3">
                  {plan.features.map((f, j) => (
                    <div key={j} className="flex items-center gap-2 text-sm text-gray-300">
                      <Check className="w-4 h-4 text-[#E040FB]" weight="bold" /> {f}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="text-center mt-12 flex flex-col sm:flex-row gap-4 justify-center">
            <button onClick={() => navigate('/register')} className="px-10 py-4 rounded-full animate-btn-gradient text-white text-sm font-bold tracking-[2px] inline-flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/20" data-testid="home-start-free-btn">
              START FREE <ArrowRight className="w-4 h-4" />
            </button>
            <button onClick={() => navigate('/pricing')} className="px-10 py-4 rounded-full border-2 border-[#7C4DFF] text-white text-sm font-bold tracking-[2px] hover:brightness-110 transition-all" style={{ animation: 'outlineCycle 6s ease-in-out infinite' }} data-testid="home-pricing-btn">
              ALL PRICING
            </button>
          </div>
        </div>
      </section>

      {/* ===== READY TO START JOURNEY — Gradient CTA ===== */}
      <section className="py-32 px-6 text-center relative overflow-hidden" data-testid="journey-section">
        <div className="absolute inset-0 bg-gradient-to-br from-[#7C4DFF]/30 via-[#E040FB]/20 to-[#FF4081]/30" />
        <div className="absolute inset-0 bg-black/50" />
        <div className="relative z-10 max-w-3xl mx-auto">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-[1.05] tracking-tight text-white mb-6">
            Ready to Start Your Journey?
          </h2>
          <p className="text-lg text-gray-300 mb-10 max-w-lg mx-auto">Join thousands of artists distributing their music worldwide with Kalmori.</p>
          <Link to="/register">
            <button className="animate-btn-gradient text-white px-12 py-5 rounded-full font-bold text-sm tracking-[2px] inline-flex items-center gap-3 hover:brightness-110 transition-all shadow-lg shadow-[#E040FB]/30" data-testid="journey-cta-btn">
              GET STARTED FREE <ArrowRight className="w-5 h-5" />
            </button>
          </Link>
        </div>
      </section>

      <GlobalFooter />
    </PublicLayout>
  );
};

export default LandingPage;
