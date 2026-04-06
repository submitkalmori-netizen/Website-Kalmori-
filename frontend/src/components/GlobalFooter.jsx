import React from 'react';
import { Link } from 'react-router-dom';
import { InstagramLogo, TwitterLogo, TiktokLogo, YoutubeLogo } from '@phosphor-icons/react';

const GlobalFooter = () => (
  <footer className="py-10 px-6 bg-black border-t border-[#222] text-center" data-testid="global-footer">
    <style>{`
      @keyframes footer-logo-cycle {
        0%, 100% { color: #7C4DFF; text-shadow: 0 0 10px rgba(124,77,255,0.5), 0 0 20px rgba(124,77,255,0.3); }
        33% { color: #E040FB; text-shadow: 0 0 10px rgba(224,64,251,0.5), 0 0 20px rgba(224,64,251,0.3); }
        66% { color: #FF4081; text-shadow: 0 0 10px rgba(255,64,129,0.5), 0 0 20px rgba(255,64,129,0.3); }
      }
    `}</style>
    <p className="text-[22px] font-extrabold tracking-[3px] mb-2" style={{ animation: 'footer-logo-cycle 6s ease-in-out infinite' }}>KALMORI</p>
    <p className="text-sm text-gray-400 mb-6">Your Music, Your Way</p>
    <div className="flex flex-wrap justify-center gap-6 mb-6">
      <Link to="/about" className="text-sm text-gray-400 hover:text-white transition-colors">About</Link>
      <Link to="/services" className="text-sm text-gray-400 hover:text-white transition-colors">Services</Link>
      <Link to="/pricing" className="text-sm text-gray-400 hover:text-white transition-colors">Pricing</Link>
                <Link to="/faq" className="text-sm text-gray-400 hover:text-white transition-colors">FAQ</Link>
      <Link to="/contact" className="text-sm text-gray-400 hover:text-white transition-colors">Contact</Link>
      <Link to="/stores" className="text-sm text-gray-400 hover:text-white transition-colors">Stores</Link>
      <Link to="/terms" className="text-sm text-gray-400 hover:text-white transition-colors">Terms</Link>
      <Link to="/privacy" className="text-sm text-gray-400 hover:text-white transition-colors">Privacy</Link>
    </div>
    <div className="flex justify-center gap-4 mb-6">
      {[InstagramLogo, TwitterLogo, TiktokLogo, YoutubeLogo].map((Icon, i) => (
        <div key={i} className="w-11 h-11 rounded-full bg-[#111] flex items-center justify-center hover:bg-white/10 transition-colors cursor-pointer">
          <Icon className="w-5 h-5 text-white" />
        </div>
      ))}
    </div>
    <p className="text-xs text-[#444]">&copy; {new Date().getFullYear()} Kalmori. All rights reserved.</p>
  </footer>
);

export default GlobalFooter;
