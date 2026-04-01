import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Progress } from '../components/ui/progress';
import { 
  Disc, 
  UploadSimple,
  Play,
  Pause,
  Trash,
  Plus,
  CheckCircle,
  Globe,
  CurrencyDollar,
  MusicNotes,
  SpotifyLogo,
  AppleLogo,
  YoutubeLogo
} from '@phosphor-icons/react';
import { toast } from 'sonner';

const ReleaseDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [release, setRelease] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploadingCover, setUploadingCover] = useState(false);
  const [uploadingAudio, setUploadingAudio] = useState(false);
  const [stores, setStores] = useState([]);
  const [selectedStores, setSelectedStores] = useState([]);
  const [distributing, setDistributing] = useState(false);
  const [newTrack, setNewTrack] = useState({ title: '', track_number: 1 });
  const [showAddTrack, setShowAddTrack] = useState(false);
  const [playingTrack, setPlayingTrack] = useState(null);
  const [audioRef] = useState(new Audio());

  const fetchRelease = useCallback(async () => {
    try {
      const [releaseRes, storesRes] = await Promise.all([
        axios.get(`${API}/releases/${id}`),
        axios.get(`${API}/distributions/stores`)
      ]);
      setRelease(releaseRes.data);
      setStores(storesRes.data);
      setSelectedStores(storesRes.data.map(s => s.store_id));
    } catch (error) {
      toast.error('Failed to load release');
      navigate('/releases');
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    fetchRelease();
    
    // Check for payment status from URL
    const params = new URLSearchParams(window.location.search);
    const paymentStatus = params.get('payment');
    const sessionId = params.get('session_id');
    
    if (paymentStatus === 'success' && sessionId) {
      pollPaymentStatus(sessionId);
    }
    
    return () => {
      audioRef.pause();
    };
  }, [fetchRelease, audioRef]);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    if (attempts >= 5) {
      toast.info('Payment status check timed out. Please refresh.');
      return;
    }
    
    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      if (response.data.payment_status === 'paid') {
        toast.success('Payment successful!');
        fetchRelease();
        // Clean URL
        window.history.replaceState(null, '', window.location.pathname);
      } else {
        setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), 2000);
      }
    } catch (error) {
      console.error('Payment status check failed:', error);
    }
  };

  const handleCoverUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file');
      return;
    }
    
    setUploadingCover(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await axios.post(`${API}/releases/${id}/cover`, formData);
      toast.success('Cover art uploaded!');
      fetchRelease();
    } catch (error) {
      toast.error('Failed to upload cover art');
    } finally {
      setUploadingCover(false);
    }
  };

  const handleAddTrack = async () => {
    if (!newTrack.title) {
      toast.error('Please enter a track title');
      return;
    }
    
    try {
      await axios.post(`${API}/tracks`, {
        release_id: id,
        title: newTrack.title,
        track_number: release.tracks?.length + 1 || 1
      });
      toast.success('Track added!');
      setNewTrack({ title: '', track_number: 1 });
      setShowAddTrack(false);
      fetchRelease();
    } catch (error) {
      toast.error('Failed to add track');
    }
  };

  const handleAudioUpload = async (trackId, file) => {
    if (!file) return;
    
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/x-wav', 'audio/flac'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload WAV, MP3, or FLAC');
      return;
    }
    
    setUploadingAudio(trackId);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await axios.post(`${API}/tracks/${trackId}/audio`, formData);
      toast.success('Audio uploaded!');
      fetchRelease();
    } catch (error) {
      toast.error('Failed to upload audio');
    } finally {
      setUploadingAudio(null);
    }
  };

  const handleDeleteTrack = async (trackId) => {
    if (!window.confirm('Are you sure you want to delete this track?')) return;
    
    try {
      await axios.delete(`${API}/tracks/${trackId}`);
      toast.success('Track deleted');
      fetchRelease();
    } catch (error) {
      toast.error('Failed to delete track');
    }
  };

  const togglePlay = (track) => {
    if (playingTrack === track.id) {
      audioRef.pause();
      setPlayingTrack(null);
    } else {
      audioRef.src = `${API}/tracks/${track.id}/stream`;
      audioRef.play();
      setPlayingTrack(track.id);
    }
  };

  const handleCheckout = async () => {
    try {
      const response = await axios.post(`${API}/payments/checkout`, {
        release_id: id,
        origin_url: window.location.origin
      });
      
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else {
        // Free tier
        toast.success('Free tier activated!');
        fetchRelease();
      }
    } catch (error) {
      toast.error('Failed to initiate checkout');
    }
  };

  const handleDistribute = async () => {
    if (!release.cover_art_url) {
      toast.error('Please upload cover art first');
      return;
    }
    
    const readyTracks = release.tracks?.filter(t => t.audio_url);
    if (!readyTracks?.length) {
      toast.error('Please upload at least one track');
      return;
    }
    
    setDistributing(true);
    try {
      await axios.post(`${API}/distributions/submit/${id}`, selectedStores);
      toast.success('Distribution submitted!');
      fetchRelease();
    } catch (error) {
      const msg = error.response?.data?.detail || 'Distribution failed';
      toast.error(typeof msg === 'string' ? msg : 'Distribution failed');
    } finally {
      setDistributing(false);
    }
  };

  const toggleStore = (storeId) => {
    setSelectedStores(prev => 
      prev.includes(storeId) 
        ? prev.filter(s => s !== storeId)
        : [...prev, storeId]
    );
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-[#FF3B30] border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  if (!release) return null;

  const getStoreIcon = (storeId) => {
    switch (storeId) {
      case 'spotify': return <SpotifyLogo className="w-5 h-5" />;
      case 'apple_music': return <AppleLogo className="w-5 h-5" />;
      case 'youtube_music': return <YoutubeLogo className="w-5 h-5" />;
      default: return <Globe className="w-5 h-5" />;
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-8" data-testid="release-detail-page">
        {/* Header */}
        <div className="flex flex-col md:flex-row gap-6">
          {/* Cover Art */}
          <div className="w-48 h-48 flex-shrink-0">
            <label className="relative block w-full h-full bg-[#141414] border border-white/10 rounded-md overflow-hidden cursor-pointer group">
              {release.cover_art_url ? (
                <img 
                  src={`${API.replace('/api', '')}/api/files/${release.cover_art_url}`}
                  alt={release.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-[#71717A] group-hover:text-white transition-colors">
                  <UploadSimple className="w-8 h-8 mb-2" />
                  <span className="text-xs">Upload Cover</span>
                </div>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={handleCoverUpload}
                className="hidden"
                disabled={uploadingCover}
                data-testid="cover-upload-input"
              />
              {uploadingCover && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                  <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                </div>
              )}
            </label>
          </div>

          {/* Info */}
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs uppercase tracking-widest text-[#FF3B30] font-semibold">
                  {release.release_type}
                </span>
                <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mt-1">{release.title}</h1>
                <p className="text-[#A1A1AA] mt-1">{release.artist_name}</p>
              </div>
              <span className={`px-3 py-1 rounded text-xs capitalize ${
                release.status === 'distributed' ? 'bg-[#22C55E]/10 text-[#22C55E]' :
                release.status === 'processing' ? 'bg-[#FFCC00]/10 text-[#FFCC00]' :
                'bg-[#71717A]/10 text-[#71717A]'
              }`}>
                {release.status}
              </span>
            </div>
            
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
              <div>
                <p className="text-xs text-[#71717A] uppercase">UPC</p>
                <p className="font-mono text-sm mt-1">{release.upc}</p>
              </div>
              <div>
                <p className="text-xs text-[#71717A] uppercase">Genre</p>
                <p className="text-sm mt-1">{release.genre}</p>
              </div>
              <div>
                <p className="text-xs text-[#71717A] uppercase">Release Date</p>
                <p className="text-sm mt-1">{release.release_date}</p>
              </div>
              <div>
                <p className="text-xs text-[#71717A] uppercase">Tracks</p>
                <p className="text-sm mt-1">{release.track_count}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tracks */}
        <div className="bg-[#141414] border border-white/10 rounded-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-medium flex items-center gap-2">
              <MusicNotes className="w-5 h-5 text-[#FF3B30]" />
              Tracks
            </h2>
            <Button
              size="sm"
              onClick={() => setShowAddTrack(!showAddTrack)}
              className="bg-white/10 hover:bg-white/20 text-white"
              data-testid="add-track-btn"
            >
              <Plus className="w-4 h-4 mr-1" /> Add Track
            </Button>
          </div>

          {showAddTrack && (
            <div className="flex gap-3 mb-6 p-4 bg-[#0A0A0A] rounded-md">
              <Input
                placeholder="Track title"
                value={newTrack.title}
                onChange={(e) => setNewTrack({ ...newTrack, title: e.target.value })}
                className="bg-[#141414] border-white/10 text-white"
                data-testid="new-track-title-input"
              />
              <Button onClick={handleAddTrack} className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white" data-testid="save-track-btn">
                Save
              </Button>
            </div>
          )}

          {release.tracks?.length === 0 ? (
            <div className="text-center py-8 text-[#71717A]">
              <Disc className="w-12 h-12 mx-auto mb-3" />
              <p>No tracks yet. Add your first track above.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {release.tracks?.map((track, index) => (
                <div 
                  key={track.id}
                  className="flex items-center gap-4 p-3 rounded-md hover:bg-white/5 transition-colors"
                >
                  <span className="w-6 text-center text-sm text-[#71717A] font-mono">
                    {index + 1}
                  </span>
                  
                  {track.audio_url ? (
                    <button
                      onClick={() => togglePlay(track)}
                      className="w-8 h-8 flex items-center justify-center rounded-full bg-[#FF3B30] hover:bg-[#FF3B30]/80 transition-colors"
                      data-testid={`play-track-${track.id}`}
                    >
                      {playingTrack === track.id ? (
                        <Pause className="w-4 h-4 text-white" weight="fill" />
                      ) : (
                        <Play className="w-4 h-4 text-white" weight="fill" />
                      )}
                    </button>
                  ) : (
                    <label className="w-8 h-8 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 cursor-pointer transition-colors">
                      <UploadSimple className="w-4 h-4" />
                      <input
                        type="file"
                        accept="audio/*"
                        onChange={(e) => handleAudioUpload(track.id, e.target.files?.[0])}
                        className="hidden"
                        data-testid={`upload-audio-${track.id}`}
                      />
                    </label>
                  )}
                  
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{track.title}</p>
                    <p className="text-xs text-[#71717A] font-mono">{track.isrc}</p>
                  </div>
                  
                  {track.duration && (
                    <span className="text-sm text-[#71717A] font-mono">
                      {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
                    </span>
                  )}
                  
                  <span className={`text-xs px-2 py-1 rounded ${
                    track.status === 'ready' ? 'bg-[#22C55E]/10 text-[#22C55E]' : 'bg-[#FFCC00]/10 text-[#FFCC00]'
                  }`}>
                    {track.status}
                  </span>
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDeleteTrack(track.id)}
                    className="text-[#71717A] hover:text-[#FF3B30]"
                    data-testid={`delete-track-${track.id}`}
                  >
                    <Trash className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Distribution */}
        {release.status !== 'distributed' && (
          <div className="bg-[#141414] border border-white/10 rounded-md p-6">
            <h2 className="text-lg font-medium mb-6 flex items-center gap-2">
              <Globe className="w-5 h-5 text-[#007AFF]" />
              Distribution
            </h2>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-6">
              {stores.map((store) => (
                <button
                  key={store.store_id}
                  onClick={() => toggleStore(store.store_id)}
                  className={`p-3 rounded-md border transition-all ${
                    selectedStores.includes(store.store_id)
                      ? 'border-[#FF3B30] bg-[#FF3B30]/10'
                      : 'border-white/10 hover:border-white/30'
                  }`}
                  data-testid={`store-${store.store_id}`}
                >
                  <div className="flex flex-col items-center gap-2">
                    {getStoreIcon(store.store_id)}
                    <span className="text-xs">{store.store_name}</span>
                    {selectedStores.includes(store.store_id) && (
                      <CheckCircle className="w-4 h-4 text-[#22C55E]" />
                    )}
                  </div>
                </button>
              ))}
            </div>

            {release.payment_status !== 'paid' && release.payment_status !== 'free_tier' ? (
              <div className="flex items-center justify-between p-4 bg-[#0A0A0A] rounded-md mb-4">
                <div>
                  <p className="font-medium flex items-center gap-2">
                    <CurrencyDollar className="w-5 h-5 text-[#FFCC00]" />
                    Payment Required
                  </p>
                  <p className="text-sm text-[#A1A1AA]">
                    ${release.release_type === 'single' ? '20.00' : release.release_type === 'ep' ? '35.00' : '50.00'} for {release.release_type} or use free tier (15% share)
                  </p>
                </div>
                <Button 
                  onClick={handleCheckout}
                  className="bg-[#FFCC00] hover:bg-[#FFCC00]/90 text-black"
                  data-testid="checkout-btn"
                >
                  Pay Now
                </Button>
              </div>
            ) : (
              <Button
                onClick={handleDistribute}
                disabled={distributing || selectedStores.length === 0}
                className="w-full bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white"
                data-testid="distribute-btn"
              >
                {distributing ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>Distribute to {selectedStores.length} Platforms</>
                )}
              </Button>
            )}
          </div>
        )}

        {/* Distribution Status */}
        {release.status === 'distributed' && (
          <div className="bg-[#141414] border border-[#22C55E]/30 rounded-md p-6">
            <div className="flex items-center gap-3 text-[#22C55E] mb-4">
              <CheckCircle className="w-6 h-6" weight="fill" />
              <h2 className="text-lg font-medium">Distributed Successfully</h2>
            </div>
            <p className="text-[#A1A1AA] text-sm">
              Your release has been submitted to streaming platforms. It may take 24-48 hours to appear on all stores.
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default ReleaseDetailPage;
