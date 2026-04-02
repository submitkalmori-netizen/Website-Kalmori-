import React from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { ArrowRight } from '@phosphor-icons/react';

const stores = [
  { id: 'spotify', name: 'Spotify', textLogo: 'Spotify', textColor: '#1DB954', desc: "Spotify is a digital music streaming service that gives you access to millions of songs, podcasts, and videos from artists all over the world. With over 500 million active users, it's the world's largest audio streaming platform.", website: 'https://www.spotify.com/about-us/contact/' },
  { id: 'apple-music', name: 'Apple Music', textLogo: '♪ Music', textColor: '#FC3C44', desc: 'With an effortless design, millions of songs, and features like Apple Music Radio, Spatial Audio with Dolby Atmos, and lossless audio, Apple Music delivers the ultimate listening experience.', website: 'https://www.apple.com/apple-music/' },
  { id: 'deezer', name: 'Deezer', textLogo: 'DEEZER', textColor: '#FEAA2D', desc: 'Available in over 180 countries, Deezer gives fans access to 90 million tracks and offers music streaming in multiple audio formats including HiFi FLAC quality.', website: 'https://www.deezer.com/company' },
  { id: 'youtube', name: 'YouTube', textLogo: '▶ YouTube', textColor: '#FF0000', desc: "YouTube is home to the world's largest collection of on-demand music, with billions of viewers consuming music content daily. YouTube Music offers premium streaming.", website: 'https://www.youtube.com/about/' },
  { id: 'amazon-music', name: 'Amazon Music', textLogo: 'amazon music', textColor: '#00A8E1', desc: 'Amazon Music provides music fans multiple ways to enjoy music with HD and Ultra HD audio. Reach fans through Alexa, Echo devices, and the Fire TV platform.', website: 'https://www.amazon.com/music/unlimited' },
  { id: 'tiktok', name: 'TikTok', textLogo: '♪ TikTok', textColor: '#00F2EA', desc: 'TikTok is the leading short-form video platform with over 1 billion monthly active users. Your music can go viral when creators use your sounds in their videos.', website: 'https://www.tiktok.com/about' },
  { id: 'tidal', name: 'Tidal', textLogo: 'TIDAL', textColor: '#FFFFFF', desc: 'TIDAL is the first music streaming service with High Fidelity sound quality, Master Quality Authenticated audio, music videos, and exclusive artist content.', website: 'https://tidal.com/about' },
  { id: 'pandora', name: 'Pandora', textLogo: 'PANDORA', textColor: '#3668FF', desc: "Pandora is the world's most powerful music discovery platform with the Music Genome Project. It offers personalized radio and on-demand music streaming to 50M+ users.", website: 'https://www.pandora.com/about' },
  { id: 'soundcloud', name: 'SoundCloud', textLogo: '☁ SoundCloud', textColor: '#FF5500', desc: 'SoundCloud is an artist-first platform for emerging and established creators to share, promote, and monetize their music with 175 million monthly listeners.', website: 'https://soundcloud.com/pages/contact' },
  { id: 'instagram', name: 'Instagram & Facebook', textLogo: '📷 Instagram', textColor: '#E4405F', desc: "Add your music to Instagram Reels and Facebook Stories. Reach billions of users on Meta's social platforms and let creators share your music with the world.", website: 'https://about.meta.com/' },
  { id: 'audiomack', name: 'Audiomack', textLogo: 'AUDIOMACK', textColor: '#FFA200', desc: 'Audiomack is a free, artist-first streaming platform popular for hip-hop, R&B, and afrobeats discovery with over 20 million monthly active users.', website: 'https://audiomack.com/about' },
  { id: 'boomplay', name: 'Boomplay', textLogo: 'BOOMPLAY', textColor: '#FACD00', desc: "Boomplay is Africa's largest music streaming platform with over 80 million users across the continent. Essential for reaching the African music market.", website: 'https://www.boomplay.com/about' },
];

export default function StoresPage() {
  const navigate = useNavigate();
  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto bg-[#0a0a0a]" data-testid="stores-page">
        <div className="pt-4">
          {stores.map((store, i) => (
            <div key={store.id}>
              <div className="py-10 px-6 text-center" data-testid={`store-${store.id}`}>
                <div className="w-[220px] h-[100px] mx-auto mb-6 flex items-center justify-center">
                  <span className="text-[42px] font-extrabold tracking-[2px] text-center" style={{ color: store.textColor }}>{store.textLogo}</span>
                </div>
                <h3 className="text-[22px] font-bold text-white mb-4">{store.name}</h3>
                <p className="text-[15px] text-[#999] leading-relaxed mb-6 px-2.5">{store.desc}</p>
                <a href={store.website} target="_blank" rel="noopener noreferrer"
                  className="inline-block px-8 py-3 rounded-full bg-[#E040FB] text-white text-[13px] font-bold tracking-wider hover:opacity-90 transition-opacity">
                  READ MORE
                </a>
              </div>
              {i < stores.length - 1 && <div className="h-px bg-[#222] mx-10" />}
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mx-5 my-10 p-10 bg-[#111] rounded-2xl text-center max-w-xl self-center">
          <h2 className="text-2xl font-bold text-white mb-3">Ready to distribute your music?</h2>
          <p className="text-[15px] text-gray-400 leading-relaxed mb-6">Kalmori helps independent artists get their music on all major platforms. Start reaching millions of listeners today.</p>
          <button onClick={() => navigate('/register')} className="px-10 py-4 rounded-full bg-[#E040FB] text-white text-sm font-bold tracking-wider" data-testid="stores-get-started">
            GET STARTED
          </button>
        </div>

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
