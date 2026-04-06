import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { SpotifyLogo, Play, Clock, Fire, Users, ArrowSquareOut, MusicNotes, Headphones, Star, ArrowRight } from '@phosphor-icons/react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export default function SpotifyAnalyticsPage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const statusRes = await axios.get(`${API}/spotify/status`, { withCredentials: true });
      setStatus(statusRes.data);
      if (statusRes.data.connected && statusRes.data.spotify_artist_id) {
        const dataRes = await axios.get(`${API}/spotify/artist-data`, { withCredentials: true });
        setData(dataRes.data);
      }
    } catch (err) {
      console.error('Spotify load error:', err);
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError(err.response?.data?.detail || 'Failed to load Spotify data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <DashboardLayout>
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-[#1DB954] border-t-transparent rounded-full animate-spin" />
      </div>
    </DashboardLayout>
  );

  if (!status?.connected) return (
    <DashboardLayout>
      <div className="max-w-lg mx-auto text-center py-20" data-testid="spotify-not-connected">
        <div className="w-20 h-20 rounded-2xl bg-[#1DB954]/10 flex items-center justify-center mx-auto mb-6">
          <SpotifyLogo className="w-10 h-10 text-[#1DB954]" weight="fill" />
        </div>
        <h1 className="text-2xl font-bold text-white mb-3">Connect Spotify</h1>
        <p className="text-sm text-gray-400 mb-6">Link your Spotify account to see real-time artist data, top tracks, and follower analytics.</p>
        {error && <p className="text-sm text-red-400 mb-4" data-testid="spotify-error">{error}</p>}
        <button onClick={() => navigate('/settings')} className="px-6 py-3 bg-[#1DB954] text-white rounded-full text-sm font-bold hover:bg-[#1DB954]/80 transition-all" data-testid="go-to-settings-btn">
          Go to Settings <ArrowRight className="w-4 h-4 inline ml-1" />
        </button>
      </div>
    </DashboardLayout>
  );

  if (!data) return (
    <DashboardLayout>
      <div className="max-w-lg mx-auto text-center py-20">
        <SpotifyLogo className="w-12 h-12 text-[#1DB954] mx-auto mb-4" weight="fill" />
        <h1 className="text-xl font-bold text-white mb-2">No Artist Linked</h1>
        <p className="text-sm text-gray-400 mb-4">Go to Settings &gt; Integrations to search and link your Spotify artist profile.</p>
        <button onClick={() => navigate('/settings')} className="px-5 py-2 bg-white/10 text-white rounded-full text-sm hover:bg-white/15">
          Open Settings
        </button>
      </div>
    </DashboardLayout>
  );

  const { artist, top_tracks, albums, related_artists } = data;

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="spotify-analytics">
        {/* Header */}
        <div className="flex items-center gap-4">
          {artist.image && <img src={artist.image} alt={artist.name} className="w-16 h-16 rounded-xl object-cover" />}
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <SpotifyLogo className="w-5 h-5 text-[#1DB954]" weight="fill" />
              <h1 className="text-xl font-bold text-white" data-testid="spotify-artist-name">{artist.name}</h1>
            </div>
            <div className="flex items-center gap-4 mt-1">
              <span className="text-xs text-gray-400"><Users className="w-3.5 h-3.5 inline mr-1" />{(artist.followers || 0).toLocaleString()} followers</span>
              <span className="text-xs text-gray-400"><Fire className="w-3.5 h-3.5 inline mr-1" />Popularity: {artist.popularity}/100</span>
              {artist.genres?.length > 0 && <span className="text-xs text-gray-500">{artist.genres.slice(0, 3).join(', ')}</span>}
            </div>
          </div>
          {artist.external_url && (
            <a href={artist.external_url} target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-[#1DB954]/10 text-[#1DB954] rounded-full text-xs font-bold hover:bg-[#1DB954]/20 flex items-center gap-1.5" data-testid="open-spotify-link">
              Open on Spotify <ArrowSquareOut className="w-3.5 h-3.5" />
            </a>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-[#141414] border border-white/5 rounded-xl p-4" data-testid="stat-followers">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Followers</p>
            <p className="text-2xl font-black text-white mt-1">{(artist.followers || 0).toLocaleString()}</p>
          </div>
          <div className="bg-[#141414] border border-white/5 rounded-xl p-4" data-testid="stat-popularity">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Popularity</p>
            <p className="text-2xl font-black text-[#1DB954] mt-1">{artist.popularity}<span className="text-sm text-gray-500">/100</span></p>
          </div>
          <div className="bg-[#141414] border border-white/5 rounded-xl p-4" data-testid="stat-tracks">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Top Tracks</p>
            <p className="text-2xl font-black text-white mt-1">{top_tracks?.length || 0}</p>
          </div>
          <div className="bg-[#141414] border border-white/5 rounded-xl p-4" data-testid="stat-releases">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Releases</p>
            <p className="text-2xl font-black text-white mt-1">{albums?.length || 0}</p>
          </div>
        </div>

        {/* Top Tracks */}
        {top_tracks?.length > 0 && (
          <div className="bg-[#141414] border border-white/5 rounded-xl overflow-hidden" data-testid="top-tracks-section">
            <div className="px-5 py-4 border-b border-white/5">
              <h2 className="text-sm font-bold text-white flex items-center gap-2"><Headphones className="w-4 h-4 text-[#1DB954]" /> Top Tracks on Spotify</h2>
            </div>
            <div className="divide-y divide-white/5">
              {top_tracks.map((track, i) => (
                <div key={i} className="flex items-center gap-3 px-5 py-3 hover:bg-white/[0.02] transition-colors" data-testid={`track-${i}`}>
                  <span className="text-xs text-gray-600 w-6 text-right font-mono">{i + 1}</span>
                  {track.album_image && <img src={track.album_image} alt="" className="w-10 h-10 rounded" />}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{track.name}</p>
                    <p className="text-xs text-gray-500 truncate">{track.album}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-24 bg-white/5 rounded-full h-1.5">
                      <div className="h-full bg-[#1DB954] rounded-full" style={{ width: `${track.popularity}%` }} />
                    </div>
                    <span className="text-[10px] text-gray-500 w-8 text-right">{track.popularity}</span>
                    {track.explicit && <span className="text-[9px] bg-white/10 text-gray-400 px-1.5 py-0.5 rounded font-bold">E</span>}
                    <span className="text-xs text-gray-600">
                      {Math.floor(track.duration_ms / 60000)}:{String(Math.floor((track.duration_ms % 60000) / 1000)).padStart(2, '0')}
                    </span>
                    {track.external_url && (
                      <a href={track.external_url} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-[#1DB954]">
                        <ArrowSquareOut className="w-3.5 h-3.5" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Albums / Releases */}
        {albums?.length > 0 && (
          <div data-testid="albums-section">
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2"><MusicNotes className="w-4 h-4 text-[#7C4DFF]" /> Discography</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {albums.map((album, i) => (
                <a key={i} href={album.external_url} target="_blank" rel="noopener noreferrer"
                  className="group bg-[#141414] border border-white/5 rounded-xl overflow-hidden hover:border-white/15 transition-all" data-testid={`album-${i}`}>
                  {album.image && <img src={album.image} alt={album.name} className="w-full aspect-square object-cover" />}
                  <div className="p-3">
                    <p className="text-xs font-bold text-white truncate group-hover:text-[#1DB954]">{album.name}</p>
                    <p className="text-[10px] text-gray-500 mt-0.5">{album.type === 'single' ? 'Single' : 'Album'} &middot; {album.release_date?.slice(0, 4)}</p>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Related Artists */}
        {related_artists?.length > 0 && (
          <div data-testid="related-artists-section">
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2"><Star className="w-4 h-4 text-[#FFD700]" /> Related Artists</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
              {related_artists.map((ra, i) => (
                <div key={i} className="bg-[#141414] border border-white/5 rounded-xl p-4 text-center hover:border-white/15 transition-all" data-testid={`related-${i}`}>
                  {ra.image && <img src={ra.image} alt={ra.name} className="w-14 h-14 rounded-full mx-auto mb-2 object-cover" />}
                  <p className="text-xs font-bold text-white truncate">{ra.name}</p>
                  <p className="text-[10px] text-gray-500 mt-0.5">{(ra.followers || 0).toLocaleString()} fans</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <p className="text-[10px] text-gray-600 text-center">Data from Spotify Web API &middot; Last fetched: {data.fetched_at ? new Date(data.fetched_at).toLocaleString() : 'just now'}</p>
      </div>
    </DashboardLayout>
  );
}
