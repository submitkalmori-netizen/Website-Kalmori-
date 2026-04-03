import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { useAuth, API } from '../App';
import { ArrowLeft, ArrowRight, MusicNote, Image, Disc, Globe, PaperPlaneTilt, Check, Upload, Plus, Trash, X, Info, CaretDown, CaretUp, PencilSimple, Warning, Barcode, VinylRecord, FileAudio } from '@phosphor-icons/react';
import axios from 'axios';
import { toast } from 'sonner';

const TABS = [
  { id: 'general', label: 'General Information' },
  { id: 'tracks', label: 'Tracks & Assets' },
  { id: 'territory', label: 'Territory & Platform Rights' },
  { id: 'summary', label: 'Summary' },
];

const PRODUCT_TYPES = ['Single', 'EP', 'Album', 'Compilation', 'Mixtape'];
const GENRES = ['Hip-Hop/Rap', 'R&B/Soul', 'Pop', 'Afrobeats', 'Dancehall', 'Reggae', 'Drill', 'Trap', 'Gospel', 'Electronic/EDM', 'Latin', 'Rock', 'Country', 'Jazz', 'Classical', 'Amapiano', 'Afropop', 'Highlife', 'Soca', 'Kompa', 'Other'];
const LANGUAGES = [
  { code: 'en', name: 'English' }, { code: 'es', name: 'Spanish' }, { code: 'fr', name: 'French' },
  { code: 'pt', name: 'Portuguese' }, { code: 'de', name: 'German' }, { code: 'it', name: 'Italian' },
  { code: 'ja', name: 'Japanese' }, { code: 'ko', name: 'Korean' }, { code: 'zh', name: 'Chinese' },
  { code: 'ar', name: 'Arabic' }, { code: 'hi', name: 'Hindi' }, { code: 'yo', name: 'Yoruba' },
  { code: 'ig', name: 'Igbo' }, { code: 'sw', name: 'Swahili' }, { code: 'ha', name: 'Hausa' },
  { code: 'nl', name: 'Dutch' }, { code: 'ru', name: 'Russian' }, { code: 'tr', name: 'Turkish' },
];

const DISTRIBUTED_PLATFORMS = [
  { id: 'spotify', name: 'Spotify', color: '#1DB954' },
  { id: 'apple', name: 'Apple Music', color: '#FC3C44' },
  { id: 'amazon', name: 'Amazon Music', color: '#FF9900' },
  { id: 'youtube_art', name: 'YouTube Art Track', color: '#FF0000' },
  { id: 'tidal', name: 'Tidal', color: '#00FFFF' },
  { id: 'deezer', name: 'Deezer', color: '#A238FF' },
  { id: 'tiktok', name: 'TikTok', color: '#010101' },
  { id: 'tiktok_video', name: 'TikTok Music Video', color: '#010101' },
  { id: 'soundcloud', name: 'SoundCloud', color: '#FF5500' },
  { id: 'audiomack', name: 'Audiomack', color: '#FFA200' },
  { id: 'boomplay', name: 'Boomplay', color: '#E23145' },
  { id: 'pandora', name: 'Pandora', color: '#005483' },
  { id: 'spotify_video', name: 'Spotify Video', color: '#1DB954' },
  { id: '7digital', name: '7digital', color: '#0070C0' },
  { id: 'beatport', name: 'Beatport', color: '#94D500' },
  { id: 'beatsource', name: 'Beatsource', color: '#333333' },
  { id: 'kkbox', name: 'KKBox', color: '#0091FF' },
  { id: 'kuack', name: 'Kuack Media', color: '#FF6B00' },
  { id: 'nuuday', name: 'Nuuday', color: '#00C853' },
  { id: 'qobuz', name: 'Qobuz', color: '#2C2C2C' },
  { id: 'rytebox', name: 'RyteBox-SR1', color: '#4A90D9' },
  { id: 'fb_fingerprint', name: 'Facebook Fingerprint', color: '#1877F2' },
  { id: 'fb_library', name: 'Facebook Library', color: '#1877F2' },
  { id: 'imusica', name: 'iMusica', color: '#1A237E' },
  { id: 'zojakreporting', name: 'ZojakReporting', color: '#00BFA5' },
  { id: 'audible', name: 'Audible', color: '#F7991C' },
];

const NOT_DISTRIBUTED_PLATFORMS = [
  { id: 'ami', name: 'AMI', color: '#E53935' },
  { id: 'anghami', name: 'Anghami Music', color: '#9C27B0' },
  { id: 'fb_video_fp', name: 'Facebook Video Fingerprint', color: '#1877F2' },
  { id: 'hungama', name: 'Hungama', color: '#FF5722' },
  { id: 'juno', name: 'Juno Download', color: '#333333' },
  { id: 'kanjian', name: 'Kanjian', color: '#2196F3' },
  { id: 'netease', name: 'NetEase', color: '#E53935' },
  { id: 'pretzel', name: 'Pretzel', color: '#4CAF50' },
  { id: 'reggae_zion', name: 'Reggae Zion', color: '#FFD600' },
  { id: 'yt_content_id', name: 'YouTube Content ID', color: '#FF0000' },
  { id: 'iheart', name: 'iHeart Radio', color: '#C62828' },
];

const FieldLabel = ({ label, required, tooltip }) => (
  <label className="flex items-center gap-1.5 text-sm text-gray-300 mb-1.5 font-medium">
    {label}{required && <span className="text-[#E040FB]">*</span>}
    {tooltip && (
      <span className="group relative cursor-help">
        <Info className="w-3.5 h-3.5 text-gray-500" />
        <span className="hidden group-hover:block absolute left-full ml-2 top-1/2 -translate-y-1/2 bg-[#1a1a1a] border border-white/10 rounded-lg px-3 py-2 text-xs text-gray-300 w-56 z-50 shadow-xl">{tooltip}</span>
      </span>
    )}
  </label>
);

const InputField = ({ value, onChange, placeholder, testId, type = 'text', disabled }) => (
  <input type={type} value={value} onChange={onChange} placeholder={placeholder} disabled={disabled}
    className="w-full bg-[#0d0d1a] border border-white/10 rounded-lg px-4 py-3 text-white text-sm focus:border-[#7C4DFF]/50 focus:outline-none transition-colors disabled:opacity-50"
    data-testid={testId} />
);

const SelectField = ({ value, onChange, options, placeholder, testId }) => (
  <select value={value} onChange={onChange} data-testid={testId}
    className="w-full bg-[#0d0d1a] border border-white/10 rounded-lg px-4 py-3 text-white text-sm focus:border-[#7C4DFF]/50 focus:outline-none transition-colors appearance-none">
    {placeholder && <option value="">{placeholder}</option>}
    {options.map(o => typeof o === 'string'
      ? <option key={o} value={o}>{o}</option>
      : <option key={o.value || o.code} value={o.value || o.code}>{o.label || o.name}</option>
    )}
  </select>
);

export default function ReleaseWizardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [loading, setLoading] = useState(false);
  const [releaseId, setReleaseId] = useState(null);
  const [tabComplete, setTabComplete] = useState({ general: false, tracks: false, territory: false });

  // General Information
  const [form, setForm] = useState({
    title: '', title_version: '', label: user?.artist_name || '', upc: '',
    product_type: '', genre: 'Hip-Hop/Rap', is_compilation: false,
    metadata_language: 'en', catalog_number: '', production_year: new Date().getFullYear().toString(),
    copyright_line: '', production_line: '', release_date: '',
    main_artist: user?.artist_name || '',
  });
  const [coverFile, setCoverFile] = useState(null);
  const [coverPreview, setCoverPreview] = useState(null);
  const [bookletFile, setBookletFile] = useState(null);
  const [bookletName, setBookletName] = useState('');

  // Tracks
  const defaultTrack = {
    title: '', title_version: '', track_number: 1, explicit: false,
    audioFile: null, audioName: '', isrc: '', dolby_atmos_isrc: '', iswc: '',
    audio_language: 'English', production: '', publisher: '',
    preview_start: '00:30', preview_end: '00:00',
    artists: [{ role: 'Main Artist', name: '' }],
    main_contributors: [{ role: 'Composer', name: '' }, { role: 'Lyricist', name: '' }],
    contributors: [],
  };
  const [volumes, setVolumes] = useState([{ id: 1, tracks: [{ ...defaultTrack }] }]);

  // Territory
  const [territory, setTerritory] = useState('worldwide');
  const [distributedPlatforms, setDistributedPlatforms] = useState(DISTRIBUTED_PLATFORMS.map(p => p.id));
  const [rightsConfirmed, setRightsConfirmed] = useState('yes');

  const token = document.cookie.split(';').find(c => c.trim().startsWith('access_token='))?.split('=')[1] || localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  const updateForm = (field, value) => setForm(prev => ({ ...prev, [field]: value }));

  const generateUPC = () => {
    const upc = '0' + Array.from({ length: 11 }, () => Math.floor(Math.random() * 10)).join('');
    updateForm('upc', upc);
    toast.success('UPC generated');
  };

  // Cover art
  const handleCoverSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setCoverFile(file);
      const reader = new FileReader();
      reader.onload = (ev) => setCoverPreview(ev.target.result);
      reader.readAsDataURL(file);
    }
  };

  const handleBookletSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) { setBookletFile(file); setBookletName(file.name); }
  };

  // Track management
  const addTrack = (volIdx) => {
    setVolumes(prev => prev.map((v, i) => i === volIdx ? {
      ...v, tracks: [...v.tracks, { ...defaultTrack, track_number: v.tracks.length + 1 }]
    } : v));
  };

  const removeTrack = (volIdx, trackIdx) => {
    setVolumes(prev => prev.map((v, i) => i === volIdx ? {
      ...v, tracks: v.tracks.filter((_, ti) => ti !== trackIdx).map((t, ti) => ({ ...t, track_number: ti + 1 }))
    } : v));
  };

  const updateTrack = (volIdx, trackIdx, field, value) => {
    setVolumes(prev => prev.map((v, i) => i === volIdx ? {
      ...v, tracks: v.tracks.map((t, ti) => ti === trackIdx ? { ...t, [field]: value } : t)
    } : v));
  };

  const handleAudioSelect = (volIdx, trackIdx, file) => {
    if (file) {
      updateTrack(volIdx, trackIdx, 'audioFile', file);
      updateTrack(volIdx, trackIdx, 'audioName', file.name);
      if (!volumes[volIdx].tracks[trackIdx].title) {
        const name = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ');
        updateTrack(volIdx, trackIdx, 'title', name);
      }
    }
  };

  const addVolume = () => {
    setVolumes(prev => [...prev, { id: prev.length + 1, tracks: [{ ...defaultTrack }] }]);
  };

  // Validation
  const getValidation = () => {
    const missing = [];
    if (!form.title) missing.push('Album Title');
    if (!form.product_type) missing.push('Product Type');
    if (!form.upc) missing.push('UPC');
    if (!form.metadata_language) missing.push('Metadata Language');
    if (!form.copyright_line) missing.push('© Copyright Line');
    if (!form.production_line) missing.push('℗ Production Line');
    if (!form.genre) missing.push('Main Genre');
    if (!form.main_artist) missing.push('Main Artist');
    if (!coverFile && !coverPreview) missing.push('Cover Art');
    if (!form.release_date) missing.push('Release Date');
    const allTracks = volumes.flatMap(v => v.tracks);
    const hasTrack = allTracks.some(t => t.title);
    if (!hasTrack) missing.push('At least one track');
    return missing;
  };

  // Save & Navigate
  const goToTab = (tabId) => {
    setActiveTab(tabId);
  };

  const saveAndNext = async () => {
    const tabIdx = TABS.findIndex(t => t.id === activeTab);
    if (tabIdx < TABS.length - 1) {
      // Mark current tab as complete
      setTabComplete(prev => ({ ...prev, [activeTab]: true }));
      setActiveTab(TABS[tabIdx + 1].id);
    }
  };

  const handleSubmit = async () => {
    const missing = getValidation();
    if (missing.length > 0) {
      toast.error(`Missing required fields: ${missing.join(', ')}`);
      return;
    }
    setLoading(true);
    try {
      // Create release with all metadata
      const releaseData = {
        title: form.title, release_type: form.product_type.toLowerCase() || 'single',
        genre: form.genre, release_date: form.release_date,
        description: '', explicit: false, language: form.metadata_language,
        label: form.label, upc: form.upc, catalog_number: form.catalog_number,
        production_year: form.production_year, copyright_line: form.copyright_line,
        production_line: form.production_line, is_compilation: form.is_compilation,
        title_version: form.title_version, main_artist: form.main_artist,
        territory: territory, distributed_platforms: distributedPlatforms,
        rights_confirmed: rightsConfirmed === 'yes',
      };
      const releaseRes = await axios.post(`${API}/releases`, releaseData, { headers });
      const newId = releaseRes.data.id;
      setReleaseId(newId);

      // Upload cover
      if (coverFile) {
        const coverFD = new FormData();
        coverFD.append('file', coverFile);
        await axios.post(`${API}/releases/${newId}/cover`, coverFD, { headers: { ...headers, 'Content-Type': 'multipart/form-data' } });
      }

      // Upload tracks
      const allTracks = volumes.flatMap(v => v.tracks);
      for (const track of allTracks) {
        if (!track.title) continue;
        const trackRes = await axios.post(`${API}/tracks`, {
          release_id: newId, title: track.title,
          track_number: track.track_number, explicit: track.explicit,
        }, { headers });
        if (track.audioFile) {
          const audioFD = new FormData();
          audioFD.append('file', track.audioFile);
          await axios.post(`${API}/tracks/${trackRes.data.id}/audio`, audioFD, { headers: { ...headers, 'Content-Type': 'multipart/form-data' } });
        }
      }

      // Submit for distribution
      await axios.post(`${API}/distributions/submit/${newId}`, distributedPlatforms.map(id => id), { headers });
      toast.success('Release submitted for review!');
      navigate(`/releases/${newId}`);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to submit release');
    }
    setLoading(false);
  };

  const allTracks = volumes.flatMap(v => v.tracks);
  const missing = getValidation();

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto" data-testid="release-wizard">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 rounded-xl bg-[#1a1a2e] flex items-center justify-center overflow-hidden">
            {coverPreview ? <img src={coverPreview} alt="" className="w-full h-full object-cover" /> : <VinylRecord className="w-6 h-6 text-gray-600" />}
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">{form.title || 'Untitled album'}</h1>
            <p className="text-xs text-gray-500">{form.main_artist || '—'}</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-1 bg-[#0d0d1a] rounded-xl p-1 border border-white/10 mb-8">
          {TABS.map((tab, i) => (
            <button key={tab.id} onClick={() => goToTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 px-3 py-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id ? 'bg-[#1a1a3e] text-white' : 'text-gray-500 hover:text-gray-300'
              }`} data-testid={`tab-${tab.id}`}>
              {tabComplete[tab.id] && <Check className="w-3.5 h-3.5 text-[#4CAF50]" weight="bold" />}
              {tab.label}
            </button>
          ))}
        </div>

        {/* ===== TAB 1: GENERAL INFORMATION ===== */}
        {activeTab === 'general' && (
          <div className="space-y-8" data-testid="tab-general-info">
            {/* Title Section */}
            <section className="bg-[#0d0d1a] border border-white/10 rounded-xl p-6 space-y-4">
              <h2 className="text-base font-bold text-white">Title</h2>
              <div>
                <FieldLabel label="Album Title" required />
                <InputField value={form.title} onChange={e => updateForm('title', e.target.value)} placeholder="Enter album title" testId="wiz-title" />
              </div>
              <div>
                <FieldLabel label="Title Version" tooltip="Add version info like 'Deluxe Edition', 'Remix', etc." />
                <InputField value={form.title_version} onChange={e => updateForm('title_version', e.target.value)} placeholder="e.g. Deluxe Edition" testId="wiz-title-version" />
              </div>
            </section>

            {/* Information Section */}
            <section className="bg-[#0d0d1a] border border-white/10 rounded-xl p-6 space-y-4">
              <h2 className="text-base font-bold text-white">Information</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <FieldLabel label="Label" required />
                  <InputField value={form.label} onChange={e => updateForm('label', e.target.value)} placeholder="Your label name" testId="wiz-label" />
                </div>
                <div>
                  <FieldLabel label="Main Artist" required />
                  <InputField value={form.main_artist} onChange={e => updateForm('main_artist', e.target.value)} placeholder="Primary artist name" testId="wiz-main-artist" />
                </div>
              </div>
              <div>
                <FieldLabel label="UPC" required />
                <div className="flex gap-2">
                  <InputField value={form.upc} onChange={e => updateForm('upc', e.target.value)} placeholder="Universal Product Code" testId="wiz-upc" />
                  <button onClick={generateUPC} className="px-4 py-2 text-xs font-medium text-[#7C4DFF] border border-[#7C4DFF]/30 rounded-lg hover:bg-[#7C4DFF]/10 transition-colors whitespace-nowrap" data-testid="generate-upc-btn">
                    Generate UPC
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <FieldLabel label="Product Type" required />
                  <SelectField value={form.product_type} onChange={e => updateForm('product_type', e.target.value)} options={PRODUCT_TYPES} placeholder="Select type..." testId="wiz-product-type" />
                </div>
                <div>
                  <FieldLabel label="Main Genre" required />
                  <SelectField value={form.genre} onChange={e => updateForm('genre', e.target.value)} options={GENRES} testId="wiz-genre" />
                </div>
              </div>
              <label className="flex items-center gap-3 cursor-pointer py-1">
                <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${form.is_compilation ? 'bg-[#7C4DFF] border-[#7C4DFF]' : 'border-gray-600'}`}
                  onClick={() => updateForm('is_compilation', !form.is_compilation)}>
                  {form.is_compilation && <Check className="w-3 h-3 text-white" weight="bold" />}
                </div>
                <span className="text-sm text-gray-300">This album is a compilation</span>
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <FieldLabel label="Metadata Language" required tooltip="The language of the album metadata (title, description, etc.)" />
                  <SelectField value={form.metadata_language} onChange={e => updateForm('metadata_language', e.target.value)}
                    options={LANGUAGES.map(l => ({ value: l.code, label: l.name }))} testId="wiz-language" />
                </div>
                <div>
                  <FieldLabel label="Release Date" required />
                  <InputField type="date" value={form.release_date} onChange={e => updateForm('release_date', e.target.value)} testId="wiz-date" />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <FieldLabel label="Catalog Number" tooltip="Optional identifier for your internal catalog" />
                  <InputField value={form.catalog_number} onChange={e => updateForm('catalog_number', e.target.value)} placeholder="e.g. CAT-001" testId="wiz-catalog" />
                </div>
                <div>
                  <FieldLabel label="Production Year" />
                  <InputField value={form.production_year} onChange={e => updateForm('production_year', e.target.value)} placeholder="2026" testId="wiz-prod-year" />
                </div>
              </div>
              <div>
                <FieldLabel label="© Copyright Line" required tooltip="The copyright holder of the sound recording, e.g. '2026 Your Label'" />
                <InputField value={form.copyright_line} onChange={e => updateForm('copyright_line', e.target.value)} placeholder="2026 Your Label Name" testId="wiz-copyright" />
              </div>
              <div>
                <FieldLabel label="℗ Production Line" required tooltip="The producer of the sound recording, e.g. '2026 Your Label'" />
                <InputField value={form.production_line} onChange={e => updateForm('production_line', e.target.value)} placeholder="2026 Your Label Name" testId="wiz-production" />
              </div>
            </section>

            {/* Cover Art & Booklet */}
            <section className="bg-[#0d0d1a] border border-white/10 rounded-xl p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <FieldLabel label="Cover Art" required tooltip="Square image, min 3000x3000px, JPG/PNG, max 10MB" />
                  <label className="cursor-pointer block mt-2">
                    {coverPreview ? (
                      <div className="relative group rounded-xl overflow-hidden aspect-square max-w-[240px]">
                        <img src={coverPreview} alt="Cover" className="w-full h-full object-cover" />
                        <div className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <span className="text-white text-sm font-bold">Change</span>
                        </div>
                      </div>
                    ) : (
                      <div className="aspect-square max-w-[240px] border-2 border-dashed border-gray-700 rounded-xl flex flex-col items-center justify-center hover:border-[#7C4DFF]/50 transition-colors bg-[#0a0a14]">
                        <Image className="w-10 h-10 text-gray-600 mb-2" />
                        <span className="text-xs text-gray-500">Upload cover art</span>
                      </div>
                    )}
                    <input type="file" accept="image/*" className="hidden" onChange={handleCoverSelect} data-testid="wiz-cover-input" />
                  </label>
                </div>
                <div>
                  <FieldLabel label="Booklet" tooltip="Optional booklet/liner notes PDF or image" />
                  <label className="cursor-pointer block mt-2">
                    <div className="aspect-square max-w-[240px] border-2 border-dashed border-gray-700 rounded-xl flex flex-col items-center justify-center hover:border-[#7C4DFF]/50 transition-colors bg-[#0a0a14]">
                      {bookletName ? (
                        <><FileAudio className="w-10 h-10 text-[#7C4DFF] mb-2" /><span className="text-xs text-gray-400 px-4 text-center truncate max-w-full">{bookletName}</span></>
                      ) : (
                        <><Image className="w-10 h-10 text-gray-600 mb-2" /><span className="text-xs text-gray-500">Upload booklet</span></>
                      )}
                    </div>
                    <input type="file" accept="image/*,.pdf" className="hidden" onChange={handleBookletSelect} data-testid="wiz-booklet-input" />
                  </label>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* ===== TAB 2: TRACKS & ASSETS ===== */}
        {activeTab === 'tracks' && (
          <div className="space-y-6" data-testid="tab-tracks">
            {volumes.map((vol, volIdx) => (
              <div key={vol.id}>
                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center gap-2">
                    {volumes.map((v, vi) => (
                      <button key={v.id} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${vi === volIdx ? 'bg-white/10 text-white' : 'text-gray-600 hover:text-gray-400'}`}>
                        Volume {v.id}
                      </button>
                    ))}
                    <button onClick={addVolume} className="p-1.5 rounded-lg text-gray-600 hover:text-white hover:bg-white/5 transition-all" data-testid="add-volume-btn">
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="bg-[#0d0d1a] border border-white/10 rounded-xl p-6">
                  <div className="flex flex-col sm:flex-row gap-8 items-start justify-center mb-8">
                    {/* Add New Track */}
                    <div className="text-center">
                      <div className="w-32 h-32 bg-[#1a1a2e] rounded-2xl flex items-center justify-center mx-auto mb-3 relative">
                        <MusicNote className="w-12 h-12 text-gray-500" />
                        <div className="absolute -bottom-1 -right-1 w-7 h-7 bg-[#7C4DFF] rounded-full flex items-center justify-center">
                          <Plus className="w-4 h-4 text-white" weight="bold" />
                        </div>
                      </div>
                      <p className="text-sm font-medium text-gray-300">Add New Track</p>
                      <div className="flex items-center gap-2 mt-2 justify-center">
                        <input type="number" min="1" value={vol.tracks.length + 1} readOnly
                          className="w-12 bg-[#0a0a14] border border-white/10 rounded px-2 py-1 text-white text-sm text-center" />
                        <button onClick={() => addTrack(volIdx)} className="px-3 py-1 bg-[#1a1a2e] text-gray-300 text-sm rounded hover:bg-white/10 transition-colors" data-testid="add-track-btn">
                          Add
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Track List */}
                  <div className="space-y-4">
                    {vol.tracks.map((track, trackIdx) => (
                      <div key={trackIdx} className="bg-[#0a0a14] border border-white/5 rounded-xl p-5 space-y-5" data-testid={`track-${trackIdx}`}>
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-gray-500 tracking-wider">TRACK {track.track_number}</span>
                          {vol.tracks.length > 1 && (
                            <button onClick={() => removeTrack(volIdx, trackIdx)} className="text-gray-600 hover:text-red-400 p-1 transition-colors"><Trash className="w-4 h-4" /></button>
                          )}
                        </div>

                        {/* === TITLE === */}
                        <div className="space-y-3">
                          <h4 className="text-xs font-bold text-[#7C4DFF] uppercase tracking-wider">Title</h4>
                          <InputField value={track.title} onChange={e => updateTrack(volIdx, trackIdx, 'title', e.target.value)}
                            placeholder="Track title *" testId={`track-title-${trackIdx}`} />
                          <InputField value={track.title_version || ''} onChange={e => updateTrack(volIdx, trackIdx, 'title_version', e.target.value)}
                            placeholder="Title Version (e.g. Remix, Acoustic)" testId={`track-title-version-${trackIdx}`} />
                        </div>

                        {/* === AUDIO FILE === */}
                        <div className="flex items-center gap-3">
                          <label className="flex-1 cursor-pointer">
                            <div className={`flex items-center gap-2 px-4 py-2.5 border rounded-lg transition-colors ${track.audioName ? 'border-[#4CAF50]/30 bg-[#4CAF50]/5' : 'border-white/10 hover:border-[#7C4DFF]/30'}`}>
                              <Upload className="w-4 h-4 text-gray-500 flex-shrink-0" />
                              <span className="text-sm text-gray-400 truncate">{track.audioName || 'Upload audio (WAV, MP3, FLAC)'}</span>
                            </div>
                            <input type="file" accept="audio/*" className="hidden" onChange={e => handleAudioSelect(volIdx, trackIdx, e.target.files?.[0])} data-testid={`track-audio-${trackIdx}`} />
                          </label>
                          <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-400 px-2">
                            <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${track.explicit ? 'bg-[#E040FB] border-[#E040FB]' : 'border-gray-600'}`}
                              onClick={() => updateTrack(volIdx, trackIdx, 'explicit', !track.explicit)}>
                              {track.explicit && <Check className="w-2.5 h-2.5 text-white" weight="bold" />}
                            </div>
                            Explicit
                          </label>
                        </div>

                        {/* === INFORMATION === */}
                        <div className="space-y-3">
                          <h4 className="text-xs font-bold text-[#E040FB] uppercase tracking-wider">Information</h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div className="flex gap-2">
                              <div className="flex-1">
                                <InputField value={track.isrc} onChange={e => updateTrack(volIdx, trackIdx, 'isrc', e.target.value)}
                                  placeholder="Audio ISRC *" testId={`track-isrc-${trackIdx}`} />
                              </div>
                              <button type="button" onClick={() => {
                                const isrc = 'US' + 'KAL' + new Date().getFullYear().toString().slice(-2) + Math.floor(10000 + Math.random() * 90000);
                                updateTrack(volIdx, trackIdx, 'isrc', isrc);
                              }} className="px-3 py-2 text-[10px] font-bold text-[#7C4DFF] border border-[#7C4DFF]/30 rounded-lg hover:bg-[#7C4DFF]/10 transition-colors whitespace-nowrap"
                                data-testid={`generate-isrc-${trackIdx}`}>
                                Generate ISRC
                              </button>
                            </div>
                            <div className="flex gap-2">
                              <div className="flex-1">
                                <InputField value={track.dolby_atmos_isrc || ''} onChange={e => updateTrack(volIdx, trackIdx, 'dolby_atmos_isrc', e.target.value)}
                                  placeholder="Dolby Atmos ISRC" testId={`track-dolby-isrc-${trackIdx}`} />
                              </div>
                              <button type="button" onClick={() => {
                                const isrc = 'US' + 'KAL' + new Date().getFullYear().toString().slice(-2) + Math.floor(10000 + Math.random() * 90000);
                                updateTrack(volIdx, trackIdx, 'dolby_atmos_isrc', isrc);
                              }} className="px-3 py-2 text-[10px] font-bold text-[#7C4DFF] border border-[#7C4DFF]/30 rounded-lg hover:bg-[#7C4DFF]/10 transition-colors whitespace-nowrap"
                                data-testid={`generate-dolby-isrc-${trackIdx}`}>
                                Generate ISRC
                              </button>
                            </div>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <InputField value={track.iswc || ''} onChange={e => updateTrack(volIdx, trackIdx, 'iswc', e.target.value)}
                              placeholder="ISWC" testId={`track-iswc-${trackIdx}`} />
                            <div>
                              <select value={track.audio_language || 'English'} onChange={e => updateTrack(volIdx, trackIdx, 'audio_language', e.target.value)}
                                className="w-full bg-[#0a0a14] border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#7C4DFF]"
                                data-testid={`track-language-${trackIdx}`}>
                                {['English','Spanish','French','Portuguese','German','Italian','Japanese','Korean','Chinese','Hindi','Arabic','Swahili','Yoruba','Igbo','Zulu','Dutch','Swedish','Russian','Turkish','Polish','Instrumental'].map(lang => (
                                  <option key={lang} value={lang}>{lang}</option>
                                ))}
                              </select>
                            </div>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <InputField value={track.production || ''} onChange={e => updateTrack(volIdx, trackIdx, 'production', e.target.value)}
                              placeholder="Production" testId={`track-production-${trackIdx}`} />
                            <InputField value={track.publisher || ''} onChange={e => updateTrack(volIdx, trackIdx, 'publisher', e.target.value)}
                              placeholder="Publisher" testId={`track-publisher-${trackIdx}`} />
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-xs text-gray-500 mb-1">Preview Start Time *</label>
                              <input type="text" value={track.preview_start || '00:30'} onChange={e => updateTrack(volIdx, trackIdx, 'preview_start', e.target.value)}
                                placeholder="00:30" className="w-full bg-[#0a0a14] border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#7C4DFF]"
                                data-testid={`track-preview-start-${trackIdx}`} />
                            </div>
                            <div>
                              <label className="block text-xs text-gray-500 mb-1">Preview End Time</label>
                              <input type="text" value={track.preview_end || '00:00'} onChange={e => updateTrack(volIdx, trackIdx, 'preview_end', e.target.value)}
                                placeholder="00:00" className="w-full bg-[#0a0a14] border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#7C4DFF]"
                                data-testid={`track-preview-end-${trackIdx}`} />
                            </div>
                          </div>
                        </div>

                        {/* === ARTISTS === */}
                        <div className="space-y-3">
                          <h4 className="text-xs font-bold text-[#FFD700] uppercase tracking-wider">Artists *</h4>
                          <p className="text-[11px] text-gray-500">Enter the name of the main artists</p>
                          {(track.artists || []).map((art, artIdx) => (
                            <div key={artIdx} className="flex items-center gap-2">
                              <select value={art.role} onChange={e => {
                                const updated = [...(track.artists || [])];
                                updated[artIdx] = { ...updated[artIdx], role: e.target.value };
                                updateTrack(volIdx, trackIdx, 'artists', updated);
                              }} className="bg-[#0a0a14] border border-white/10 rounded-lg px-3 py-2 text-xs text-white w-32"
                                data-testid={`track-artist-role-${trackIdx}-${artIdx}`}>
                                <option value="Main Artist">Main Artist</option>
                                <option value="Featured">Featured</option>
                                <option value="Remixer">Remixer</option>
                              </select>
                              <input value={art.name} onChange={e => {
                                const updated = [...(track.artists || [])];
                                updated[artIdx] = { ...updated[artIdx], name: e.target.value };
                                updateTrack(volIdx, trackIdx, 'artists', updated);
                              }} placeholder="Name"
                                className="flex-1 bg-[#0a0a14] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#7C4DFF]"
                                data-testid={`track-artist-name-${trackIdx}-${artIdx}`} />
                              <button type="button" onClick={() => {
                                const updated = [...(track.artists || []), { role: 'Featured', name: '' }];
                                updateTrack(volIdx, trackIdx, 'artists', updated);
                              }} className="p-2 text-[#7C4DFF] hover:bg-[#7C4DFF]/10 rounded-lg"><Plus className="w-4 h-4" /></button>
                              {(track.artists || []).length > 1 && (
                                <button type="button" onClick={() => {
                                  const updated = (track.artists || []).filter((_, i) => i !== artIdx);
                                  updateTrack(volIdx, trackIdx, 'artists', updated);
                                }} className="p-2 text-red-400 hover:bg-red-400/10 rounded-lg"><Trash className="w-4 h-4" /></button>
                              )}
                            </div>
                          ))}
                        </div>

                        {/* === MAIN CONTRIBUTORS === */}
                        <div className="space-y-3">
                          <h4 className="text-xs font-bold text-[#00BCD4] uppercase tracking-wider">Main Contributors *</h4>
                          <p className="text-[11px] text-gray-500">Enter the name of the main contributors</p>
                          {(track.main_contributors || []).map((mc, mcIdx) => (
                            <div key={mcIdx} className="flex items-center gap-2">
                              <select value={mc.role} onChange={e => {
                                const updated = [...(track.main_contributors || [])];
                                updated[mcIdx] = { ...updated[mcIdx], role: e.target.value };
                                updateTrack(volIdx, trackIdx, 'main_contributors', updated);
                              }} className="bg-[#0a0a14] border border-white/10 rounded-lg px-3 py-2 text-xs text-white w-32"
                                data-testid={`track-mc-role-${trackIdx}-${mcIdx}`}>
                                <option value="Composer">Composer</option>
                                <option value="Lyricist">Lyricist</option>
                                <option value="Arranger">Arranger</option>
                              </select>
                              <input value={mc.name} onChange={e => {
                                const updated = [...(track.main_contributors || [])];
                                updated[mcIdx] = { ...updated[mcIdx], name: e.target.value };
                                updateTrack(volIdx, trackIdx, 'main_contributors', updated);
                              }} placeholder="Name"
                                className="flex-1 bg-[#0a0a14] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#7C4DFF]"
                                data-testid={`track-mc-name-${trackIdx}-${mcIdx}`} />
                              <button type="button" onClick={() => {
                                const updated = [...(track.main_contributors || []), { role: 'Composer', name: '' }];
                                updateTrack(volIdx, trackIdx, 'main_contributors', updated);
                              }} className="p-2 text-[#7C4DFF] hover:bg-[#7C4DFF]/10 rounded-lg"><Plus className="w-4 h-4" /></button>
                              {(track.main_contributors || []).length > 1 && (
                                <button type="button" onClick={() => {
                                  const updated = (track.main_contributors || []).filter((_, i) => i !== mcIdx);
                                  updateTrack(volIdx, trackIdx, 'main_contributors', updated);
                                }} className="p-2 text-red-400 hover:bg-red-400/10 rounded-lg"><Trash className="w-4 h-4" /></button>
                              )}
                            </div>
                          ))}
                        </div>

                        {/* === CONTRIBUTORS === */}
                        <div className="space-y-3">
                          <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                            Contributors <Info className="w-3 h-3 text-gray-500" />
                          </h4>
                          <p className="text-[11px] text-gray-500">Add contributor roles and fill in their names</p>
                          {(track.contributors || []).map((ct, ctIdx) => (
                            <div key={ctIdx} className="flex items-center gap-2">
                              <select value={ct.role} onChange={e => {
                                const updated = [...(track.contributors || [])];
                                updated[ctIdx] = { ...updated[ctIdx], role: e.target.value };
                                updateTrack(volIdx, trackIdx, 'contributors', updated);
                              }} className="bg-[#0a0a14] border border-white/10 rounded-lg px-3 py-2 text-xs text-white w-32">
                                <option value="Producer">Producer</option>
                                <option value="Mixer">Mixer</option>
                                <option value="Mastering Engineer">Mastering</option>
                                <option value="Recording Engineer">Recording</option>
                                <option value="Performer">Performer</option>
                              </select>
                              <input value={ct.name} onChange={e => {
                                const updated = [...(track.contributors || [])];
                                updated[ctIdx] = { ...updated[ctIdx], name: e.target.value };
                                updateTrack(volIdx, trackIdx, 'contributors', updated);
                              }} placeholder="Name"
                                className="flex-1 bg-[#0a0a14] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#7C4DFF]" />
                              <button type="button" onClick={() => {
                                const updated = (track.contributors || []).filter((_, i) => i !== ctIdx);
                                updateTrack(volIdx, trackIdx, 'contributors', updated);
                              }} className="p-2 text-red-400 hover:bg-red-400/10 rounded-lg"><Trash className="w-4 h-4" /></button>
                            </div>
                          ))}
                          <button type="button" onClick={() => {
                            const updated = [...(track.contributors || []), { role: 'Producer', name: '' }];
                            updateTrack(volIdx, trackIdx, 'contributors', updated);
                          }} className="flex items-center gap-2 text-[#7C4DFF] text-xs font-semibold hover:text-[#E040FB] transition-colors"
                            data-testid={`add-contributor-${trackIdx}`}>
                            <Plus className="w-4 h-4" /> Add New Contributor
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ===== TAB 3: TERRITORY & PLATFORM RIGHTS ===== */}
        {activeTab === 'territory' && (
          <div className="space-y-6" data-testid="tab-territory">
            <section className="bg-[#0d0d1a] border border-white/10 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-6">
                <h2 className="text-base font-bold text-white">Distributed Territories and Platforms</h2>
                <Info className="w-4 h-4 text-gray-500" />
              </div>

              {/* Territories / Platforms tabs */}
              <div className="flex gap-6 mb-6 border-b border-white/10">
                <button className="flex items-center gap-2 pb-3 text-sm font-medium text-gray-400 border-b-2 border-transparent">
                  <Globe className="w-4 h-4" /> Territories
                </button>
                <button className="flex items-center gap-2 pb-3 text-sm font-medium text-white border-b-2 border-white">
                  <Disc className="w-4 h-4" /> Platforms
                </button>
              </div>

              <div className="flex gap-8">
                <div className="w-28 flex-shrink-0">
                  <p className="text-sm text-gray-300 font-medium">Worldwide</p>
                </div>
                <div className="flex-1 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                  {DISTRIBUTED_PLATFORMS.map(p => (
                    <button key={p.id} onClick={() => {
                      setDistributedPlatforms(prev => prev.includes(p.id) ? prev.filter(x => x !== p.id) : [...prev, p.id]);
                    }} className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                      distributedPlatforms.includes(p.id) ? 'bg-white/5 border border-white/10 text-white' : 'bg-transparent border border-transparent text-gray-600 hover:text-gray-400'
                    }`} data-testid={`platform-${p.id}`}>
                      <div className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${p.color}30` }}>
                        <MusicNote className="w-3 h-3" style={{ color: p.color }} />
                      </div>
                      <span className="truncate">{p.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </section>

            {/* Not Distributed */}
            <section className="bg-[#0d0d1a] border border-white/10 rounded-xl p-6">
              <h2 className="text-base font-bold text-white mb-4">Not Distributed</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                {NOT_DISTRIBUTED_PLATFORMS.map(p => (
                  <div key={p.id} className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-xs text-gray-500">
                    <div className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${p.color}15` }}>
                      <MusicNote className="w-3 h-3" style={{ color: p.color }} />
                    </div>
                    <span className="truncate">{p.name}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Confirm Rights */}
            <section className="bg-[#0d0d1a] border border-white/10 rounded-xl p-6">
              <h2 className="text-base font-bold text-white mb-2">Confirm Your Album Rights</h2>
              <p className="text-sm text-gray-400 mb-4">Do the above rights apply to your album?</p>
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2 cursor-pointer" data-testid="rights-yes">
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${rightsConfirmed === 'yes' ? 'border-[#7C4DFF]' : 'border-gray-600'}`}>
                    {rightsConfirmed === 'yes' && <div className="w-2.5 h-2.5 rounded-full bg-[#7C4DFF]" />}
                  </div>
                  <span className="text-sm text-gray-300">Yes, they do.</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer" onClick={() => setRightsConfirmed('no')} data-testid="rights-no">
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${rightsConfirmed === 'no' ? 'border-[#7C4DFF]' : 'border-gray-600'}`}>
                    {rightsConfirmed === 'no' && <div className="w-2.5 h-2.5 rounded-full bg-[#7C4DFF]" />}
                  </div>
                  <span className="text-sm text-gray-300">No, I'd like to request a change.</span>
                </label>
              </div>
            </section>
          </div>
        )}

        {/* ===== TAB 4: SUMMARY ===== */}
        {activeTab === 'summary' && (
          <div className="space-y-4" data-testid="tab-summary">
            {/* General Info Summary */}
            <SummarySection title="General Information" subtitle={`${form.title || 'Untitled album'} —`}
              hasMissing={!form.title || !form.product_type || !form.upc || !form.copyright_line || !form.production_line || !form.metadata_language || !form.genre || !form.main_artist || (!coverFile && !coverPreview)}
              onEdit={() => setActiveTab('general')}>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-2 text-sm">
                <SummaryField label="Label" value={form.label} />
                <SummaryField label="Production Year" value={form.production_year} />
                <SummaryField label="Main Genre" value={form.genre} required />
                <SummaryField label="© Copyright Line" value={form.copyright_line} required />
                <SummaryField label="UPC" value={form.upc} required />
                <SummaryField label="℗ Production Line" value={form.production_line} required />
                <SummaryField label="Product Type" value={form.product_type} required />
                <SummaryField label="Catalog Number" value={form.catalog_number} />
                <SummaryField label="Release Date" value={form.release_date} />
                <SummaryField label="Metadata Language" value={LANGUAGES.find(l => l.code === form.metadata_language)?.name || form.metadata_language} required />
              </div>
              <div className="mt-4 space-y-2">
                <p className="text-xs font-bold text-gray-500">Artwork</p>
                <div className="flex gap-4">
                  <SummaryField label="Cover Art" value={coverFile ? coverFile.name : null} required />
                  <SummaryField label="Booklet" value={bookletName || null} />
                </div>
                <p className="text-xs font-bold text-gray-500 mt-3">Artists</p>
                <SummaryField label="Main Artist" value={form.main_artist} required />
              </div>
            </SummarySection>

            {/* Tracks Summary */}
            <SummarySection title="Tracks & Assets" subtitle={`Volume 1 — ${allTracks.filter(t => t.title).length} tracks`}
              hasMissing={!allTracks.some(t => t.title)}
              onEdit={() => setActiveTab('tracks')}>
              {allTracks.filter(t => t.title).length === 0 ? (
                <p className="text-sm text-[#E040FB]">No tracks added</p>
              ) : (
                <div className="space-y-1">
                  {allTracks.filter(t => t.title).map((t, i) => (
                    <p key={i} className="text-sm text-gray-300">{t.track_number}. {t.title} {t.audioName && <span className="text-gray-600">({t.audioName})</span>}</p>
                  ))}
                </div>
              )}
            </SummarySection>

            {/* Territory Summary */}
            <SummarySection title="Territory and Platform Rights" subtitle={rightsConfirmed === 'yes' ? '' : 'Change requested'}
              hasMissing={false}
              onEdit={() => setActiveTab('territory')}>
              <p className="text-sm text-gray-300">{distributedPlatforms.length} platforms selected — {territory === 'worldwide' ? 'Worldwide' : 'Selected territories'}</p>
            </SummarySection>

            {/* Submit */}
            <div className="text-center pt-4 pb-8">
              <button onClick={handleSubmit} disabled={loading || missing.length > 0}
                className={`px-8 py-3 rounded-lg text-sm font-bold transition-all ${missing.length > 0 ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-white text-black hover:bg-gray-200'}`}
                data-testid="wiz-submit">
                {loading ? <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin mx-auto" /> : 'Submit'}
              </button>
              <p className="text-sm text-gray-500 mt-3">Your album will be reviewed by our teams.</p>
            </div>
          </div>
        )}

        {/* Navigation */}
        {activeTab !== 'summary' && (
          <div className="flex items-center justify-between mt-8 gap-3">
            <button onClick={() => {
              const idx = TABS.findIndex(t => t.id === activeTab);
              if (idx === 0) navigate('/releases');
              else setActiveTab(TABS[idx - 1].id);
            }} className="flex items-center gap-2 px-5 py-3 rounded-lg border border-white/10 text-gray-400 hover:text-white hover:bg-white/5 text-sm font-medium transition-all" data-testid="wiz-back">
              <ArrowLeft className="w-4 h-4" /> Previous Step
            </button>
            <button onClick={saveAndNext} disabled={loading}
              className="flex items-center gap-2 px-6 py-3 rounded-lg bg-white text-black text-sm font-bold hover:bg-gray-200 transition-all" data-testid="wiz-next">
              {loading ? <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" /> : <>Save & Go To Next Step <ArrowRight className="w-4 h-4" /></>}
            </button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

function SummarySection({ title, subtitle, hasMissing, onEdit, children }) {
  const [expanded, setExpanded] = useState(true);
  return (
    <div className="bg-[#0d0d1a] border border-white/10 rounded-xl overflow-hidden">
      <div className="flex items-center justify-between p-5 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${hasMissing ? 'bg-[#E040FB]/20' : 'bg-[#4CAF50]/20'}`}>
            {hasMissing ? <Warning className="w-4 h-4 text-[#E040FB]" /> : <Check className="w-4 h-4 text-[#4CAF50]" weight="bold" />}
          </div>
          <div>
            <p className="text-sm font-bold text-white">{title}</p>
            <p className="text-xs text-gray-500">{subtitle}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {hasMissing && <span className="text-xs font-bold text-[#E040FB]">missing item</span>}
          <button onClick={(e) => { e.stopPropagation(); onEdit(); }} className="px-3 py-1 text-xs border border-white/10 rounded-md text-gray-400 hover:text-white hover:bg-white/5 transition-all" data-testid={`edit-${title.toLowerCase().replace(/\s+/g, '-')}`}>
            Edit
          </button>
          {expanded ? <CaretUp className="w-4 h-4 text-gray-500" /> : <CaretDown className="w-4 h-4 text-gray-500" />}
        </div>
      </div>
      {expanded && <div className="px-5 pb-5 border-t border-white/5 pt-4">{children}</div>}
    </div>
  );
}

function SummaryField({ label, value, required }) {
  const isMissing = required && !value;
  return (
    <div className="flex items-start gap-1">
      <span className="text-gray-500 text-xs">{label}:</span>
      {isMissing ? (
        <span className="text-xs font-bold text-[#E040FB] bg-[#E040FB]/10 px-1.5 py-0.5 rounded">missing item</span>
      ) : (
        <span className="text-xs text-gray-300">{value || '—'}</span>
      )}
    </div>
  );
}
