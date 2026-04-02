import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API, useAuth } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  User, 
  MusicNotes,
  MusicNote,
  Globe,
  Gear,
  Crown,
  CheckCircle,
  UploadSimple,
  Bell,
  SpotifyLogo,
  Link as LinkIcon,
  PlugsConnected
} from '@phosphor-icons/react';
import { toast } from 'sonner';

const NOTIF_PREF_LABELS = {
  email_releases: { label: 'Release Updates', desc: 'Email when releases are approved or distributed' },
  email_collaborations: { label: 'Collaboration Invites', desc: 'Email when someone invites you to collaborate' },
  email_payments: { label: 'Payment Receipts', desc: 'Email receipts for purchases and subscriptions' },
  email_marketing: { label: 'Marketing & Tips', desc: 'Promotional emails and distribution tips' },
  push_releases: { label: 'Release Notifications', desc: 'In-app notifications for release status changes' },
  push_collaborations: { label: 'Collaboration Updates', desc: 'In-app notifications for collaboration activity' },
  push_payments: { label: 'Payment Alerts', desc: 'In-app notifications for payments and earnings' },
  push_milestones: { label: 'Milestone Celebrations', desc: 'In-app notifications when you hit streaming milestones' },
};

const SettingsPage = () => {
  const { user, checkAuth } = useAuth();
  const [profile, setProfile] = useState({
    artist_name: '',
    bio: '',
    genre: '',
    country: '',
    website: '',
    spotify_url: '',
    apple_music_url: '',
    instagram: '',
    twitter: ''
  });
  const [plans, setPlans] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [notifPrefs, setNotifPrefs] = useState({});
  const [savingNotifPrefs, setSavingNotifPrefs] = useState(false);
  const [spotifyStatus, setSpotifyStatus] = useState(null);

  useEffect(() => {
    fetchData();
    fetchNotifPrefs();
    fetchSpotifyStatus();
  }, []);

  const fetchSpotifyStatus = async () => {
    try {
      const res = await axios.get(`${API}/integrations/spotify/status`, { withCredentials: true });
      setSpotifyStatus(res.data);
    } catch {}
  };

  const fetchNotifPrefs = async () => {
    try {
      const res = await axios.get(`${API}/settings/notification-preferences`, { withCredentials: true });
      setNotifPrefs(res.data || {});
    } catch {}
  };

  const toggleNotifPref = async (key) => {
    const newVal = !notifPrefs[key];
    setNotifPrefs(prev => ({ ...prev, [key]: newVal }));
    setSavingNotifPrefs(true);
    try {
      await axios.put(`${API}/settings/notification-preferences`, { [key]: newVal }, { withCredentials: true });
    } catch { toast.error('Failed to update preference'); }
    finally { setSavingNotifPrefs(false); }
  };

  const fetchData = async () => {
    try {
      const [profileRes, plansRes] = await Promise.all([
        axios.get(`${API}/artists/profile`),
        axios.get(`${API}/subscriptions/plans`)
      ]);
      setProfile(profileRes.data);
      setPlans(plansRes.data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/artists/profile`, profile);
      toast.success('Profile saved!');
      checkAuth();
    } catch (error) {
      toast.error('Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file');
      return;
    }
    
    setUploadingAvatar(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await axios.post(`${API}/artists/avatar`, formData);
      toast.success('Avatar uploaded!');
      checkAuth();
    } catch (error) {
      toast.error('Failed to upload avatar');
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handleUpgradePlan = async (plan) => {
    try {
      await axios.post(`${API}/subscriptions/upgrade`, null, { params: { plan } });
      toast.success(`Upgraded to ${plans[plan]?.name} plan!`);
      checkAuth();
    } catch (error) {
      toast.error('Failed to upgrade plan');
    }
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

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto" data-testid="settings-page">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-8">Settings</h1>

        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="bg-[#141414] border border-white/10">
            <TabsTrigger value="profile" className="data-[state=active]:bg-[#FF3B30] data-[state=active]:text-white">
              <User className="w-4 h-4 mr-2" /> Profile
            </TabsTrigger>
            <TabsTrigger value="subscription" className="data-[state=active]:bg-[#FF3B30] data-[state=active]:text-white">
              <Crown className="w-4 h-4 mr-2" /> Subscription
            </TabsTrigger>
            <TabsTrigger value="notifications" className="data-[state=active]:bg-[#FF3B30] data-[state=active]:text-white" data-testid="notifications-settings-tab">
              <Bell className="w-4 h-4 mr-2" /> Notifications
            </TabsTrigger>
            <TabsTrigger value="integrations" className="data-[state=active]:bg-[#FF3B30] data-[state=active]:text-white" data-testid="integrations-settings-tab">
              <PlugsConnected className="w-4 h-4 mr-2" /> Integrations
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            {/* Avatar */}
            <div className="bg-[#141414] border border-white/10 rounded-md p-6">
              <h2 className="text-lg font-medium mb-6 flex items-center gap-2">
                <User className="w-5 h-5 text-[#FF3B30]" />
                Avatar
              </h2>
              
              <div className="flex items-center gap-6">
                <label className="relative w-24 h-24 cursor-pointer group">
                  <div className="w-full h-full rounded-full bg-[#1E1E1E] overflow-hidden">
                    {user?.avatar_url ? (
                      <img 
                        src={`${API.replace('/api', '')}/api/files/${user.avatar_url}`}
                        alt="Avatar"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-3xl font-bold text-[#FF3B30]">
                        {user?.name?.charAt(0).toUpperCase() || 'A'}
                      </div>
                    )}
                  </div>
                  <div className="absolute inset-0 rounded-full bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <UploadSimple className="w-6 h-6 text-white" />
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                    disabled={uploadingAvatar}
                    data-testid="avatar-upload-input"
                  />
                </label>
                <div>
                  <p className="font-medium">{user?.name}</p>
                  <p className="text-sm text-[#A1A1AA]">{user?.email}</p>
                </div>
              </div>
            </div>

            {/* Artist Profile */}
            <div className="bg-[#141414] border border-white/10 rounded-md p-6">
              <h2 className="text-lg font-medium mb-6 flex items-center gap-2">
                <MusicNotes className="w-5 h-5 text-[#FF3B30]" />
                Artist Profile
              </h2>

              <div className="space-y-4">
                <div>
                  <Label className="text-white mb-2 block">Artist Name</Label>
                  <Input
                    value={profile.artist_name}
                    onChange={(e) => setProfile({ ...profile, artist_name: e.target.value })}
                    className="bg-[#0A0A0A] border-white/10 text-white"
                    data-testid="artist-name-input"
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">Bio</Label>
                  <Textarea
                    value={profile.bio || ''}
                    onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                    placeholder="Tell your story..."
                    rows={4}
                    className="bg-[#0A0A0A] border-white/10 text-white"
                    data-testid="bio-textarea"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white mb-2 block">Genre</Label>
                    <Input
                      value={profile.genre || ''}
                      onChange={(e) => setProfile({ ...profile, genre: e.target.value })}
                      placeholder="e.g., Pop, Rock"
                      className="bg-[#0A0A0A] border-white/10 text-white"
                      data-testid="genre-input"
                    />
                  </div>
                  <div>
                    <Label className="text-white mb-2 block">Country</Label>
                    <Input
                      value={profile.country || ''}
                      onChange={(e) => setProfile({ ...profile, country: e.target.value })}
                      placeholder="e.g., United States"
                      className="bg-[#0A0A0A] border-white/10 text-white"
                      data-testid="country-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Social Links */}
            <div className="bg-[#141414] border border-white/10 rounded-md p-6">
              <h2 className="text-lg font-medium mb-6 flex items-center gap-2">
                <Globe className="w-5 h-5 text-[#007AFF]" />
                Social Links
              </h2>

              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white mb-2 block">Website</Label>
                    <Input
                      value={profile.website || ''}
                      onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                      placeholder="https://yoursite.com"
                      className="bg-[#0A0A0A] border-white/10 text-white"
                      data-testid="website-input"
                    />
                  </div>
                  <div>
                    <Label className="text-white mb-2 block">Spotify URL</Label>
                    <Input
                      value={profile.spotify_url || ''}
                      onChange={(e) => setProfile({ ...profile, spotify_url: e.target.value })}
                      placeholder="https://spotify.com/artist/..."
                      className="bg-[#0A0A0A] border-white/10 text-white"
                      data-testid="spotify-input"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white mb-2 block">Instagram</Label>
                    <Input
                      value={profile.instagram || ''}
                      onChange={(e) => setProfile({ ...profile, instagram: e.target.value })}
                      placeholder="@username"
                      className="bg-[#0A0A0A] border-white/10 text-white"
                      data-testid="instagram-input"
                    />
                  </div>
                  <div>
                    <Label className="text-white mb-2 block">Twitter</Label>
                    <Input
                      value={profile.twitter || ''}
                      onChange={(e) => setProfile({ ...profile, twitter: e.target.value })}
                      placeholder="@username"
                      className="bg-[#0A0A0A] border-white/10 text-white"
                      data-testid="twitter-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button 
                onClick={handleSaveProfile}
                disabled={saving}
                className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white"
                data-testid="save-profile-btn"
              >
                {saving ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  'Save Changes'
                )}
              </Button>
            </div>
          </TabsContent>

          {/* Subscription Tab */}
          <TabsContent value="subscription" className="space-y-6">
            <div className="bg-[#141414] border border-white/10 rounded-md p-6">
              <h2 className="text-lg font-medium mb-2">Current Plan</h2>
              <p className="text-[#A1A1AA] text-sm mb-6">
                You are currently on the <span className="text-[#FFCC00] font-semibold uppercase">{user?.plan || 'Free'}</span> plan
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(plans).map(([key, plan]) => (
                  <div 
                    key={key}
                    className={`p-6 rounded-md border ${
                      user?.plan === key 
                        ? 'border-[#FF3B30] bg-[#FF3B30]/10' 
                        : 'border-white/10 bg-[#0A0A0A]'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold">{plan.name}</h3>
                      {user?.plan === key && (
                        <CheckCircle className="w-5 h-5 text-[#22C55E]" weight="fill" />
                      )}
                    </div>
                    
                    <p className="text-2xl font-bold font-mono mb-4">
                      ${plan.price}
                      <span className="text-sm text-[#A1A1AA] font-normal">/mo</span>
                    </p>
                    
                    <ul className="space-y-2 mb-6">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="text-sm text-[#A1A1AA] flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-[#22C55E]" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    
                    {plan.revenue_share > 0 && (
                      <p className="text-xs text-[#FFCC00] mb-4">
                        Note: {plan.revenue_share}% revenue share
                      </p>
                    )}
                    
                    {user?.plan !== key && (
                      <Button
                        onClick={() => handleUpgradePlan(key)}
                        className={`w-full ${
                          key === 'rise' 
                            ? 'bg-[#FF3B30] hover:bg-[#FF3B30]/90' 
                            : 'bg-white/10 hover:bg-white/20'
                        } text-white`}
                        data-testid={`upgrade-${key}-btn`}
                      >
                        {key === 'free' ? 'Downgrade' : 'Upgrade'}
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications" className="space-y-6">
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white mb-1">Email Notifications</h2>
                <p className="text-sm text-gray-400">Choose what emails you receive</p>
              </div>
              <div className="space-y-3">
                {Object.entries(NOTIF_PREF_LABELS).filter(([k]) => k.startsWith('email_')).map(([key, { label, desc }]) => (
                  <div key={key} className="flex items-center justify-between p-4 bg-[#141414] border border-white/10 rounded-lg" data-testid={`pref-${key}`}>
                    <div>
                      <p className="text-sm font-medium text-white">{label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
                    </div>
                    <Switch checked={!!notifPrefs[key]} onCheckedChange={() => toggleNotifPref(key)} data-testid={`toggle-${key}`} />
                  </div>
                ))}
              </div>
              <div className="pt-4">
                <h2 className="text-lg font-bold text-white mb-1">In-App Notifications</h2>
                <p className="text-sm text-gray-400">Choose what notifications appear in your dashboard</p>
              </div>
              <div className="space-y-3">
                {Object.entries(NOTIF_PREF_LABELS).filter(([k]) => k.startsWith('push_')).map(([key, { label, desc }]) => (
                  <div key={key} className="flex items-center justify-between p-4 bg-[#141414] border border-white/10 rounded-lg" data-testid={`pref-${key}`}>
                    <div>
                      <p className="text-sm font-medium text-white">{label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
                    </div>
                    <Switch checked={!!notifPrefs[key]} onCheckedChange={() => toggleNotifPref(key)} data-testid={`toggle-${key}`} />
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Integrations Tab */}
          <TabsContent value="integrations" className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-white mb-1">Connected Services</h2>
              <p className="text-sm text-gray-400">Link your streaming accounts for enhanced analytics</p>
            </div>

            {/* Spotify */}
            <div className="p-5 bg-[#141414] border border-white/10 rounded-lg" data-testid="spotify-integration">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-[#1DB954]/15 flex items-center justify-center">
                    <SpotifyLogo className="w-7 h-7 text-[#1DB954]" weight="fill" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white">Spotify for Artists</p>
                    <p className="text-xs text-gray-500">
                      {spotifyStatus?.connected ? `Connected as ${spotifyStatus.display_name || 'your account'}` : 'Connect to import real streaming data'}
                    </p>
                  </div>
                </div>
                {spotifyStatus?.connected ? (
                  <button onClick={async () => {
                    await axios.delete(`${API}/integrations/spotify/disconnect`, { withCredentials: true });
                    setSpotifyStatus({ connected: false });
                    toast.success('Spotify disconnected');
                  }} className="px-4 py-2 text-xs font-medium text-red-400 border border-red-400/30 rounded-full hover:bg-red-400/10 transition-all" data-testid="disconnect-spotify">
                    Disconnect
                  </button>
                ) : (
                  <button onClick={() => toast.info('Spotify OAuth coming soon! Connect your Spotify for Artists account for real-time streaming analytics.')}
                    className="px-4 py-2 text-xs font-bold text-[#1DB954] border border-[#1DB954]/30 rounded-full hover:bg-[#1DB954]/10 transition-all flex items-center gap-2" data-testid="connect-spotify">
                    <LinkIcon className="w-3.5 h-3.5" /> Connect
                  </button>
                )}
              </div>
            </div>

            {/* Apple Music */}
            <div className="p-5 bg-[#141414] border border-white/10 rounded-lg opacity-60">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-[#FC3C44]/15 flex items-center justify-center">
                    <MusicNote className="w-7 h-7 text-[#FC3C44]" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white">Apple Music for Artists</p>
                    <p className="text-xs text-gray-500">Coming soon</p>
                  </div>
                </div>
                <span className="px-3 py-1 text-[10px] font-bold text-gray-500 border border-white/10 rounded-full">COMING SOON</span>
              </div>
            </div>

            {/* YouTube */}
            <div className="p-5 bg-[#141414] border border-white/10 rounded-lg opacity-60">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-[#FF0000]/15 flex items-center justify-center">
                    <MusicNote className="w-7 h-7 text-[#FF0000]" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white">YouTube Music Analytics</p>
                    <p className="text-xs text-gray-500">Coming soon</p>
                  </div>
                </div>
                <span className="px-3 py-1 text-[10px] font-bold text-gray-500 border border-white/10 rounded-full">COMING SOON</span>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

export default SettingsPage;
