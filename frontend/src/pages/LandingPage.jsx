import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { MusicNotes, ChartLineUp, Globe, Wallet, Play, ArrowRight, Check, List, X, ArrowUp, User, SpotifyLogo, AppleLogo, YoutubeLogo, TiktokLogo, InstagramLogo, Envelope, MusicNote, Playlist } from '@phosphor-icons/react';

// Your original hero images
const heroSlideImages = [
  'https://customer-assets.emergentagent.com/job_9d65d3d0-8e4c-4ca7-97e3-3472b806edee/artifacts/oldly27j_vecteezy_professional-microphone-on-stage-in-a-bar-in-the-pink-rays_46833147_1.jpg',
  'https://customer-assets.emergentagent.com/job_9d65d3d0-8e4c-4ca7-97e3-3472b806edee/artifacts/3rjo6nvi_large-vecteezy_music-recording-studio-with-professional-equipment-and_34430986_large.jpg',
];

// Animated Color Text Component
const AnimatedColorText = ({ children, className = '' }) => {
  return <span className={`animate-color-cycle ${className}`}>{children}</span>;
};

// Animated Tagline (Red/Yellow)
const AnimatedTagline = () => {
  return <span className="animate-tagline-cycle font-semibold tracking-wider">Your Music, Your Way</span>;
};

// Typewriter with looping
const LoopingTypewriter = ({ text, className = '' }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  
  useEffect(() => {
    let timeout;
    if (!isDeleting) {
      if (displayedText.length < text.length) {
        timeout = setTimeout(() => setDisplayedText(text.slice(0, displayedText.length + 1)), 30);
      } else {
        timeout = setTimeout(() => setIsDeleting(true), 3000);
      }
    } else {
      if (displayedText.length > 0) {
        timeout = setTimeout(() => setDisplayedText(text.slice(0, displayedText.length - 1)), 15);
      } else {
        timeout = setTimeout(() => setIsDeleting(false), 1000);
      }
    }
    return () => clearTimeout(timeout);
  }, [displayedText, isDeleting, text]);
  
  return <span className={className}>{displayedText}<span className="animate-blink text-[#7C4DFF]">|</span></span>;
};

// Hero Typewriter Sequence
const HeroTypewriterSequence = () => {
  const [phase, setPhase] = useState(0);
  const [line1, setLine1] = useState('');
  const [line2, setLine2] = useState('');
  const [desc, setDesc] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  
  const LINE1 = "G.O.A.T In";
  const LINE2 = "Music Distribution";
  const DESC = "Get your music on Spotify, Apple Music, TikTok, YouTube, Tidal and more. Keep 100% ownership of your music and stay in control of your career.";
  
  useEffect(() => {
    let timeout;
    if (phase === 0) {
      if (line1.length < LINE1.length) {
        timeout = setTimeout(() => setLine1(LINE1.slice(0, line1.length + 1)), 120);
      } else {
        timeout = setTimeout(() => setPhase(1), 500);
      }
    } else if (phase === 1) {
      if (line2.length < LINE2.length) {
        timeout = setTimeout(() => setLine2(LINE2.slice(0, line2.length + 1)), 80);
      } else {
        timeout = setTimeout(() => setPhase(2), 500);
      }
    } else if (phase === 2) {
      if (!isDeleting) {
        if (desc.length < DESC.length) {
          timeout = setTimeout(() => setDesc(DESC.slice(0, desc.length + 1)), 30);
        } else {
          timeout = setTimeout(() => setIsDeleting(true), 3000);
        }
      } else {
        if (desc.length > 0) {
          timeout = setTimeout(() => setDesc(DESC.slice(0, desc.length - 1)), 15);
        } else {
          timeout = setTimeout(() => setIsDeleting(false), 1000);
        }
      }
    }
    return () => clearTimeout(timeout);
  }, [phase, line1, line2, desc, isDeleting]);
  
  return (
    <div className="text-center">
      <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold mb-2">
        <AnimatedColorText>{line1}</AnimatedColorText>
        {phase === 0 && <span className="animate-blink text-[#7C4DFF]">|</span>}
      </h1>
      <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6">
        <AnimatedColorText>{line2}</AnimatedColorText>
        {phase === 1 && <span className="animate-blink text-[#7C4DFF]">|</span>}
      </h2>
      <p className="text-gray-300 max-w-lg mx-auto mb-8 text-sm sm:text-base leading-relaxed">
        {desc}
        {phase === 2 && <span className="animate-blink text-[#7C4DFF]">|</span>}
      </p>
    </div>
  );
};

// Animated Button
const AnimatedButton = ({ children, onClick, className = '' }) => {
  return (
    <button onClick={onClick} className={`animate-btn-gradient text-white font-bold py-4 px-8 rounded-full flex items-center gap-3 ${className}`}>
      {children}
    </button>
  );
};

const platforms = [
  { name: 'Spotify', icon: <SpotifyLogo className="w-8 h-8" weight="fill" />, color: '#1DB954' },
  { name: 'Apple Music', icon: <AppleLogo className="w-8 h-8" weight="fill" />, color: '#fff' },
  { name: 'YouTube', icon: <YoutubeLogo className="w-8 h-8" weight="fill" />, color: '#FF0000' },
  { name: 'TikTok', icon: <TiktokLogo className="w-8 h-8" weight="fill" />, color: '#fff' },
  { name: 'Amazon', icon: <MusicNotes className="w-8 h-8" weight="fill" />, color: '#FF9900' },
  { name: 'Deezer', icon: <MusicNote className="w-8 h-8" weight="fill" />, color: '#FF0092' },
];

const promotionCards = [
  { name: 'Instagram', desc: 'Stories, Reels & Posts', icon: <InstagramLogo className="w-6 h-6" />, color: '#E1306C' },
  { name: 'TikTok', desc: 'Viral Marketing', icon: <TiktokLogo className="w-6 h-6" />, color: '#000' },
  { name: 'Email', desc: 'Curator Outreach', icon: <Envelope className="w-6 h-6" />, color: '#7C4DFF' },
  { name: 'Playlists', desc: 'Editorial Pitching', icon: <Playlist className="w-6 h-6" />, color: '#1DB954' },
];

const LandingPage = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [zoomScale, setZoomScale] = useState(1);
  
  // Auto-rotate slides every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => setCurrentSlide((p) => (p + 1) % heroSlideImages.length), 30000);
    return () => clearInterval(interval);
  }, []);
  
  // Zoom effect for second slide
  useEffect(() => {
    if (currentSlide === 1) {
      setZoomScale(1);
      const zoomInterval = setInterval(() => {
        setZoomScale(prev => Math.min(prev + 0.009, 1.25));
      }, 1000);
      return () => clearInterval(zoomInterval);
    } else {
      setZoomScale(1);
    }
  }, [currentSlide]);

  return (
    <PublicLayout>
      {/* Custom CSS for animations */}
      <style>{`
        @keyframes colorCycle { 0%{color:#7C4DFF} 33%{color:#E040FB} 66%{color:#FF4081} 100%{color:#7C4DFF} }
        @keyframes taglineCycle { 0%{color:#FF4444} 50%{color:#FFD700} 100%{color:#FF4444} }
        @keyframes btnGradient { 0%{background:#7C4DFF} 33%{background:#E040FB} 66%{background:#FF4081} 100%{background:#7C4DFF} }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes underlineCycle { 0%{background:#7C4DFF} 33%{background:#E040FB} 66%{background:#FF4081} 100%{background:#7C4DFF} }
        .animate-color-cycle { animation: colorCycle 6s ease-in-out infinite; }
        .animate-tagline-cycle { animation: taglineCycle 4s ease-in-out infinite; }
        .animate-btn-gradient { animation: btnGradient 6s ease-in-out infinite; }
        .animate-blink { animation: blink 1s step-end infinite; }
        .animate-underline { animation: underlineCycle 6s ease-in-out infinite; }
      `}</style>

      {/* Hero Section */}
      <section className="relative min-h-screen overflow-hidden">
        <div className="absolute inset-0 transition-all duration-500" style={{ backgroundImage: `url(${heroSlideImages[currentSlide]})`, backgroundSize: 'cover', backgroundPosition: 'center', transform: `scale(${zoomScale})` }} />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.6) 50%, rgba(0,0,0,1) 100%)' }} />
        <div className="relative z-10 min-h-screen flex flex-col items-center justify-end pb-24 px-6">
          <HeroTypewriterSequence />
          <Link to="/register">
            <button className="bg-[#E53935] px-8 py-4 rounded text-white font-bold text-sm tracking-wider flex items-center gap-3" data-testid="hero-cta-btn">
              DISTRIBUTE MY MUSIC ONLINE <ArrowRight className="w-5 h-5" />
            </button>
          </Link>
          <div className="absolute bottom-8 right-8 flex gap-2">
            {heroSlideImages.map((_, i) => (
              <button key={i} onClick={() => setCurrentSlide(i)} className={`h-2.5 rounded-full transition-all ${currentSlide === i ? 'w-6 bg-[#7C4DFF]' : 'w-2.5 bg-gray-600'}`} />
            ))}
          </div>
        </div>
      </section>

      {/* Unlimited Distribution */}
      <section className="py-16 px-6 text-center bg-[#0a0a0a] border-b border-white/10">
        <p className="text-xs font-bold tracking-[3px] text-[#E53935] mb-3">UNLIMITED DISTRIBUTION</p>
        <h3 className="text-2xl sm:text-3xl font-bold"><span className="text-[#E040FB]">Unlimited Distribution</span><br/>Starting at</h3>
        <p className="my-4"><span className="text-5xl font-extrabold text-[#FFD700]">$20</span><span className="text-lg text-white">/Year</span></p>
        <p className="text-gray-400 max-w-md mx-auto mb-6 text-sm">Increase the reach of your music across the most popular streaming platforms worldwide. One payment, 1-year distribution.</p>
        <a href="#pricing" className="inline-flex items-center gap-2 text-[#E53935] font-bold text-sm">VIEW PRICING <ArrowRight className="w-4 h-4" /></a>
      </section>

      {/* Platforms */}
      <section id="platforms" className="py-16 px-6 text-center bg-black max-w-3xl mx-auto">
        <p className="text-xs font-bold tracking-[3px] text-[#E040FB] mb-3">AVAILABLE EVERYWHERE</p>
        <h3 className="text-2xl sm:text-3xl font-bold mb-8"><AnimatedColorText>Distribute to 150+ Platforms</AnimatedColorText></h3>
        <div className="grid grid-cols-3 gap-3 mb-8">
          {platforms.map((p, i) => (
            <div key={i} className="bg-[#111] border border-white/10 rounded-2xl p-4 flex flex-col items-center hover:border-white/30 transition-colors">
              <div style={{ color: p.color }}>{p.icon}</div>
              <p className="text-xs text-gray-400 mt-2">{p.name}</p>
            </div>
          ))}
        </div>
        <Link to="/stores" className="inline-flex items-center gap-2 text-[#E53935] font-bold text-sm">VIEW ALL 150+ STORES <ArrowRight className="w-4 h-4" /></Link>
      </section>

      {/* Global Reach */}
      <section className="py-16 px-6 bg-[#0a0a0a] max-w-3xl mx-auto">
        <div className="w-full aspect-video mb-8 rounded-2xl overflow-hidden bg-cover bg-center" style={{ backgroundImage: `url(${heroSlideImages[0]})` }} />
        <div className="text-center">
          <p className="text-xs font-bold tracking-[3px] text-[#E53935] mb-3">GLOBAL REACH</p>
          <h3 className="text-2xl sm:text-3xl font-bold mb-4">Get Your Music<br/><span className="text-[#FFD700]">Everywhere</span></h3>
          <p className="text-gray-400 max-w-md mx-auto mb-6 text-sm">We distribute your music to every major streaming platform including Spotify, Apple Music, Amazon Music, YouTube Music, TikTok, Instagram, and 150+ more stores worldwide.</p>
          <div className="flex flex-col items-center gap-3">
            {['All major streaming platforms','Social media platforms','Digital download stores'].map((t,i)=>(
              <div key={i} className="flex items-center gap-3 text-sm text-gray-300"><Check className="w-5 h-5 text-[#E040FB]" />{t}</div>
            ))}
          </div>
        </div>
      </section>

      {/* Need Beats */}
      <section className="py-8 px-6">
        <div className="max-w-xl mx-auto rounded-3xl p-8 text-center" style={{ background: 'linear-gradient(180deg, #9C27B0 0%, #E040FB 100%)' }}>
          <MusicNotes className="w-12 h-12 text-white mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-white mb-4">Need Beats or<br/>Instrumentals?</h3>
          <p className="text-white/80 text-sm mb-6">Can't make your own beats? No problem! Get professional instrumentals with full rights or lease options.</p>
          <div className="flex flex-col items-start gap-3 mb-6 text-left max-w-xs mx-auto">
            {['Exclusive Rights Available','Affordable Lease Options','All Genres: Hip-Hop, R&B, Afrobeats, Dancehall','Custom Beats on Request'].map((t,i)=>(
              <div key={i} className="flex items-center gap-3 text-white"><Check className="w-5 h-5" />{t}</div>
            ))}
          </div>
          <Link to="/instrumentals"><button className="bg-white px-8 py-3 rounded-full font-bold text-sm flex items-center gap-2 mx-auto text-[#9C27B0]">REQUEST A BEAT <ArrowRight className="w-4 h-4" /></button></Link>
        </div>
      </section>

      {/* Why Choose Kalmori */}
      <section id="features" className="py-16 px-6 bg-[#0a0a0a] max-w-xl mx-auto text-center">
        <p className="text-xs font-bold tracking-[3px] text-gray-400 mb-3">WHY CHOOSE US</p>
        <h3 className="text-2xl sm:text-3xl font-bold mb-2">Why Choose <span className="text-[#E040FB]">Kalmori</span></h3>
        <p className="mb-8"><span className="text-[#E53935]">Best Choice</span> of Music Distribution Companies</p>
        <div className="flex flex-col items-start gap-4 mb-8 text-left max-w-sm mx-auto">
          {['Unlimited music distribution worldwide','Direct access to 150+ digital stores','Detailed sales data to guide your strategy','Keep 100% of your royalties','Free ISRC & UPC codes included'].map((t,i)=>(
            <div key={i} className="flex items-center gap-3 text-gray-300"><Check className="w-5 h-5 text-[#E53935]" />{t}</div>
          ))}
        </div>
        <Link to="/services"><button className="bg-[#E53935] px-8 py-4 rounded text-white font-bold text-sm tracking-wider flex items-center gap-3 mx-auto">ALL OUR SERVICES <ArrowRight className="w-5 h-5" /></button></Link>
      </section>

      {/* Analytics */}
      <section className="py-16 px-6 bg-black max-w-xl mx-auto text-center">
        <p className="text-xs font-bold tracking-[3px] text-[#E040FB] mb-3">TRACK YOUR SUCCESS</p>
        <h3 className="text-2xl sm:text-3xl font-bold mb-4">Real-Time<br/><span className="text-[#FFD700]">Analytics</span></h3>
        <p className="text-gray-400 max-w-md mx-auto mb-6 text-sm">Monitor your streams, downloads, and earnings across all platforms. Get insights into your audience demographics and track your growth over time.</p>
        <div className="flex flex-col items-center gap-3">
          {['Stream & download tracking','Revenue analytics','Audience insights'].map((t,i)=>(
            <div key={i} className="flex items-center gap-3 text-sm text-gray-300"><Check className="w-5 h-5 text-[#E040FB]" />{t}</div>
          ))}
        </div>
      </section>

      {/* Promotion Services */}
      <section className="py-16 px-6 bg-black max-w-3xl mx-auto text-center">
        <p className="text-xs font-bold tracking-[3px] text-[#E040FB] mb-3">PROMOTION SERVICES</p>
        <h3 className="text-2xl sm:text-3xl font-bold mb-2"><AnimatedColorText>Promotion Services</AnimatedColorText></h3>
        <p className="text-gray-400 mb-8 text-sm">We help you get heard across all platforms</p>
        <div className="grid grid-cols-2 gap-3 mb-8">
          {promotionCards.map((p,i)=>(
            <div key={i} className="bg-[#111] border border-white/10 rounded-2xl p-4 text-left">
              <div className="w-10 h-10 rounded-full flex items-center justify-center mb-3" style={{ backgroundColor: p.color }}>{p.icon}</div>
              <h4 className="font-bold text-white">{p.name}</h4>
              <p className="text-xs text-gray-400">{p.desc}</p>
            </div>
          ))}
        </div>
        <AnimatedButton onClick={() => {}} className="mx-auto">LEARN MORE ABOUT PROMOTION <ArrowRight className="w-5 h-5" /></AnimatedButton>
      </section>

      {/* Young Artists */}
      <section className="py-16 px-6 bg-[#0a0a0a] max-w-xl mx-auto text-center">
        <h3 className="text-2xl font-bold mb-2">Built for<br/><span className="text-[#FFD700]">Young Artists & Producers</span></h3>
        <p className="text-gray-400 text-sm mb-6">Whether you're making Dancehall beats in Kingston, crafting Trap hits in Atlanta, or producing R&B vibes in LA - KALMORI is your gateway to the world.</p>
        <div className="flex flex-col items-start gap-3 mb-6 text-left max-w-sm mx-auto">
          {['Start for FREE - No credit card required','Reach fans in 150+ countries worldwide','From Dancehall to Trap to R&B - All genres welcome','Get paid directly - Keep up to 100% royalties'].map((t,i)=>(
            <div key={i} className="flex items-center gap-3 text-gray-300"><Check className="w-5 h-5 text-[#4CAF50]" />{t}</div>
          ))}
        </div>
        <div className="flex gap-3 justify-center">
          <Link to="/register"><button className="bg-[#E53935] px-6 py-3 rounded text-white font-bold text-sm">START FREE</button></Link>
          <Link to="/pricing"><button className="border border-[#E53935] px-6 py-3 rounded text-[#E53935] font-bold text-sm">PRICING</button></Link>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-16 px-6 bg-[#0a0a0a] max-w-4xl mx-auto text-center">
        <p className="text-xs font-bold tracking-[3px] text-[#E040FB] mb-3">PRICING</p>
        <h3 className="text-2xl sm:text-3xl font-bold mb-2"><AnimatedColorText>Simple, Transparent Pricing</AnimatedColorText></h3>
        <p className="text-gray-400 text-sm mb-8">Choose the plan that works best for you</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#111] border-2 border-white/10 rounded-2xl p-6 text-center">
            <div className="bg-[#E53935] text-xs font-bold py-1 px-3 rounded-full inline-block mb-4">UNLIMITED</div>
            <h4 className="text-lg font-bold">Single</h4>
            <p className="text-3xl font-extrabold my-2">$20<span className="text-sm font-normal text-gray-400">/year</span></p>
            <p className="text-xs text-gray-400">Up to 3 tracks • 100% royalties</p>
          </div>
          <div className="bg-[#111] border-2 border-[#FFD700] rounded-2xl p-6 text-center relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#FFD700] text-black text-xs font-bold py-1 px-4 rounded-full">BEST DEAL</div>
            <h4 className="text-lg font-bold mt-4">Album</h4>
            <p className="text-3xl font-extrabold my-2">$75<span className="text-sm font-normal text-gray-400">/year</span></p>
            <p className="text-xs text-gray-400">7+ tracks • 100% royalties</p>
          </div>
          <div className="bg-[#111] border-2 border-white/10 rounded-2xl p-6 text-center">
            <div className="bg-gray-600 text-xs font-bold py-1 px-3 rounded-full inline-block mb-4">FREE</div>
            <h4 className="text-lg font-bold">Start Free</h4>
            <p className="text-3xl font-extrabold my-2">$0</p>
            <p className="text-xs text-gray-400">15-20% revenue share</p>
          </div>
        </div>
        <Link to="/pricing"><AnimatedButton className="mt-8 mx-auto">VIEW ALL PLANS <ArrowRight className="w-5 h-5" /></AnimatedButton></Link>
        <div className="mt-8 flex items-center justify-center gap-4 p-5 rounded-2xl bg-[#111] border border-[#E040FB]/20">
          <MusicNotes className="w-10 h-10 text-[#E040FB]" />
          <div className="text-left"><h4 className="font-bold">Built for Young Artists & Producers</h4><p className="text-sm text-gray-400">Start your music career with $0 upfront. We believe in your talent!</p></div>
        </div>
      </section>

      {/* Journey CTA */}
      <section className="py-20 px-6 text-center" style={{ background: 'linear-gradient(135deg, rgba(124,77,255,0.3), rgba(224,64,251,0.2))' }}>
        <h3 className="text-3xl sm:text-4xl font-extrabold mb-4">Ready to Start Your<br/>Journey?</h3>
        <p className="text-gray-300 mb-8 text-sm">Join thousands of artists distributing their music worldwide with Kalmori.</p>
        <Link to="/register"><button className="bg-white text-[#E53935] px-8 py-4 rounded font-bold text-sm tracking-wider inline-flex items-center gap-2">GET STARTED FREE <ArrowRight className="w-4 h-4" /></button></Link>
      </section>

      <GlobalFooter />
    </PublicLayout>
  );
};

export default LandingPage;
