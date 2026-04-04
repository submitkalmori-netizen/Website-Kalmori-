import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, SpotifyLogo, AppleLogo, InstagramLogo, TwitterLogo, MusicNotes, Disc, Play, Pause, ShareNetwork, CheckCircle, Copy, Users, QrCode, X, DownloadSimple } from '@phosphor-icons/react';
import { API, BACKEND_URL } from '../App';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.5, ease: [0.22, 1, 0.36, 1] } })
};

const SocialIcon = ({ url, icon: Icon, label, testId, themeColor }) => {
  if (!url) return null;
  const href = url.startsWith('http') ? url : (url.startsWith('@') ? `https://instagram.com/${url.replace('@', '')}` : `https://${url}`);
  return (
    <motion.a
      href={href} target="_blank" rel="noopener noreferrer"
      className="w-12 h-12 rounded-full bg-[#141414] border border-white/10 flex items-center justify-center text-white/80 transition-all duration-300 hover:scale-110"
      style={{ '--hover-bg': themeColor }}
      onMouseEnter={e => { e.currentTarget.style.backgroundColor = themeColor; e.currentTarget.style.color = '#fff'; }}
      onMouseLeave={e => { e.currentTarget.style.backgroundColor = '#141414'; e.currentTarget.style.color = 'rgba(255,255,255,0.8)'; }}
      whileTap={{ scale: 0.9 }}
      title={label}
      data-testid={testId}
    >
      <Icon className="w-5 h-5" weight="fill" />
    </motion.a>
  );
};

/* ============ Audio Preview Player ============ */
const AudioPreviewPlayer = ({ track, slug, themeColor, isPlaying, onPlay, onStop }) => {
  const progressRef = useRef(null);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(track.duration || 0);
  const audioRef = useRef(null);

  useEffect(() => {
    if (isPlaying) {
      if (!audioRef.current) {
        audioRef.current = new Audio(`${API}/artist/${slug}/track/${track.id}/preview`);
        audioRef.current.addEventListener('loadedmetadata', () => {
          if (audioRef.current) setDuration(Math.round(audioRef.current.duration));
        });
        audioRef.current.addEventListener('ended', () => { setProgress(0); onStop(); });
      }
      audioRef.current.play().catch(() => onStop());
      const iv = setInterval(() => {
        if (audioRef.current) setProgress((audioRef.current.currentTime / audioRef.current.duration) * 100 || 0);
      }, 200);
      return () => clearInterval(iv);
    } else {
      if (audioRef.current) { audioRef.current.pause(); audioRef.current.currentTime = 0; }
      setProgress(0);
    }
  }, [isPlaying]);

  useEffect(() => {
    return () => { if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; } };
  }, []);

  const handleSeek = (e) => {
    if (!audioRef.current || !isPlaying) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    audioRef.current.currentTime = pct * audioRef.current.duration;
  };

  const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

  return (
    <div className="flex items-center gap-3 w-full mt-2" data-testid={`audio-player-${track.id}`}>
      <button
        onClick={() => isPlaying ? onStop() : onPlay()}
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 transition-all hover:scale-110"
        style={{ backgroundColor: isPlaying ? themeColor : 'rgba(255,255,255,0.1)' }}
        data-testid={`play-btn-${track.id}`}
      >
        {isPlaying ? <Pause className="w-3.5 h-3.5 text-white" weight="fill" /> : <Play className="w-3.5 h-3.5 text-white" weight="fill" />}
      </button>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-white/70 truncate mb-1">{track.title}</p>
        <div className="relative h-1.5 bg-white/10 rounded-full cursor-pointer overflow-hidden" ref={progressRef} onClick={handleSeek}>
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{ width: `${progress}%`, backgroundColor: themeColor }}
            transition={{ duration: 0.1 }}
          />
        </div>
      </div>
      <span className="text-[10px] text-white/40 tabular-nums flex-shrink-0">{fmt(duration)}</span>
    </div>
  );
};

/* ============ Release Card ============ */
const ReleaseCard = ({ release, index, slug, themeColor, playingTrackId, onPlayTrack, onStopTrack }) => {
  const coverUrl = release.cover_art_url ? `${BACKEND_URL}/api/files/${release.cover_art_url}` : null;

  return (
    <motion.div
      custom={index + 4}
      initial="hidden" animate="visible" variants={fadeUp}
      className="group p-4 bg-[#141414]/60 backdrop-blur-xl border border-white/10 rounded-2xl hover:border-opacity-40 transition-all duration-300"
      style={{ '--card-border': themeColor }}
      onMouseEnter={e => e.currentTarget.style.borderColor = `${themeColor}66`}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'}
      data-testid={`release-card-${release.id}`}
    >
      <div className="flex items-center gap-4">
        {coverUrl ? (
          <img src={coverUrl} alt={release.title} className="w-16 h-16 rounded-lg object-cover flex-shrink-0" />
        ) : (
          <div className="w-16 h-16 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${themeColor}33, ${themeColor}11)` }}>
            <Disc className="w-7 h-7" style={{ color: themeColor }} />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white truncate">{release.title}</p>
          <p className="text-xs text-white/50 mt-0.5">
            {release.release_type && <span className="capitalize">{release.release_type}</span>}
            {release.genre && <span> &middot; {release.genre}</span>}
            {release.track_count > 0 && <span> &middot; {release.track_count} tracks</span>}
          </p>
          {release.total_streams > 0 && (
            <p className="text-[11px] font-medium mt-1" style={{ color: themeColor }}>
              {release.total_streams.toLocaleString()} streams
            </p>
          )}
        </div>
      </div>
      {/* Track list with audio previews */}
      {release.tracks?.length > 0 && (
        <div className="mt-3 space-y-1 border-t border-white/5 pt-3">
          {release.tracks.map((track) => (
            <AudioPreviewPlayer
              key={track.id}
              track={track}
              slug={slug}
              themeColor={themeColor}
              isPlaying={playingTrackId === track.id}
              onPlay={() => onPlayTrack(track.id)}
              onStop={onStopTrack}
            />
          ))}
        </div>
      )}
    </motion.div>
  );
};

/* ============ Pre-Save Card ============ */
const PreSaveCard = ({ campaign, index, themeColor }) => {
  const coverUrl = campaign.cover_art_url ? `${BACKEND_URL}/api/files/${campaign.cover_art_url}` : null;
  const releaseDate = campaign.release_date
    ? new Date(campaign.release_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    : null;

  return (
    <motion.div
      custom={index + 6}
      initial="hidden" animate="visible" variants={fadeUp}
      className="relative bg-[#141414] rounded-2xl border border-white/10 overflow-hidden group"
      data-testid={`presave-card-${campaign.id}`}
    >
      <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity duration-500 blur-xl"
        style={{ background: `linear-gradient(to right, ${themeColor}, #E040FB, ${themeColor})` }} />
      <div className="relative p-5">
        <div className="flex items-center gap-4 mb-4">
          {coverUrl ? (
            <img src={coverUrl} alt={campaign.release_title} className="w-20 h-20 rounded-xl object-cover" />
          ) : (
            <div className="w-20 h-20 rounded-xl flex items-center justify-center"
              style={{ background: `linear-gradient(135deg, ${themeColor}44, #E040FB44)` }}>
              <MusicNotes className="w-8 h-8 text-[#E040FB]" />
            </div>
          )}
          <div>
            <span className="inline-block px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-[#FFD700] bg-[#FFD700]/10 rounded-full mb-1">Upcoming</span>
            <p className="text-lg font-bold text-white">{campaign.release_title}</p>
            {releaseDate && <p className="text-xs text-white/50 mt-0.5">Dropping {releaseDate}</p>}
          </div>
        </div>
        {campaign.subscriber_count > 0 && (
          <p className="text-xs text-white/40 mb-3 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5" /> {campaign.subscriber_count.toLocaleString()} pre-saves
          </p>
        )}
        <Link
          to={`/presave/${campaign.id}`}
          className="block w-full py-3 text-white text-sm font-bold rounded-full text-center transition-all duration-300 active:scale-95"
          style={{ background: `linear-gradient(to right, ${themeColor}, #E040FB)`, boxShadow: `0 0 20px ${themeColor}33` }}
          data-testid={`presave-button-${campaign.id}`}
        >
          Pre-Save Now
        </Link>
      </div>
    </motion.div>
  );
};

/* ============ Share + QR Bottom Bar ============ */
const ShareBar = ({ slug, themeColor }) => {
  const [copied, setCopied] = useState(false);
  const [showQR, setShowQR] = useState(false);
  const profileUrl = `${window.location.origin}/artist/${slug}`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(profileUrl);
    } catch {
      const input = document.createElement('input');
      input.value = profileUrl;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadQR = () => {
    const a = document.createElement('a');
    a.href = `${API}/artist/${slug}/qr`;
    a.download = `${slug}-qr.png`;
    a.click();
  };

  return (
    <>
      {/* QR Modal */}
      <AnimatePresence>
        {showQR && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60] bg-black/80 backdrop-blur-md flex items-center justify-center px-6"
            onClick={() => setShowQR(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="bg-[#141414] border border-white/10 rounded-3xl p-8 max-w-sm w-full text-center relative"
              onClick={e => e.stopPropagation()}
              data-testid="qr-modal"
            >
              <button onClick={() => setShowQR(false)} className="absolute top-4 right-4 text-white/40 hover:text-white" data-testid="close-qr-btn">
                <X className="w-5 h-5" />
              </button>
              <p className="text-xs uppercase tracking-[0.2em] text-white/40 font-bold mb-4">Scan to visit profile</p>
              <div className="bg-[#0A0A0A] rounded-2xl p-4 inline-block mb-5">
                <img
                  src={`${API}/artist/${slug}/qr`}
                  alt="QR Code"
                  className="w-48 h-48 mx-auto"
                  data-testid="qr-code-img"
                />
              </div>
              <p className="text-xs text-white/50 mb-4 break-all">{profileUrl}</p>
              <button
                onClick={handleDownloadQR}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold text-white transition-all hover:brightness-110"
                style={{ backgroundColor: themeColor }}
                data-testid="download-qr-btn"
              >
                <DownloadSimple className="w-4 h-4" /> Download QR
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom bar */}
      <div className="fixed bottom-0 left-0 right-0 z-50">
        <div className="max-w-xl mx-auto">
          <motion.div
            initial={{ y: 60, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.4 }}
            className="backdrop-blur-2xl bg-[#0A0A0A]/80 border-t border-white/10 p-4 flex justify-center gap-3"
            data-testid="share-bar"
          >
            <motion.button
              onClick={handleCopy}
              className="flex items-center gap-2 px-5 py-2.5 bg-white/10 backdrop-blur-xl border border-white/10 rounded-full text-sm font-medium text-white hover:bg-white/20 transition-all active:scale-95"
              whileTap={{ scale: 0.95 }}
              data-testid="share-profile-btn"
            >
              {copied ? (
                <><CheckCircle className="w-4 h-4 text-[#22C55E]" weight="fill" /> Copied!</>
              ) : (
                <><Copy className="w-4 h-4" /> Share Profile</>
              )}
            </motion.button>
            <motion.button
              onClick={() => setShowQR(true)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-full text-sm font-medium text-white transition-all active:scale-95 border"
              style={{ borderColor: `${themeColor}66`, backgroundColor: `${themeColor}15` }}
              whileTap={{ scale: 0.95 }}
              data-testid="qr-code-btn"
            >
              <QrCode className="w-4 h-4" style={{ color: themeColor }} /> QR Code
            </motion.button>
          </motion.div>
        </div>
      </div>
    </>
  );
};

const formatNumber = (n) => {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
};

const ArtistProfilePage = () => {
  const { slug } = useParams();
  const [artist, setArtist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playingTrackId, setPlayingTrackId] = useState(null);

  useEffect(() => {
    fetchArtist();
  }, [slug]);

  const fetchArtist = async () => {
    try {
      const res = await fetch(`${API}/artist/${slug}`);
      if (!res.ok) {
        setError(res.status === 404 ? 'not_found' : 'error');
        return;
      }
      setArtist(await res.json());
    } catch {
      setError('error');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayTrack = useCallback((trackId) => {
    setPlayingTrackId(trackId);
  }, []);

  const handleStopTrack = useCallback(() => {
    setPlayingTrackId(null);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col items-center justify-center px-6" data-testid="artist-not-found">
        <MusicNotes className="w-16 h-16 text-white/20 mb-6" />
        <h1 className="text-2xl font-bold mb-2">
          {error === 'not_found' ? 'Artist Not Found' : 'Something went wrong'}
        </h1>
        <p className="text-white/50 text-sm mb-8">
          {error === 'not_found' ? "This profile doesn't exist or hasn't been set up yet." : 'Please try again later.'}
        </p>
        <Link to="/" className="px-6 py-2.5 bg-[#7C4DFF] rounded-full text-sm font-semibold hover:bg-[#7C4DFF]/80 transition-colors" data-testid="back-home-btn">
          Back to Home
        </Link>
      </div>
    );
  }

  const tc = artist.theme_color || '#7C4DFF';
  const avatarUrl = artist.avatar_url ? `${BACKEND_URL}/api/files/${artist.avatar_url}` : null;
  const hasSocials = artist.website || artist.spotify_url || artist.apple_music_url || artist.instagram || artist.twitter;
  const distributedReleases = artist.releases?.filter(r => r.status === 'distributed') || [];
  const pendingReleases = artist.releases?.filter(r => r.status === 'pending_review') || [];
  const allReleases = [...distributedReleases, ...pendingReleases];

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white relative overflow-hidden" data-testid="artist-profile-page">
      {/* Background atmosphere using theme color */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full blur-3xl"
          style={{ background: `radial-gradient(ellipse, ${tc}0D, ${tc}06, transparent)` }} />
      </div>

      {/* Powered by KALMORI */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="fixed top-4 left-1/2 -translate-x-1/2 z-50">
        <Link to="/" className="flex items-center gap-1.5 px-3 py-1.5 bg-[#141414]/80 backdrop-blur-xl border border-white/10 rounded-full" data-testid="kalmori-badge">
          <MusicNotes className="w-3.5 h-3.5" weight="fill" style={{ color: tc }} />
          <span className="text-[10px] font-bold tracking-[0.15em] text-white/60 uppercase">Kalmori</span>
        </Link>
      </motion.div>

      <div className="relative max-w-xl mx-auto px-4 sm:px-6 w-full pt-16 pb-28">
        {/* Hero: Avatar + Name + Bio */}
        <motion.div custom={0} initial="hidden" animate="visible" variants={fadeUp} className="flex flex-col items-center text-center mb-8">
          {avatarUrl ? (
            <img src={avatarUrl} alt={artist.artist_name}
              className="w-32 h-32 md:w-40 md:h-40 rounded-full border-2 border-white/10 object-cover mb-6"
              style={{ boxShadow: `0 0 40px ${tc}40` }}
              data-testid="artist-avatar" />
          ) : (
            <div className="w-32 h-32 md:w-40 md:h-40 rounded-full flex items-center justify-center mb-6"
              style={{ background: `linear-gradient(135deg, ${tc}, #E040FB)`, boxShadow: `0 0 40px ${tc}40` }}
              data-testid="artist-avatar"
            >
              <span className="text-5xl md:text-6xl font-extrabold text-white">
                {artist.artist_name?.charAt(0).toUpperCase() || 'A'}
              </span>
            </div>
          )}

          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/70" data-testid="artist-name">
            {artist.artist_name}
          </h1>

          {artist.genre && (
            <motion.p custom={1} initial="hidden" animate="visible" variants={fadeUp} className="text-sm uppercase tracking-[0.2em] text-white/40 mt-2 font-medium">
              {artist.genre}{artist.country ? ` \u00b7 ${artist.country}` : ''}
            </motion.p>
          )}

          {artist.bio && (
            <motion.p custom={2} initial="hidden" animate="visible" variants={fadeUp} className="text-base leading-relaxed text-white/60 mt-4 max-w-md">
              {artist.bio}
            </motion.p>
          )}

          {/* Stats */}
          {(artist.stats?.total_streams > 0 || artist.stats?.total_releases > 0) && (
            <motion.div custom={2} initial="hidden" animate="visible" variants={fadeUp} className="flex items-center gap-6 mt-5">
              {artist.stats.total_streams > 0 && (
                <div className="text-center" data-testid="stat-streams">
                  <p className="text-xl font-bold text-white">{formatNumber(artist.stats.total_streams)}</p>
                  <p className="text-[11px] text-white/40 uppercase tracking-wider">Streams</p>
                </div>
              )}
              {artist.stats.total_releases > 0 && (
                <div className="text-center" data-testid="stat-releases">
                  <p className="text-xl font-bold text-white">{artist.stats.total_releases}</p>
                  <p className="text-[11px] text-white/40 uppercase tracking-wider">Releases</p>
                </div>
              )}
            </motion.div>
          )}
        </motion.div>

        {/* Social Links */}
        {hasSocials && (
          <motion.div custom={3} initial="hidden" animate="visible" variants={fadeUp} className="flex items-center justify-center flex-wrap gap-3 mb-10">
            <SocialIcon url={artist.spotify_url} icon={SpotifyLogo} label="Spotify" testId="social-link-spotify" themeColor={tc} />
            <SocialIcon url={artist.apple_music_url} icon={AppleLogo} label="Apple Music" testId="social-link-apple" themeColor={tc} />
            <SocialIcon url={artist.instagram} icon={InstagramLogo} label="Instagram" testId="social-link-instagram" themeColor={tc} />
            <SocialIcon url={artist.twitter} icon={TwitterLogo} label="Twitter" testId="social-link-twitter" themeColor={tc} />
            <SocialIcon url={artist.website} icon={Globe} label="Website" testId="social-link-website" themeColor={tc} />
          </motion.div>
        )}

        {/* Pre-Save Campaigns */}
        {artist.presave_campaigns?.length > 0 && (
          <div className="mb-10" data-testid="presave-section">
            <motion.h2 custom={5} initial="hidden" animate="visible" variants={fadeUp} className="text-xs uppercase tracking-[0.2em] text-white/30 font-bold mb-4">Upcoming Releases</motion.h2>
            <div className="space-y-4">
              {artist.presave_campaigns.map((c, i) => (
                <PreSaveCard key={c.id} campaign={c} index={i} themeColor={tc} />
              ))}
            </div>
          </div>
        )}

        {/* Released Music */}
        {allReleases.length > 0 && (
          <div className="mb-10" data-testid="releases-section">
            <motion.h2 custom={4} initial="hidden" animate="visible" variants={fadeUp} className="text-xs uppercase tracking-[0.2em] text-white/30 font-bold mb-4">Music</motion.h2>
            <div className="space-y-3">
              {allReleases.map((r, i) => (
                <ReleaseCard key={r.id} release={r} index={i} slug={slug} themeColor={tc}
                  playingTrackId={playingTrackId} onPlayTrack={handlePlayTrack} onStopTrack={handleStopTrack} />
              ))}
            </div>
          </div>
        )}

        {/* Empty state */}
        {allReleases.length === 0 && !artist.presave_campaigns?.length && (
          <motion.div custom={4} initial="hidden" animate="visible" variants={fadeUp} className="text-center py-12">
            <Disc className="w-12 h-12 text-white/10 mx-auto mb-4" />
            <p className="text-white/30 text-sm">No releases yet. Stay tuned!</p>
          </motion.div>
        )}
      </div>

      {/* Sticky bottom share + QR bar */}
      <ShareBar slug={slug} themeColor={tc} />
    </div>
  );
};

export default ArtistProfilePage;
