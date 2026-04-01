import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { MusicNotes, ChartLineUp, Globe, Wallet, Play, ArrowRight, Check, List, X, SpotifyLogo, AppleLogo, YoutubeLogo } from '@phosphor-icons/react';

const AnimatedLogo = () => (
  <div className="flex flex-col items-center">
    <span className="text-2xl font-black tracking-[4px] gradient-text">KALMORI</span>
    <div className="gradient-underline mt-1" />
  </div>
);

const AnimatedTagline = () => <span className="text-sm font-semibold tracking-wider gradient-text-red">Your Music, Your Way</span>;

const TypewriterText = ({ text, delay = 0, className = '' }) => {
  const [displayText, setDisplayText] = useState('');
  useEffect(() => {
    let timeout, index = 0;
    const startTyping = () => {
      if (index < text.length) { setDisplayText(text.substring(0, index + 1)); index++; timeout = setTimeout(startTyping, 80); }
      else { timeout = setTimeout(startDeleting, 3000); }
    };
    const startDeleting = () => {
      if (index > 0) { index--; setDisplayText(text.substring(0, index)); timeout = setTimeout(startDeleting, 40); }
      else { timeout = setTimeout(startTyping, 500); }
    };
    timeout = setTimeout(startTyping, delay);
    return () => clearTimeout(timeout);
  }, [text, delay]);
  return <span className={className}>{displayText}<span className="cursor text-[#7C4DFF]">|</span></span>;
};

const GradientText = ({ children, className = '' }) => <span className={`gradient-text ${className}`}>{children}</span>;

const LandingPage = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const heroImages = ['https://images.pexels.com/photos/1763075/pexels-photo-1763075.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260', 'https://images.pexels.com/photos/1644616/pexels-photo-1644616.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260'];
  
  useEffect(() => { const i = setInterval(() => setCurrentSlide((p) => (p + 1) % heroImages.length), 30000); return () => clearInterval(i); }, [heroImages.length]);
  
  const platforms = [{ name: 'Spotify', color: '#1DB954' }, { name: 'Apple Music', color: '#fff' }, { name: 'YouTube', color: '#FF0000' }, { name: 'TikTok', color: '#fff' }, { name: 'Amazon', color: '#FF9900' }, { name: 'Deezer', color: '#FF0092' }];
  const features = [{ icon: <Globe className="w-6 h-6" />, title: "150+ Platforms", desc: "Global distribution" }, { icon: <Wallet className="w-6 h-6" />, title: "100% Royalties", desc: "Keep all earnings" }, { icon: <ChartLineUp className="w-6 h-6" />, title: "Real-Time Analytics", desc: "Track performance" }, { icon: <MusicNotes className="w-6 h-6" />, title: "Free ISRC/UPC", desc: "Codes included" }];

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-lg border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <button onClick={() => setMenuOpen(true)} className="p-2 lg:hidden"><List className="w-6 h-6" /></button>
          <Link to="/" className="absolute left-1/2 -translate-x-1/2 lg:static lg:translate-x-0"><AnimatedLogo /></Link>
          <div className="hidden lg:flex items-center gap-8">
            <a href="#pricing" className="text-sm text-gray-400 hover:text-white">Pricing</a>
            <a href="#platforms" className="text-sm text-gray-400 hover:text-white">Platforms</a>
            <a href="#features" className="text-sm text-gray-400 hover:text-white">Features</a>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login"><Button variant="ghost" className="text-white hover:bg-white/10 hidden sm:flex" data-testid="nav-login-btn">Sign In</Button></Link>
            <Link to="/register"><button className="btn-animated px-4 py-2 rounded-full text-sm font-semibold text-white" data-testid="nav-signup-btn">Get Started</button></Link>
          </div>
        </div>
      </header>

      {menuOpen && (
        <div className="fixed inset-0 z-[60]">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMenuOpen(false)} />
          <div className="absolute left-0 top-0 bottom-0 w-[85%] max-w-[320px] bg-[#0a0a0a] border-r border-white/10">
            <div className="p-5 border-b border-white/10 flex items-center justify-between">
              <span className="text-xl font-bold tracking-[3px] gradient-text">KALMORI</span>
              <button onClick={() => setMenuOpen(false)} className="p-2"><X className="w-6 h-6" /></button>
            </div>
            <div className="px-5 py-3"><AnimatedTagline /></div>
            <div className="h-[2px] gradient-bg mx-5 mb-4" />
            <nav className="p-5 space-y-4">
              <Link to="/" onClick={() => setMenuOpen(false)} className="flex items-center gap-4 py-3 text-white hover:text-[#7C4DFF]"><MusicNotes className="w-5 h-5" /> Home</Link>
              <Link to="/releases" onClick={() => setMenuOpen(false)} className="flex items-center gap-4 py-3 text-white hover:text-[#7C4DFF]"><Play className="w-5 h-5" /> My Releases</Link>
              <a href="#pricing" onClick={() => setMenuOpen(false)} className="flex items-center gap-4 py-3 text-white hover:text-[#7C4DFF]"><Wallet className="w-5 h-5" /> Pricing</a>
              <div className="border-t border-white/10 my-4" />
              <Link to="/login" onClick={() => setMenuOpen(false)}><button className="w-full btn-animated py-3 rounded-lg text-white font-semibold">Sign In</button></Link>
              <Link to="/register" onClick={() => setMenuOpen(false)}><button className="w-full border border-[#7C4DFF] py-3 rounded-lg text-[#7C4DFF] font-semibold mt-3">Create Account</button></Link>
            </nav>
            <div className="absolute bottom-0 left-0 right-0 p-5 border-t border-white/10"><p className="text-xs text-gray-500 text-center">© 2026 Kalmori. All rights reserved.</p></div>
          </div>
        </div>
      )}

      <section className="relative h-screen pt-16 overflow-hidden">
        <div className="absolute inset-0 transition-opacity duration-1000" style={{ backgroundImage: `url(${heroImages[currentSlide]})`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
        <div className="hero-gradient absolute inset-0" />
        <div className="relative z-10 h-full flex flex-col items-center justify-end pb-24 px-6 text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black mb-2"><GradientText>G.O.A.T</GradientText> In</h1>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6"><TypewriterText text="Music Distribution" delay={1000} /></h2>
          <p className="text-gray-400 max-w-xl mb-8 text-sm sm:text-base">Get your music on Spotify, Apple Music, TikTok, YouTube, Tidal and more. Keep 100% ownership.</p>
          <Link to="/register"><button className="btn-red px-8 py-4 rounded text-white font-bold text-sm tracking-wider" data-testid="hero-cta-btn">DISTRIBUTE MY MUSIC ONLINE</button></Link>
          <div className="absolute bottom-8 right-8 flex gap-2">
            {heroImages.map((_, i) => <button key={i} onClick={() => setCurrentSlide(i)} className={`h-2.5 rounded-full transition-all ${currentSlide === i ? 'w-6 bg-[#7C4DFF]' : 'w-2.5 bg-gray-600'}`} />)}
          </div>
        </div>
      </section>

      <section className="section-dark py-16 px-6 text-center border-b border-white/10">
        <p className="text-xs font-bold text-[#E53935] tracking-[2px] mb-3">UNLIMITED DISTRIBUTION</p>
        <h3 className="text-2xl sm:text-3xl font-bold mb-2">Unlimited Distribution Starting at</h3>
        <p className="text-5xl font-black text-[#FFD700] my-4">$20/Year</p>
        <p className="text-gray-400 max-w-md mx-auto mb-6 text-sm">Increase the reach of your music across popular streaming platforms.</p>
        <Link to="/register" className="inline-flex items-center gap-2 text-[#E53935] font-bold text-sm">VIEW PRICING <ArrowRight className="w-4 h-4" /></Link>
      </section>

      <section id="platforms" className="py-16 px-6 text-center max-w-3xl mx-auto">
        <p className="text-xs font-bold text-[#E040FB] tracking-[2px] mb-3">AVAILABLE EVERYWHERE</p>
        <h3 className="text-2xl sm:text-3xl font-bold mb-8">Distribute to 150+ Platforms</h3>
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-3 mb-8">
          {platforms.map((p, i) => (
            <div key={i} className="platform-card text-center">
              <div className="w-10 h-10 mx-auto mb-2 rounded-full bg-white/5 flex items-center justify-center">
                {p.name === 'Spotify' && <SpotifyLogo className="w-5 h-5" style={{ color: p.color }} />}
                {p.name === 'Apple Music' && <AppleLogo className="w-5 h-5" style={{ color: p.color }} />}
                {p.name === 'YouTube' && <YoutubeLogo className="w-5 h-5" style={{ color: p.color }} />}
                {!['Spotify', 'Apple Music', 'YouTube'].includes(p.name) && <MusicNotes className="w-5 h-5" style={{ color: p.color }} />}
              </div>
              <p className="text-xs text-gray-400">{p.name}</p>
            </div>
          ))}
        </div>
        <Link to="/register" className="inline-flex items-center gap-2 text-[#E53935] font-bold text-sm">VIEW ALL 150+ STORES <ArrowRight className="w-4 h-4" /></Link>
      </section>

      <section id="features" className="section-dark py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-xs font-bold text-[#E53935] tracking-[2px] mb-3">WHY CHOOSE US</p>
            <h3 className="text-2xl sm:text-3xl font-bold">Why Choose <GradientText>Kalmori</GradientText></h3>
            <p className="text-gray-400 text-sm mt-2">Best Choice of Music Distribution Companies</p>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((f, i) => (
              <div key={i} className="card-kalmori p-6 text-center animate-fadeInUp" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br from-[#7C4DFF]/20 to-[#E040FB]/20 flex items-center justify-center text-[#7C4DFF]">{f.icon}</div>
                <h4 className="font-bold mb-1">{f.title}</h4>
                <p className="text-xs text-gray-400">{f.desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-8 flex flex-col items-center gap-4">
            <div className="flex items-center gap-3 text-sm text-gray-300"><Check className="w-4 h-4 text-[#4CAF50]" /> Unlimited music distribution worldwide</div>
            <div className="flex items-center gap-3 text-sm text-gray-300"><Check className="w-4 h-4 text-[#4CAF50]" /> Direct access to 150+ digital stores</div>
            <div className="flex items-center gap-3 text-sm text-gray-300"><Check className="w-4 h-4 text-[#4CAF50]" /> Keep 100% of your royalties</div>
          </div>
        </div>
      </section>

      <section id="pricing" className="py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-xs font-bold text-[#E040FB] tracking-[2px] mb-3">PRICING</p>
          <h3 className="text-2xl sm:text-3xl font-bold mb-2">Simple, Transparent Pricing</h3>
          <p className="text-gray-400 text-sm mb-12">Choose the plan that works best for you</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card-kalmori p-6">
              <div className="bg-[#E53935] text-xs font-bold py-1 px-3 rounded-full inline-block mb-4">UNLIMITED</div>
              <h4 className="text-lg font-bold mb-1">Single</h4>
              <p className="text-3xl font-black mb-1">$20<span className="text-sm font-normal text-gray-400">/year</span></p>
              <p className="text-xs text-gray-400 mb-4">Up to 3 tracks - 100% royalties</p>
              <Link to="/register"><button className="w-full btn-red py-3 rounded-lg text-sm font-semibold" data-testid="pricing-single-btn">Get Started</button></Link>
            </div>
            <div className="card-kalmori p-6 pricing-highlight">
              <h4 className="text-lg font-bold mb-1 mt-4">Album</h4>
              <p className="text-3xl font-black mb-1">$75<span className="text-sm font-normal text-gray-400">/year</span></p>
              <p className="text-xs text-gray-400 mb-4">7+ tracks - 100% royalties</p>
              <Link to="/register"><button className="w-full btn-animated py-3 rounded-lg text-sm font-semibold text-white" data-testid="pricing-album-btn">Get Started</button></Link>
            </div>
            <div className="card-kalmori p-6">
              <div className="bg-gray-600 text-xs font-bold py-1 px-3 rounded-full inline-block mb-4">FREE</div>
              <h4 className="text-lg font-bold mb-1">Start Free</h4>
              <p className="text-3xl font-black mb-1">$0</p>
              <p className="text-xs text-gray-400 mb-4">15-20% revenue share</p>
              <Link to="/register"><button className="w-full border border-white/20 py-3 rounded-lg text-sm font-semibold hover:bg-white/5" data-testid="pricing-free-btn">Start Free</button></Link>
            </div>
          </div>
          <div className="mt-8 flex items-center justify-center gap-4 p-5 rounded-2xl bg-[#111] border border-[#E040FB]/20">
            <MusicNotes className="w-10 h-10 text-[#E040FB]" />
            <div className="text-left"><h4 className="font-bold">Built for Young Artists & Producers</h4><p className="text-sm text-gray-400">Start your music career with $0 upfront.</p></div>
          </div>
        </div>
      </section>

      <section className="py-20 px-6 text-center bg-gradient-to-br from-[#7C4DFF]/20 via-[#E040FB]/10 to-[#FF4081]/20">
        <h3 className="text-3xl sm:text-4xl font-black mb-4">Ready to Start Your<br />Journey?</h3>
        <p className="text-gray-400 mb-8 text-sm">Join thousands of artists distributing their music worldwide with Kalmori.</p>
        <Link to="/register"><button className="bg-white text-[#E53935] px-8 py-4 rounded font-bold text-sm tracking-wider inline-flex items-center gap-2" data-testid="cta-signup-btn">GET STARTED FREE <ArrowRight className="w-4 h-4" /></button></Link>
      </section>

      <footer className="py-12 px-6 border-t border-white/10">
        <div className="max-w-6xl mx-auto text-center">
          <span className="text-xl font-bold tracking-[3px] text-[#E53935]">KALMORI</span>
          <p className="text-gray-400 text-sm mt-2 mb-6">Your Music, Your Way</p>
          <div className="flex flex-wrap justify-center gap-6 mb-6">
            <a href="#" className="text-sm text-gray-400 hover:text-white">Terms</a>
            <a href="#" className="text-sm text-gray-400 hover:text-white">Privacy</a>
            <a href="#" className="text-sm text-gray-400 hover:text-white">Support</a>
            <a href="#" className="text-sm text-gray-400 hover:text-white">Contact</a>
          </div>
          <p className="text-xs text-gray-600">© 2026 Kalmori. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
