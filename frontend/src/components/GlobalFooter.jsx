import React from 'react';
import { Link } from 'react-router-dom';
import { InstagramLogo, TwitterLogo, TiktokLogo, YoutubeLogo } from '@phosphor-icons/react';

const GlobalFooter = () => (
  <footer className="py-10 px-6 bg-black border-t border-[#222] text-center" data-testid="global-footer">
    <p className="text-[22px] font-extrabold text-[#E53935] tracking-[3px] mb-2">KALMORI</p>
    <p className="text-sm text-gray-400 mb-6">Your Music, Your Way</p>
    <div className="flex flex-wrap justify-center gap-6 mb-6">
      <Link to="/about" className="text-sm text-gray-400 hover:text-white transition-colors">About</Link>
      <Link to="/services" className="text-sm text-gray-400 hover:text-white transition-colors">Services</Link>
      <Link to="/pricing" className="text-sm text-gray-400 hover:text-white transition-colors">Pricing</Link>
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
