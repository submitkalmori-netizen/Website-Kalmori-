import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { API, useAuth } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import PublicLayout from '../components/PublicLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Clock, SpotifyLogo, AppleLogo, YoutubeLogo, MusicNotes, Users, Plus, Trash, Link as LinkIcon, Check, PaperPlaneTilt, CalendarBlank, ShareNetwork, Copy } from '@phosphor-icons/react';

// ===== Pre-Save Landing Page (Public) =====
export function PreSaveLandingPage() {
  const { campaignId } = useParams();
  const [campaign, setCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { fetchCampaign(); }, [campaignId]);

  const fetchCampaign = async () => {
    try {
      const res = await axios.get(`${API}/presave/${campaignId}`);
      setCampaign(res.data);
    } catch { setCampaign(null); }
    finally { setLoading(false); }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (!email) return toast.error('Email is required');
    setSubmitting(true);
    try {
      await axios.post(`${API}/presave/${campaignId}/subscribe`, { email, name });
      setSubscribed(true);
      toast.success("You're on the list!");
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to subscribe');
    } finally { setSubmitting(false); }
  };

  if (loading) return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (!campaign) return (
    <div className="min-h-screen bg-black flex items-center justify-center text-white">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-2">Campaign not found</h1>
        <Link to="/" className="text-[#7C4DFF] hover:underline">Go home</Link>
      </div>
    </div>
  );

  const releaseDate = campaign.release_date ? new Date(campaign.release_date) : null;
  const now = new Date();
  const daysLeft = releaseDate ? Math.max(0, Math.ceil((releaseDate - now) / (1000 * 60 * 60 * 24))) : 0;

  return (
    <div className="min-h-screen bg-black text-white" data-testid="presave-landing">
      <div className="max-w-lg mx-auto px-4 py-12">
        {/* Artist */}
        <p className="text-center text-sm text-[#7C4DFF] font-bold tracking-[3px] mb-6">KALMORI PRE-SAVE</p>

        {/* Cover */}
        <div className="relative mx-auto w-64 h-64 rounded-3xl overflow-hidden bg-[#1a1a1a] mb-8 shadow-2xl shadow-[#7C4DFF]/10">
          {campaign.cover_url ? (
            <img src={campaign.cover_url} alt="" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <MusicNotes className="w-20 h-20 text-gray-600" />
            </div>
          )}
        </div>

        {/* Title */}
        <h1 className="text-3xl font-extrabold text-center mb-2">{campaign.title}</h1>
        <p className="text-center text-gray-400 mb-2">{campaign.artist_name}</p>
        {campaign.description && <p className="text-center text-sm text-gray-500 mb-6">{campaign.description}</p>}

        {/* Countdown */}
        <div className="flex items-center justify-center gap-6 mb-8">
          <div className="text-center">
            <p className="text-4xl font-bold font-mono text-[#E040FB]">{daysLeft}</p>
            <p className="text-xs text-gray-500 mt-1">days</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-400">{releaseDate ? releaseDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) : 'TBA'}</p>
            <p className="text-xs text-gray-500 mt-1">release date</p>
          </div>
        </div>

        {/* Platform Links */}
        <div className="flex justify-center gap-4 mb-8">
          {campaign.spotify_url && (
            <a href={campaign.spotify_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-5 py-3 rounded-full bg-[#1DB954]/15 text-[#1DB954] text-sm font-bold hover:bg-[#1DB954]/25 transition-all" data-testid="presave-spotify">
              <SpotifyLogo className="w-5 h-5" weight="fill" /> Spotify
            </a>
          )}
          {campaign.apple_music_url && (
            <a href={campaign.apple_music_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-5 py-3 rounded-full bg-[#FC3C44]/15 text-[#FC3C44] text-sm font-bold hover:bg-[#FC3C44]/25 transition-all" data-testid="presave-apple">
              <AppleLogo className="w-5 h-5" weight="fill" /> Apple Music
            </a>
          )}
          {campaign.youtube_url && (
            <a href={campaign.youtube_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-5 py-3 rounded-full bg-[#FF0000]/15 text-[#FF0000] text-sm font-bold hover:bg-[#FF0000]/25 transition-all" data-testid="presave-youtube">
              <YoutubeLogo className="w-5 h-5" weight="fill" /> YouTube
            </a>
          )}
        </div>

        {/* Subscribe Form */}
        {subscribed ? (
          <div className="text-center py-8 bg-[#0d0d1a] rounded-2xl border border-[#4CAF50]/20" data-testid="presave-subscribed">
            <div className="w-16 h-16 rounded-full bg-[#4CAF50]/20 flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-[#4CAF50]" weight="bold" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">You're on the list!</h3>
            <p className="text-sm text-gray-400">We'll notify you when it drops.</p>
          </div>
        ) : (
          <form onSubmit={handleSubscribe} className="bg-[#0d0d1a] rounded-2xl border border-white/10 p-6 space-y-4" data-testid="presave-form">
            <h3 className="text-lg font-bold text-center">Get notified on release day</h3>
            <Input value={name} onChange={e => setName(e.target.value)} placeholder="Your name (optional)" className="bg-[#0a0a0a] border-white/10" data-testid="presave-name" />
            <Input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Your email *" required className="bg-[#0a0a0a] border-white/10" data-testid="presave-email" />
            <Button type="submit" disabled={submitting} className="w-full btn-animated rounded-full text-sm font-bold gap-2" data-testid="presave-subscribe-btn">
              {submitting ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <PaperPlaneTilt className="w-4 h-4" />}
              Pre-Save Now
            </Button>
          </form>
        )}

        {/* Footer */}
        <p className="text-center text-xs text-gray-600 mt-8">Powered by Kalmori</p>
      </div>
    </div>
  );
}


// ===== Pre-Save Manager (Dashboard) =====
export default function PreSaveManagerPage() {
  const { user } = useAuth();
  const [campaigns, setCampaigns] = useState([]);
  const [releases, setReleases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    release_id: '', title: '', description: '', release_date: '',
    spotify_url: '', apple_music_url: '', youtube_url: '', custom_message: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      const [campRes, relRes] = await Promise.all([
        axios.get(`${API}/presave/campaigns`, { withCredentials: true }),
        axios.get(`${API}/releases`, { withCredentials: true }).catch(() => ({ data: [] })),
      ]);
      setCampaigns(campRes.data.campaigns || []);
      const relData = Array.isArray(relRes.data) ? relRes.data : relRes.data.releases || [];
      setReleases(relData);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const createCampaign = async (e) => {
    e.preventDefault();
    if (!formData.release_id || !formData.title || !formData.release_date) {
      return toast.error('Release, title, and release date are required');
    }
    setSubmitting(true);
    try {
      await axios.post(`${API}/presave/campaigns`, formData, { withCredentials: true });
      toast.success('Pre-save campaign created!');
      setShowForm(false);
      setFormData({ release_id: '', title: '', description: '', release_date: '', spotify_url: '', apple_music_url: '', youtube_url: '', custom_message: '' });
      fetchAll();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create campaign');
    } finally { setSubmitting(false); }
  };

  const deleteCampaign = async (id) => {
    if (!window.confirm('Delete this campaign?')) return;
    try {
      await axios.delete(`${API}/presave/campaigns/${id}`, { withCredentials: true });
      toast.success('Campaign deleted');
      fetchAll();
    } catch (err) { toast.error('Failed to delete'); }
  };

  const copyLink = (id) => {
    navigator.clipboard.writeText(`${window.location.origin}/presave/${id}`);
    toast.success('Pre-save link copied!');
  };

  if (loading) return (
    <DashboardLayout>
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" />
      </div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="presave-manager-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Pre-Save Campaigns</h1>
            <p className="text-gray-400 mt-1">Create pre-save links for upcoming releases</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)} className="btn-animated rounded-full gap-2" data-testid="create-campaign-btn">
            <Plus className="w-4 h-4" /> New Campaign
          </Button>
        </div>

        {/* Create Form */}
        {showForm && (
          <form onSubmit={createCampaign} className="bg-[#111] border border-[#7C4DFF]/30 rounded-2xl p-6 space-y-4" data-testid="campaign-form">
            <h2 className="text-lg font-bold">Create Pre-Save Campaign</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label>Release *</Label>
                <select value={formData.release_id} onChange={e => setFormData(p => ({ ...p, release_id: e.target.value }))}
                  className="w-full mt-1 bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-white text-sm" data-testid="campaign-release">
                  <option value="">Select release...</option>
                  {releases.map(r => <option key={r.id} value={r.id}>{r.title}</option>)}
                </select>
              </div>
              <div>
                <Label>Campaign Title *</Label>
                <Input value={formData.title} onChange={e => setFormData(p => ({ ...p, title: e.target.value }))}
                  placeholder="e.g. My New Album - Pre-Save" className="mt-1 bg-[#0a0a0a] border-white/10" data-testid="campaign-title" />
              </div>
              <div>
                <Label>Release Date *</Label>
                <Input type="date" value={formData.release_date} onChange={e => setFormData(p => ({ ...p, release_date: e.target.value }))}
                  className="mt-1 bg-[#0a0a0a] border-white/10" data-testid="campaign-date" />
              </div>
              <div>
                <Label>Description</Label>
                <Input value={formData.description} onChange={e => setFormData(p => ({ ...p, description: e.target.value }))}
                  placeholder="Optional description" className="mt-1 bg-[#0a0a0a] border-white/10" />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <Label>Spotify URL</Label>
                <Input value={formData.spotify_url} onChange={e => setFormData(p => ({ ...p, spotify_url: e.target.value }))}
                  placeholder="https://open.spotify.com/..." className="mt-1 bg-[#0a0a0a] border-white/10" data-testid="campaign-spotify" />
              </div>
              <div>
                <Label>Apple Music URL</Label>
                <Input value={formData.apple_music_url} onChange={e => setFormData(p => ({ ...p, apple_music_url: e.target.value }))}
                  placeholder="https://music.apple.com/..." className="mt-1 bg-[#0a0a0a] border-white/10" data-testid="campaign-apple" />
              </div>
              <div>
                <Label>YouTube URL</Label>
                <Input value={formData.youtube_url} onChange={e => setFormData(p => ({ ...p, youtube_url: e.target.value }))}
                  placeholder="https://youtube.com/..." className="mt-1 bg-[#0a0a0a] border-white/10" data-testid="campaign-youtube" />
              </div>
            </div>
            <div className="flex gap-3">
              <Button type="submit" disabled={submitting} className="btn-animated rounded-full gap-2" data-testid="submit-campaign-btn">
                {submitting ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <PaperPlaneTilt className="w-4 h-4" />}
                Create Campaign
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowForm(false)} className="rounded-full">Cancel</Button>
            </div>
          </form>
        )}

        {/* Campaign List */}
        {campaigns.length === 0 ? (
          <div className="card-kalmori p-12 text-center">
            <CalendarBlank className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">No campaigns yet</h2>
            <p className="text-gray-400 mb-4">Create a pre-save campaign to build hype for your upcoming release.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {campaigns.map(c => (
              <div key={c.id} className="bg-[#111] border border-white/10 rounded-2xl p-5" data-testid={`campaign-${c.id}`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 rounded-xl bg-[#1a1a1a] flex items-center justify-center flex-shrink-0 overflow-hidden">
                      {c.cover_url ? <img src={c.cover_url} alt="" className="w-full h-full object-cover" /> : <MusicNotes className="w-6 h-6 text-gray-600" />}
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-white">{c.title}</h3>
                      <p className="text-xs text-gray-400 mt-0.5">{c.artist_name} | Release: {c.release_date || 'TBA'}</p>
                      <div className="flex items-center gap-3 mt-2">
                        <span className="flex items-center gap-1 text-xs text-[#E040FB]"><Users className="w-3.5 h-3.5" /> {c.subscriber_count || 0} subscribers</span>
                        {c.spotify_url && <SpotifyLogo className="w-4 h-4 text-[#1DB954]" weight="fill" />}
                        {c.apple_music_url && <AppleLogo className="w-4 h-4 text-[#FC3C44]" weight="fill" />}
                        {c.youtube_url && <YoutubeLogo className="w-4 h-4 text-[#FF0000]" weight="fill" />}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={() => copyLink(c.id)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all" data-testid={`copy-link-${c.id}`}>
                      <Copy className="w-4 h-4" />
                    </button>
                    <button onClick={() => deleteCampaign(c.id)} className="p-2 rounded-lg bg-white/5 hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-all" data-testid={`delete-campaign-${c.id}`}>
                      <Trash className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
