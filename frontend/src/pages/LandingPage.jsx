import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { 
  MusicNotes, 
  ChartLineUp, 
  Globe, 
  Wallet, 
  Users, 
  Play,
  SpotifyLogo,
  AppleLogo,
  YoutubeLogo,
  ArrowRight,
  Check
} from '@phosphor-icons/react';

const LandingPage = () => {
  const features = [
    {
      icon: <Globe className="w-6 h-6" />,
      title: "150+ Streaming Platforms",
      description: "Distribute your music to Spotify, Apple Music, Amazon, TikTok, and more."
    },
    {
      icon: <Wallet className="w-6 h-6" />,
      title: "Keep 100% Royalties",
      description: "With our paid plans, you keep every penny you earn from your streams."
    },
    {
      icon: <ChartLineUp className="w-6 h-6" />,
      title: "Real-Time Analytics",
      description: "Track your streams, downloads, and earnings across all platforms."
    },
    {
      icon: <MusicNotes className="w-6 h-6" />,
      title: "AI-Powered Tools",
      description: "Get smart metadata suggestions and AI-generated descriptions."
    }
  ];

  const plans = [
    {
      name: "Free",
      price: "$0",
      period: "forever",
      features: ["Unlimited releases", "Basic analytics", "All platforms", "15% revenue share"],
      cta: "Start Free",
      highlight: false
    },
    {
      name: "Rise",
      price: "$9.99",
      period: "/month",
      features: ["Keep 100% royalties", "Priority distribution", "Advanced analytics", "24/7 Support"],
      cta: "Get Rise",
      highlight: true
    },
    {
      name: "Pro",
      price: "$19.99",
      period: "/month",
      features: ["Everything in Rise", "YouTube Content ID", "Spotify Canvas", "AI insights"],
      cta: "Go Pro",
      highlight: false
    }
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#FF3B30] rounded-md flex items-center justify-center">
              <MusicNotes className="w-5 h-5 text-white" weight="bold" />
            </div>
            <span className="text-xl font-bold tracking-tight">TuneDrop</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-[#A1A1AA] hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="text-sm text-[#A1A1AA] hover:text-white transition-colors">Pricing</a>
            <a href="#platforms" className="text-sm text-[#A1A1AA] hover:text-white transition-colors">Platforms</a>
          </div>
          
          <div className="flex items-center gap-4">
            <Link to="/login">
              <Button variant="ghost" className="text-white hover:bg-white/10" data-testid="nav-login-btn">
                Log In
              </Button>
            </Link>
            <Link to="/register">
              <Button className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white" data-testid="nav-signup-btn">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: 'url(https://images.pexels.com/photos/196652/pexels-photo-196652.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            opacity: 0.2
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0A0A0A] via-transparent to-[#0A0A0A] z-0" />
        
        <div className="max-w-5xl mx-auto text-center relative z-10">
          <p className="text-xs uppercase tracking-[0.2em] font-semibold text-[#FF3B30] mb-6 animate-fadeIn">
            The Future of Music Distribution
          </p>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tighter mb-6 animate-fadeIn stagger-1">
            Your Music.<br />
            <span className="text-[#FF3B30]">Your Way.</span>
          </h1>
          <p className="text-lg text-[#A1A1AA] max-w-2xl mx-auto mb-10 animate-fadeIn stagger-2">
            Distribute your music to 150+ streaming platforms worldwide. Keep 100% of your royalties. 
            Track your success with real-time analytics.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fadeIn stagger-3">
            <Link to="/register">
              <Button size="lg" className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white px-8 py-6 text-lg" data-testid="hero-cta-btn">
                Start Distributing <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="border-white/20 hover:bg-white/10 text-white px-8 py-6 text-lg">
              <Play className="mr-2 w-5 h-5" /> Watch Demo
            </Button>
          </div>
          
          <div className="mt-16 flex items-center justify-center gap-8 opacity-60 animate-fadeIn stagger-4">
            <SpotifyLogo className="w-10 h-10" />
            <AppleLogo className="w-10 h-10" />
            <YoutubeLogo className="w-10 h-10" />
            <div className="text-sm text-[#A1A1AA]">+ 150 more platforms</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-xs uppercase tracking-[0.2em] font-semibold text-[#FFCC00] mb-4">Features</p>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight">
              Everything You Need to Succeed
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="bg-[#141414] border border-white/10 p-6 rounded-md card-hover animate-fadeIn"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="w-12 h-12 bg-[#FF3B30]/10 rounded-md flex items-center justify-center mb-4 text-[#FF3B30]">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-medium mb-2">{feature.title}</h3>
                <p className="text-sm text-[#A1A1AA]">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section id="platforms" className="py-20 px-6 bg-[#141414]">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-xs uppercase tracking-[0.2em] font-semibold text-[#007AFF] mb-4">Platforms</p>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-6">
            Reach Billions of Listeners
          </h2>
          <p className="text-[#A1A1AA] max-w-2xl mx-auto mb-12">
            We distribute to all major streaming platforms including Spotify, Apple Music, 
            Amazon Music, YouTube Music, TikTok, Instagram, and 150+ more.
          </p>
          
          <div className="flex flex-wrap items-center justify-center gap-8">
            {['Spotify', 'Apple Music', 'Amazon Music', 'YouTube Music', 'TikTok', 'Deezer', 'Tidal', 'Pandora'].map((platform, i) => (
              <div key={i} className="px-6 py-3 bg-[#0A0A0A] border border-white/10 rounded-md text-sm">
                {platform}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-xs uppercase tracking-[0.2em] font-semibold text-[#FFCC00] mb-4">Pricing</p>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight">
              Simple, Transparent Pricing
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan, index) => (
              <div 
                key={index}
                className={`p-6 rounded-md border ${
                  plan.highlight 
                    ? 'bg-[#FF3B30]/10 border-[#FF3B30]' 
                    : 'bg-[#141414] border-white/10'
                } card-hover`}
              >
                {plan.highlight && (
                  <span className="text-xs uppercase tracking-widest text-[#FF3B30] font-semibold">Most Popular</span>
                )}
                <h3 className="text-xl font-bold mt-2">{plan.name}</h3>
                <div className="mt-4 mb-6">
                  <span className="text-4xl font-black">{plan.price}</span>
                  <span className="text-[#A1A1AA]">{plan.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-[#22C55E]" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link to="/register">
                  <Button 
                    className={`w-full ${
                      plan.highlight 
                        ? 'bg-[#FF3B30] hover:bg-[#FF3B30]/90' 
                        : 'bg-white/10 hover:bg-white/20'
                    } text-white`}
                    data-testid={`pricing-${plan.name.toLowerCase()}-btn`}
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center bg-[#141414] border border-white/10 rounded-md p-12">
          <Users className="w-12 h-12 text-[#FF3B30] mx-auto mb-6" />
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-4">
            Join 100,000+ Artists
          </h2>
          <p className="text-[#A1A1AA] mb-8">
            Start your music career today. No credit card required for free tier.
          </p>
          <Link to="/register">
            <Button size="lg" className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white px-8" data-testid="cta-signup-btn">
              Create Free Account
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-[#FF3B30] rounded flex items-center justify-center">
              <MusicNotes className="w-4 h-4 text-white" weight="bold" />
            </div>
            <span className="font-bold">TuneDrop</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-[#A1A1AA]">
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Support</a>
          </div>
          <p className="text-sm text-[#71717A]">© 2026 TuneDrop. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
