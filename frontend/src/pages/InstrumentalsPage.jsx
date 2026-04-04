import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { useAuth } from '../App';
import { MusicNote, Lightning, ShieldCheck, Headset, Check, Star, PaperPlaneTilt, Play, Pause, SpeakerHigh, ShoppingCart, MagnifyingGlass, Sliders, X, ShareNetwork, Copy } from '@phosphor-icons/react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const licenseTiers = [
  { id: 'basic_lease', name: 'Basic Lease', price: 29.99, desc: 'Perfect for demos and mixtapes', features: ['MP3 File (320kbps)', 'Up to 5,000 streams', 'Non-exclusive license', 'Credit required'], color: '#7C4DFF' },
  { id: 'premium_lease', name: 'Premium Lease', price: 79.99, desc: 'For serious releases', features: ['WAV + MP3 Files', 'Up to 50,000 streams', 'Trackouts included', 'Non-exclusive license', 'Credit required'], color: '#E040FB', popular: true },
  { id: 'unlimited_lease', name: 'Unlimited Lease', price: 149.99, desc: 'Maximum flexibility', features: ['WAV + MP3 + Stems', 'Unlimited streams', 'Music video rights', 'Non-exclusive license', 'Credit required'], color: '#FF4081' },
  { id: 'exclusive', name: 'Exclusive Rights', price: 499.99, desc: 'Full ownership', features: ['All files + Stems', 'Unlimited usage', 'Full ownership', 'Beat removed from catalog', 'No credit required'], color: '#FFD700' },
];

const whyItems = [
  { icon: <MusicNote className="w-6 h-6" />, title: 'Industry Quality', desc: 'Professional studio-quality beats mixed and mastered to perfection', color: '#7C4DFF' },
  { icon: <Lightning className="w-6 h-6" />, title: 'Fast Delivery', desc: 'Get your beats delivered within 24-48 hours after purchase', color: '#E040FB' },
  { icon: <ShieldCheck className="w-6 h-6" />, title: '100% Original', desc: 'All beats are original compositions with no samples', color: '#FF4081' },
  { icon: <Headset className="w-6 h-6" />, title: 'Support', desc: 'Direct communication with the producer for revisions', color: '#FFD700' },
];

const genres = ['Hip-Hop/Rap', 'R&B/Soul', 'Afrobeats', 'Dancehall', 'Reggae', 'Pop', 'Trap', 'Drill', 'Gospel', 'Electronic/EDM', 'Latin', 'Other'];
const moods = ['Energetic/Hype', 'Chill/Laid-back', 'Dark/Moody', 'Emotional/Sad', 'Happy/Uplifting', 'Romantic', 'Aggressive', 'Party/Club'];

const BeatPreview = ({ beat, isPlaying, onToggle, audioRef }) => (
  <div className="flex items-center gap-4 bg-[#1a1a1a] rounded-2xl p-4 transition-all hover:bg-[#222]" data-testid={`beat-${beat.id}`}>
    <button onClick={() => onToggle(beat)}
      className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 transition-all"
      style={{ backgroundColor: isPlaying ? '#E040FB' : '#333' }}
      data-testid={`play-beat-${beat.id}`}>
      {isPlaying ? <Pause className="w-5 h-5 text-white" weight="fill" /> : <Play className="w-5 h-5 text-white" weight="fill" />}
    </button>
    <div className="flex-1 min-w-0">
      <h4 className="text-sm font-bold text-white truncate">{beat.title}</h4>
      <p className="text-xs text-gray-400">{beat.genre} &middot; {beat.bpm} BPM &middot; Key: {beat.key}</p>
    </div>
    {isPlaying && (
      <div className="flex items-center gap-2">
        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#E040FB]/15 text-[#E040FB] tracking-wider">TAGGED</span>
        <div className="flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="w-1 bg-[#E040FB] rounded-full animate-pulse" style={{
              height: `${12 + Math.random() * 16}px`,
              animationDelay: `${i * 0.1}s`,
              animationDuration: `${0.4 + Math.random() * 0.3}s`
            }} />
          ))}
        </div>
      </div>
    )}
    <div className="flex items-center gap-3 text-xs text-gray-400">
      <span>{beat.duration || '--:--'}</span>
      <span className="px-2 py-0.5 rounded-full bg-white/5">{beat.mood}</span>
    </div>
  </div>
);

export default function InstrumentalsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [selectedLicense, setSelectedLicense] = useState('');
  const [selectedBeat, setSelectedBeat] = useState(null);
  const [purchaseStep, setPurchaseStep] = useState('license'); // license, contract, processing
  const [signerName, setSignerName] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [signingContract, setSigningContract] = useState(false);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [selectedMood, setSelectedMood] = useState('');
  const [form, setForm] = useState({ artist_name: '', email: '', phone: '', tempo_range: '', reference_tracks: '', budget: '', additional_notes: '' });
  const [submitted, setSubmitted] = useState(false);
  const [playingBeat, setPlayingBeat] = useState(null);
  const [beats, setBeats] = useState([]);
  const [loadingBeats, setLoadingBeats] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterKey, setFilterKey] = useState('');
  const [bpmRange, setBpmRange] = useState([60, 200]);
  const [sortBy, setSortBy] = useState('newest');
  const [showFilters, setShowFilters] = useState(false);
  const audioRef = useRef(null);
  const searchTimeout = useRef(null);

  const KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm'];

  useEffect(() => {
    fetchBeats();
    // Handle purchase cancel return
    const params = new URLSearchParams(window.location.search);
    if (params.get('purchase') === 'cancelled') {
      toast.error('Purchase was cancelled');
      window.history.replaceState({}, '', '/instrumentals');
    }
  }, []);

  const handleBuyBeat = async (beat, licenseType) => {
    if (!user) { navigate('/login'); return; }
    if (!signerName.trim() || !agreedToTerms) {
      toast.error('Please sign the contract first');
      return;
    }
    setSigningContract(true);
    try {
      const token = document.cookie.split(';').find(c => c.trim().startsWith('access_token='))?.split('=')[1]
        || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      // Step 1: Sign the contract
      const contractRes = await axios.post(`${API_URL}/api/beats/contract/sign`, {
        beat_id: beat.id, license_type: licenseType, signer_name: signerName.trim(),
      }, { headers, withCredentials: true });
      const contractId = contractRes.data.id;
      // Step 2: Create checkout session with contract
      const res = await axios.post(`${API_URL}/api/beats/purchase/checkout`, {
        beat_id: beat.id, license_type: licenseType, contract_id: contractId, origin_url: window.location.origin,
      }, { headers, withCredentials: true });
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to process order');
    } finally { setSigningContract(false); }
  };

  const openPurchaseModal = (beat) => {
    setSelectedBeat(beat);
    setSelectedLicense('basic_lease');
    setPurchaseStep('license');
    setSignerName('');
    setAgreedToTerms(false);
  };

  const licenseTermsMap = {
    basic_lease: { name: 'Basic Lease', rights: 'Non-exclusive license', files: 'MP3 (320kbps)', streams: 'Up to 5,000', sales: 'Up to 500', video: 'Not included', credit: 'Required', ownership: 'Producer retains ownership', duration: 'Perpetual (non-exclusive)' },
    premium_lease: { name: 'Premium Lease', rights: 'Non-exclusive license', files: 'WAV + MP3 + Trackouts', streams: 'Up to 50,000', sales: 'Up to 5,000', video: '1 music video', credit: 'Required', ownership: 'Producer retains ownership', duration: 'Perpetual (non-exclusive)' },
    unlimited_lease: { name: 'Unlimited Lease', rights: 'Non-exclusive license', files: 'WAV + MP3 + Stems', streams: 'Unlimited', sales: 'Unlimited', video: 'Unlimited', credit: 'Required', ownership: 'Producer retains ownership', duration: 'Perpetual (non-exclusive)' },
    exclusive: { name: 'Exclusive Rights', rights: 'Full ownership transfer', files: 'All files + Stems + Sessions', streams: 'Unlimited', sales: 'Unlimited', video: 'Unlimited', credit: 'Not required', ownership: 'Full ownership to buyer', duration: 'Perpetual (exclusive)' },
  };

  const fetchBeats = async (params = {}) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.search || searchQuery) queryParams.set('search', params.search || searchQuery);
      if (params.genre || selectedGenre) queryParams.set('genre', params.genre || selectedGenre);
      if (params.mood || selectedMood) queryParams.set('mood', params.mood || selectedMood);
      if (params.key || filterKey) queryParams.set('key', params.key || filterKey);
      if (bpmRange[0] > 60) queryParams.set('bpm_min', bpmRange[0]);
      if (bpmRange[1] < 200) queryParams.set('bpm_max', bpmRange[1]);
      if (sortBy !== 'newest') queryParams.set('sort_by', sortBy);
      const qs = queryParams.toString();
      const res = await axios.get(`${API_URL}/api/beats${qs ? '?' + qs : ''}`);
      setBeats(res.data.beats || []);
    } catch (err) {
      console.error('Failed to fetch beats:', err);
    } finally {
      setLoadingBeats(false);
    }
  };

  const handleSearchChange = (val) => {
    setSearchQuery(val);
    clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => fetchBeats({ search: val }), 300);
  };

  const applyFilters = () => { setLoadingBeats(true); fetchBeats(); };

  const clearFilters = () => {
    setSearchQuery(''); setSelectedGenre(''); setSelectedMood(''); setFilterKey('');
    setBpmRange([60, 200]); setSortBy('newest'); setShowFilters(false);
    setLoadingBeats(true); fetchBeats({ search: '', genre: '', mood: '', key: '' });
  };

  const sharebeat = (beat) => {
    const url = `${window.location.origin}/instrumentals?beat=${beat.id}`;
    navigator.clipboard.writeText(url).then(() => toast.success('Beat link copied!'));
  };

  const toggleBeat = (beat) => {
    if (playingBeat === beat.id) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setPlayingBeat(null);
    } else {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if (beat.audio_url) {
        const audio = new Audio(`${API_URL}/api/beats/${beat.id}/stream`);
        audio.play().catch(e => console.log('Audio play failed:', e));
        audio.onended = () => setPlayingBeat(null);
        audioRef.current = audio;
      }
      setPlayingBeat(beat.id);
    }
  };

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.artist_name || !form.email || !selectedGenre) return;
    setSubmitted(true);
  };

  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto bg-[#0a0a0a]" data-testid="instrumentals-page">
        {/* Hero Card */}
        <div className="mx-4 mt-4 rounded-3xl p-7 text-center bg-gradient-to-br from-[#7C4DFF] via-[#E040FB] to-[#FF4081]">
          <div className="w-[70px] h-[70px] rounded-full bg-white/20 mx-auto mb-5 flex items-center justify-center">
            <MusicNote className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-[28px] font-extrabold text-white mb-3">Need Beats or Instrumentals?</h1>
          <p className="text-[15px] text-white/85 leading-relaxed mb-6">Can't make your own beats? No problem! Get professional instrumentals with full rights or lease options.</p>
          <div className="space-y-3">
            {['Exclusive Rights Available', 'Affordable Lease Options', 'All Genres: Hip-Hop, R&B, Afrobeats, Dancehall', 'Custom Beats on Request'].map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-full bg-white flex items-center justify-center flex-shrink-0">
                  <Check className="w-4 h-4 text-[#7C4DFF]" weight="bold" />
                </div>
                <span className="text-[15px] font-semibold text-white text-left">{f}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Why Choose Us */}
        <div className="p-6 mt-4">
          <h2 className="text-sm font-bold text-[#E040FB] tracking-[3px] text-center mb-6">WHY CHOOSE US</h2>
          <div className="grid grid-cols-2 gap-4">
            {whyItems.map((item, i) => (
              <div key={i} className="bg-[#1a1a1a] rounded-2xl p-5 text-center">
                <div className="w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center" style={{ backgroundColor: `${item.color}20`, color: item.color }}>{item.icon}</div>
                <h3 className="text-sm font-bold text-white mb-2">{item.title}</h3>
                <p className="text-xs text-gray-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* License Tiers */}
        <div className="p-6">
          <h2 className="text-sm font-bold text-[#E040FB] tracking-[3px] text-center mb-2">LICENSING OPTIONS</h2>
          <p className="text-sm text-gray-400 text-center mb-6">Choose the right license for your project</p>
          <div className="space-y-4">
            {licenseTiers.map((tier) => (
              <button key={tier.id} onClick={() => setSelectedLicense(tier.id)}
                className={`w-full bg-[#1a1a1a] rounded-2xl p-6 text-left border-2 relative overflow-hidden transition-all ${selectedLicense === tier.id ? 'border-opacity-100' : 'border-opacity-30'}`}
                style={{ borderColor: tier.color }}
                data-testid={`tier-${tier.id}`}>
                {tier.popular && (
                  <span className="absolute top-0 right-0 px-4 py-1.5 rounded-bl-xl text-[10px] font-bold text-white tracking-wider" style={{ backgroundColor: tier.color }}>MOST POPULAR</span>
                )}
                {selectedLicense === tier.id && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold text-white mb-3" style={{ backgroundColor: tier.color }}>
                    <Check className="w-3 h-3" weight="bold" /> SELECTED
                  </span>
                )}
                <h3 className="text-lg font-bold mb-2" style={{ color: tier.color }}>{tier.name}</h3>
                <div className="flex items-start mb-2">
                  <span className="text-xl font-bold text-white mt-1">$</span>
                  <span className="text-5xl font-extrabold text-white leading-none">{Math.floor(tier.price)}</span>
                  <span className="text-xl font-bold text-white mt-1">.{String(Math.round((tier.price % 1) * 100)).padStart(2, '0')}</span>
                </div>
                <p className="text-sm text-gray-400 mb-4">{tier.desc}</p>
                <div className="space-y-2.5">
                  {tier.features.map((f, j) => (
                    <div key={j} className="flex items-center gap-2.5">
                      <Check className="w-4 h-4 flex-shrink-0" style={{ color: tier.color }} weight="bold" />
                      <span className="text-sm text-gray-300">{f}</span>
                    </div>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Beat Catalog - Real Data */}
        <div className="p-6">
          <h2 className="text-sm font-bold text-[#E040FB] tracking-[3px] text-center mb-2">BEAT CATALOG</h2>
          <p className="text-sm text-gray-400 text-center mb-6">Preview our latest beats — tap to play</p>

          {/* Search & Filter Bar */}
          <div className="space-y-3 mb-6">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <MagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input type="text" value={searchQuery} onChange={e => handleSearchChange(e.target.value)}
                  placeholder="Search beats by name, genre, mood..."
                  className="w-full bg-[#111] border border-[#333] rounded-xl pl-10 pr-4 py-3 text-white text-sm focus:border-[#E040FB]/50 focus:outline-none"
                  data-testid="beat-search-input" />
                {searchQuery && (
                  <button onClick={() => handleSearchChange('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white">
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
              <button onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-3 rounded-xl border text-sm font-medium flex items-center gap-2 transition-all ${showFilters ? 'bg-[#E040FB]/10 border-[#E040FB]/30 text-[#E040FB]' : 'bg-[#111] border-[#333] text-gray-400 hover:text-white'}`}
                data-testid="toggle-filters-btn">
                <Sliders className="w-4 h-4" /> Filters
              </button>
            </div>

            {showFilters && (
              <div className="bg-[#111] border border-[#333] rounded-xl p-4 space-y-4" data-testid="filters-panel">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Genre</label>
                    <select value={selectedGenre} onChange={e => { setSelectedGenre(e.target.value); }}
                      className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="filter-genre">
                      <option value="">All Genres</option>
                      {genres.map(g => <option key={g} value={g}>{g}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Mood</label>
                    <select value={selectedMood} onChange={e => { setSelectedMood(e.target.value); }}
                      className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="filter-mood">
                      <option value="">All Moods</option>
                      {moods.map(m => <option key={m} value={m}>{m}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Key</label>
                    <select value={filterKey} onChange={e => setFilterKey(e.target.value)}
                      className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="filter-key">
                      <option value="">All Keys</option>
                      {KEYS.map(k => <option key={k} value={k}>{k}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Sort By</label>
                    <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                      className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="filter-sort">
                      <option value="newest">Newest First</option>
                      <option value="price_low">Price: Low to High</option>
                      <option value="price_high">Price: High to Low</option>
                      <option value="bpm_low">BPM: Low to High</option>
                      <option value="bpm_high">BPM: High to Low</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-500 mb-1 block">BPM Range: {bpmRange[0]} - {bpmRange[1]}</label>
                  <div className="flex items-center gap-3">
                    <input type="range" min="60" max="200" value={bpmRange[0]} onChange={e => setBpmRange([parseInt(e.target.value), bpmRange[1]])}
                      className="flex-1 accent-[#E040FB]" data-testid="bpm-min-slider" />
                    <input type="range" min="60" max="200" value={bpmRange[1]} onChange={e => setBpmRange([bpmRange[0], parseInt(e.target.value)])}
                      className="flex-1 accent-[#E040FB]" data-testid="bpm-max-slider" />
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={applyFilters} className="flex-1 py-2 rounded-lg bg-[#E040FB] text-white text-sm font-bold hover:brightness-110 transition-all" data-testid="apply-filters-btn">
                    Apply Filters
                  </button>
                  <button onClick={clearFilters} className="px-4 py-2 rounded-lg bg-[#222] text-gray-400 text-sm font-medium hover:text-white transition-all" data-testid="clear-filters-btn">
                    Clear
                  </button>
                </div>
              </div>
            )}
          </div>

          {loadingBeats ? (
            <div className="flex justify-center py-8">
              <div className="w-8 h-8 border-2 border-[#E040FB] border-t-transparent rounded-full animate-spin" />
            </div>
          ) : beats.length > 0 ? (
            <div className="space-y-3">
              {beats.map(beat => (
                <div key={beat.id} className="flex items-center gap-3 bg-[#1a1a1a] rounded-2xl p-4 transition-all hover:bg-[#222]" data-testid={`beat-${beat.id}`}>
                  <button onClick={() => toggleBeat(beat)}
                    className="w-11 h-11 rounded-full flex items-center justify-center flex-shrink-0 transition-all"
                    style={{ backgroundColor: playingBeat === beat.id ? '#E040FB' : '#333' }}
                    data-testid={`play-beat-${beat.id}`}>
                    {playingBeat === beat.id ? <Pause className="w-5 h-5 text-white" weight="fill" /> : <Play className="w-5 h-5 text-white" weight="fill" />}
                  </button>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-white truncate">{beat.title}</h4>
                    <p className="text-xs text-gray-400">{beat.genre} &middot; {beat.bpm} BPM &middot; {beat.key}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 hidden sm:block">{beat.duration || '--:--'}</span>
                    <button onClick={() => sharebeat(beat)} className="p-2 rounded-full bg-white/5 hover:bg-white/10 text-gray-500 hover:text-white transition-all" data-testid={`share-beat-${beat.id}`}>
                      <ShareNetwork className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => { openPurchaseModal(beat); }}
                      className="flex items-center gap-1.5 px-3 py-2 rounded-full bg-[#E040FB] hover:brightness-110 text-white text-xs font-bold transition-all"
                      data-testid={`buy-beat-${beat.id}`}>
                      <ShoppingCart className="w-3.5 h-3.5" /> ${beat.prices?.basic_lease || '29.99'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 text-sm">No beats available yet. Check back soon!</div>
          )}
          <div className="mt-4 p-3 bg-[#1a1a1a] rounded-xl flex items-center gap-3">
            <SpeakerHigh className="w-5 h-5 text-[#E040FB] flex-shrink-0" />
            <p className="text-xs text-gray-400">Audio previews play tagged samples. Full untagged files are delivered after purchase.</p>
          </div>
        </div>

        {/* Request Custom Beat Form */}
        <div className="mx-4 mt-4 mb-8 rounded-3xl p-6 border border-[#333] bg-[#0a0a0a]" data-testid="beat-request-form">
          <div className="text-center mb-2">
            <h2 className="text-xl font-extrabold text-white tracking-[2px]">REQUEST A CUSTOM BEAT</h2>
          </div>
          <p className="text-sm text-gray-400 text-center mb-6">Fill out the form below and we'll get back to you within 24-48 hours</p>

          {submitted ? (
            <div className="text-center py-8" data-testid="request-success">
              <div className="w-[90px] h-[90px] rounded-full bg-gradient-to-r from-[#4CAF50] to-[#2E7D32] mx-auto mb-6 flex items-center justify-center">
                <Check className="w-10 h-10 text-white" weight="bold" />
              </div>
              <h3 className="text-2xl font-extrabold text-white mb-3">Request Submitted!</h3>
              <p className="text-[15px] text-gray-400 leading-relaxed mb-6">We've received your beat request. Our team will review your requirements and contact you within 24-48 hours.</p>
              <button onClick={() => { setSubmitted(false); setForm({ artist_name: '', email: '', phone: '', tempo_range: '', reference_tracks: '', budget: '', additional_notes: '' }); setSelectedGenre(''); setSelectedMood(''); }}
                className="px-7 py-3.5 rounded-full bg-[#333] text-white text-sm font-bold tracking-wider">
                SUBMIT ANOTHER REQUEST
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <h3 className="text-base font-bold text-[#E040FB] mb-4">Your Information</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Artist/Producer Name *</label>
                    <input type="text" value={form.artist_name} onChange={(e) => setForm({ ...form, artist_name: e.target.value })}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white" data-testid="req-artist-name" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Email Address *</label>
                    <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white" data-testid="req-email" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Phone Number (Optional)</label>
                    <input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white" />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-base font-bold text-[#E040FB] mb-4">Beat Requirements</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Genre *</label>
                    <div className="flex flex-wrap gap-2.5">
                      {genres.map((g) => (
                        <button type="button" key={g} onClick={() => setSelectedGenre(g)}
                          className={`px-4 py-2.5 rounded-full text-[13px] font-medium border transition-all ${selectedGenre === g ? 'bg-[#7C4DFF] border-[#7C4DFF] text-white' : 'bg-[#111] border-[#333] text-gray-400'}`}
                          data-testid={`genre-${g.toLowerCase().replace(/[^a-z]/g, '-')}`}>
                          {g}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Mood/Vibe</label>
                    <div className="flex flex-wrap gap-2.5">
                      {moods.map((m) => (
                        <button type="button" key={m} onClick={() => setSelectedMood(m)}
                          className={`px-4 py-2.5 rounded-full text-[13px] font-medium border transition-all ${selectedMood === m ? 'bg-[#E040FB] border-[#E040FB] text-white' : 'bg-[#111] border-[#333] text-gray-400'}`}>
                          {m}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Tempo Range (BPM)</label>
                    <input type="text" value={form.tempo_range} onChange={(e) => setForm({ ...form, tempo_range: e.target.value })} placeholder="e.g., 120-140"
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white placeholder-gray-600" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Reference Tracks</label>
                    <textarea value={form.reference_tracks} onChange={(e) => setForm({ ...form, reference_tracks: e.target.value })} placeholder="Share links or names of tracks with a similar vibe" rows={3}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white placeholder-gray-600 resize-none" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Budget Range</label>
                    <input type="text" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} placeholder="e.g., $100-$300"
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white placeholder-gray-600" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Additional Notes</label>
                    <textarea value={form.additional_notes} onChange={(e) => setForm({ ...form, additional_notes: e.target.value })} placeholder="Any specific requirements..." rows={3}
                      className="w-full bg-[#111] border border-[#333] rounded-xl px-4 py-4 text-white placeholder-gray-600 resize-none" />
                  </div>
                </div>
              </div>

              {selectedLicense && (
                <div className="flex items-center gap-2.5 p-4 rounded-xl bg-[#4CAF50]/10 border border-[#4CAF50]/30">
                  <Check className="w-5 h-5 text-[#4CAF50]" weight="bold" />
                  <span className="text-sm text-[#4CAF50] font-semibold">Selected: {licenseTiers.find(t => t.id === selectedLicense)?.name}</span>
                </div>
              )}

              <button type="submit"
                className="w-full py-4 rounded-full bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white font-bold tracking-[2px] flex items-center justify-center gap-2 hover:brightness-110 transition-all"
                data-testid="submit-beat-request">
                <PaperPlaneTilt className="w-5 h-5" /> SUBMIT REQUEST
              </button>
            </form>
          )}
        </div>

        {/* Beat Purchase Modal — Multi-Step */}
        {selectedBeat && (
          <div className="fixed inset-0 bg-black/80 z-50 flex items-end sm:items-center justify-center" onClick={() => setSelectedBeat(null)}>
            <div className="bg-[#111] border border-white/10 rounded-t-3xl sm:rounded-3xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()} data-testid="purchase-modal">
              <div className="w-10 h-1 bg-gray-600 rounded-full mx-auto mb-5 sm:hidden" />

              {/* Steps Indicator */}
              <div className="flex items-center justify-center gap-2 mb-5">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${purchaseStep === 'license' ? 'bg-[#7C4DFF] text-white' : 'bg-[#7C4DFF]/20 text-[#7C4DFF]'}`}>1</div>
                <div className="w-8 h-0.5 bg-[#333]" />
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${purchaseStep === 'contract' ? 'bg-[#E040FB] text-white' : 'bg-[#333] text-gray-500'}`}>2</div>
                <div className="w-8 h-0.5 bg-[#333]" />
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold bg-[#333] text-gray-500">3</div>
              </div>

              <h3 className="text-lg font-extrabold text-white mb-1">{selectedBeat.title}</h3>
              <p className="text-sm text-gray-400 mb-5">{selectedBeat.genre} &middot; {selectedBeat.bpm} BPM &middot; Key: {selectedBeat.key}</p>

              {/* Step 1: License Selection */}
              {purchaseStep === 'license' && (
                <>
                  <p className="text-xs font-bold text-[#E040FB] tracking-[2px] mb-3">SELECT LICENSE</p>
                  <div className="space-y-2.5 mb-5">
                    {licenseTiers.map(tier => (
                      <button key={tier.id} onClick={() => setSelectedLicense(tier.id)}
                        className={`w-full flex items-center justify-between p-4 rounded-xl border-2 transition-all ${
                          selectedLicense === tier.id ? 'border-opacity-100 bg-white/5' : 'border-opacity-20'
                        }`} style={{ borderColor: tier.color }}
                        data-testid={`modal-tier-${tier.id}`}>
                        <div>
                          <p className="text-sm font-bold text-white">{tier.name}</p>
                          <p className="text-xs text-gray-500">{tier.desc}</p>
                        </div>
                        <span className="text-lg font-extrabold" style={{ color: tier.color }}>
                          ${selectedBeat.prices?.[tier.id] || tier.price}
                        </span>
                      </button>
                    ))}
                  </div>
                  <button onClick={() => { if (!user) { navigate('/login'); return; } setPurchaseStep('contract'); }}
                    disabled={!selectedLicense}
                    className="w-full py-4 rounded-full bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white font-bold tracking-[2px] hover:brightness-110 transition-all disabled:opacity-40"
                    data-testid="proceed-to-contract-btn">
                    REVIEW CONTRACT
                  </button>
                </>
              )}

              {/* Step 2: Contract Review & Sign */}
              {purchaseStep === 'contract' && (() => {
                const terms = licenseTermsMap[selectedLicense] || {};
                const price = selectedBeat.prices?.[selectedLicense] || licenseTiers.find(t => t.id === selectedLicense)?.price || 0;
                return (
                  <>
                    <p className="text-xs font-bold text-[#E040FB] tracking-[2px] mb-3">LICENSE AGREEMENT</p>

                    {/* Order Summary */}
                    <div className="bg-[#0a0a0a] border border-[#222] rounded-xl p-4 mb-4">
                      <p className="text-xs text-gray-500 mb-2 font-semibold tracking-wider">ORDER SUMMARY</p>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-300">{selectedBeat.title}</span>
                        <span className="text-sm font-bold text-white">${price}</span>
                      </div>
                      <p className="text-xs text-[#7C4DFF] font-medium">{terms.name}</p>
                    </div>

                    {/* License Terms */}
                    <div className="bg-[#0a0a0a] border border-[#222] rounded-xl p-4 mb-4">
                      <p className="text-xs text-gray-500 mb-3 font-semibold tracking-wider">LICENSE TERMS</p>
                      <div className="space-y-2">
                        {[
                          ['Rights', terms.rights],
                          ['Files Delivered', terms.files],
                          ['Streams', terms.streams],
                          ['Sales', terms.sales],
                          ['Music Video', terms.video],
                          ['Credit', terms.credit],
                          ['Ownership', terms.ownership],
                          ['Duration', terms.duration],
                        ].map(([label, val]) => (
                          <div key={label} className="flex justify-between text-xs">
                            <span className="text-gray-500">{label}</span>
                            <span className="text-gray-300 text-right max-w-[60%]">{val}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Binding Terms */}
                    <div className="bg-[#0a0a0a] border border-[#222] rounded-xl p-4 mb-4">
                      <p className="text-xs text-gray-500 mb-2 font-semibold tracking-wider">BINDING TERMS</p>
                      <p className="text-xs text-gray-400 leading-relaxed">
                        By signing below, you ("Licensee") agree to the terms of this license agreement with the producer ("Licensor").
                        This agreement grants you the rights described above for the beat "{selectedBeat.title}".
                        {selectedLicense === 'exclusive' ? ' Upon payment, full ownership transfers to the Licensee and the beat will be removed from the catalog.' : ' The Licensor retains ownership and may continue licensing this beat to others.'}
                        {' '}Violation of these terms may result in legal action. This contract is legally binding upon digital signature and payment.
                      </p>
                    </div>

                    {/* Digital Signature */}
                    <div className="bg-[#0a0a0a] border border-[#222] rounded-xl p-4 mb-4">
                      <p className="text-xs text-gray-500 mb-3 font-semibold tracking-wider">DIGITAL SIGNATURE</p>
                      <label className="block text-xs text-gray-400 mb-1.5">Full Legal Name *</label>
                      <input
                        type="text"
                        value={signerName}
                        onChange={(e) => setSignerName(e.target.value)}
                        placeholder="Type your full name to sign"
                        className="w-full bg-[#111] border border-[#333] rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-[#7C4DFF] placeholder-gray-600 mb-3"
                        data-testid="signer-name-input"
                      />
                      <label className="flex items-start gap-2.5 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={agreedToTerms}
                          onChange={(e) => setAgreedToTerms(e.target.checked)}
                          className="mt-0.5 w-4 h-4 rounded border-[#333] bg-[#111] accent-[#7C4DFF]"
                          data-testid="agree-terms-checkbox"
                        />
                        <span className="text-xs text-gray-400 leading-relaxed">
                          I have read and agree to the license terms above. I understand this is a legally binding agreement.
                        </span>
                      </label>
                    </div>

                    <div className="flex gap-2">
                      <button onClick={() => setPurchaseStep('license')}
                        className="flex-1 py-4 rounded-full border border-[#333] text-gray-400 font-bold text-sm hover:border-white hover:text-white transition-all"
                        data-testid="back-to-license-btn">
                        BACK
                      </button>
                      <button
                        onClick={() => handleBuyBeat(selectedBeat, selectedLicense)}
                        disabled={!signerName.trim() || !agreedToTerms || signingContract}
                        className="flex-[2] py-4 rounded-full bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white font-bold tracking-[2px] flex items-center justify-center gap-2 hover:brightness-110 transition-all disabled:opacity-40"
                        data-testid="confirm-purchase-btn"
                      >
                        {signingContract ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> :
                          <><ShoppingCart className="w-5 h-5" /> SIGN &amp; PAY — ${price}</>}
                      </button>
                    </div>
                  </>
                );
              })()}

              <button onClick={() => setSelectedBeat(null)} className="w-full py-3 text-gray-400 text-sm mt-2 hover:text-white transition-colors">Cancel</button>
            </div>
          </div>
        )}

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
