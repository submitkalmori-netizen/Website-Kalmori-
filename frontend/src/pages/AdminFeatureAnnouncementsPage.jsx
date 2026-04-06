import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../App';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Lightning, Star, Rocket, ChartLineUp, MusicNote, ShoppingCart, Users, Megaphone, Trash, Plus, X } from '@phosphor-icons/react';
import { toast } from 'sonner';

const PLAN_OPTIONS = [
  { value: 'free', label: 'Free (All Users)', color: '#A1A1AA' },
  { value: 'rise', label: 'Rise & Above', color: '#FFCC00' },
  { value: 'pro', label: 'Pro Only', color: '#E040FB' },
];

const CATEGORY_OPTIONS = [
  { value: 'general', label: 'General' },
  { value: 'distribution', label: 'Distribution' },
  { value: 'analytics', label: 'Analytics' },
  { value: 'ai', label: 'AI Features' },
  { value: 'marketplace', label: 'Marketplace' },
  { value: 'social', label: 'Social' },
];

const ICON_OPTIONS = [
  { value: 'Lightning', label: 'Lightning', icon: <Lightning className="w-4 h-4" /> },
  { value: 'Star', label: 'Star', icon: <Star className="w-4 h-4" /> },
  { value: 'Rocket', label: 'Rocket', icon: <Rocket className="w-4 h-4" /> },
  { value: 'ChartLineUp', label: 'Chart', icon: <ChartLineUp className="w-4 h-4" /> },
  { value: 'MusicNote', label: 'Music', icon: <MusicNote className="w-4 h-4" /> },
  { value: 'ShoppingCart', label: 'Cart', icon: <ShoppingCart className="w-4 h-4" /> },
  { value: 'Users', label: 'Users', icon: <Users className="w-4 h-4" /> },
  { value: 'Megaphone', label: 'Announce', icon: <Megaphone className="w-4 h-4" /> },
];

const COLOR_OPTIONS = ['#7C4DFF', '#E040FB', '#1DB954', '#FF3B30', '#FFCC00', '#007AFF', '#FF9500', '#00FFFF'];

export default function AdminFeatureAnnouncementsPage() {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    title: '', description: '', min_plan: 'free', category: 'general', icon: 'Lightning', color: '#7C4DFF',
  });

  useEffect(() => { fetchAnnouncements(); }, []);

  const fetchAnnouncements = async () => {
    try {
      const res = await axios.get(`${API}/admin/feature-announcements`, { withCredentials: true });
      setAnnouncements(res.data);
    } catch (err) { toast.error('Failed to load announcements'); }
    finally { setLoading(false); }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.description.trim()) {
      toast.error('Title and description are required');
      return;
    }
    setCreating(true);
    try {
      const res = await axios.post(`${API}/admin/feature-announcements`, form, { withCredentials: true });
      toast.success(res.data.message || 'Announcement created!');
      setShowForm(false);
      setForm({ title: '', description: '', min_plan: 'free', category: 'general', icon: 'Lightning', color: '#7C4DFF' });
      fetchAnnouncements();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to create announcement'); }
    finally { setCreating(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this announcement?')) return;
    try {
      await axios.delete(`${API}/admin/feature-announcements/${id}`, { withCredentials: true });
      toast.success('Announcement deleted');
      setAnnouncements(prev => prev.filter(a => a.id !== id));
    } catch { toast.error('Failed to delete'); }
  };

  const getIconComponent = (name) => {
    const found = ICON_OPTIONS.find(i => i.value === name);
    return found ? found.icon : <Lightning className="w-4 h-4" />;
  };

  if (loading) return <AdminLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" /></div></AdminLayout>;

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="admin-feature-announcements">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Feature Announcements</h1>
            <p className="text-sm text-[#A1A1AA] mt-1">Create and manage feature announcements. Each announcement notifies all users.</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)} className="bg-[#7C4DFF] hover:bg-[#7C4DFF]/80 text-white gap-2" data-testid="new-announcement-btn">
            {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            {showForm ? 'Cancel' : 'New Announcement'}
          </Button>
        </div>

        {showForm && (
          <form onSubmit={handleCreate} className="bg-[#141414] border border-white/10 rounded-lg p-6 space-y-4" data-testid="announcement-form">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-[#A1A1AA] block mb-1.5">Title</label>
                <Input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                  placeholder="e.g. Spotify Integration" className="bg-[#0a0a0a] border-white/10 text-white" data-testid="announcement-title" />
              </div>
              <div>
                <label className="text-xs text-[#A1A1AA] block mb-1.5">Category</label>
                <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                  className="w-full h-10 px-3 rounded-md bg-[#0a0a0a] border border-white/10 text-white text-sm" data-testid="announcement-category">
                  {CATEGORY_OPTIONS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs text-[#A1A1AA] block mb-1.5">Description</label>
              <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                placeholder="What does this feature do?"
                className="w-full h-24 px-3 py-2 rounded-md bg-[#0a0a0a] border border-white/10 text-white text-sm resize-none" data-testid="announcement-description" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs text-[#A1A1AA] block mb-1.5">Minimum Plan</label>
                <div className="flex gap-2">
                  {PLAN_OPTIONS.map(p => (
                    <button key={p.value} type="button" onClick={() => setForm(f => ({ ...f, min_plan: p.value }))}
                      className={`flex-1 px-3 py-2 rounded-md text-xs font-medium border transition-all ${form.min_plan === p.value ? 'border-white/40 bg-white/10 text-white' : 'border-white/10 text-[#A1A1AA] hover:border-white/20'}`}
                      data-testid={`plan-${p.value}`}>
                      <span className="w-2 h-2 rounded-full inline-block mr-1.5" style={{ backgroundColor: p.color }} />
                      {p.value.charAt(0).toUpperCase() + p.value.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-xs text-[#A1A1AA] block mb-1.5">Icon</label>
                <div className="flex gap-1.5 flex-wrap">
                  {ICON_OPTIONS.map(i => (
                    <button key={i.value} type="button" onClick={() => setForm(f => ({ ...f, icon: i.value }))}
                      className={`w-9 h-9 rounded-md flex items-center justify-center border transition-all ${form.icon === i.value ? 'border-[#7C4DFF] bg-[#7C4DFF]/20 text-white' : 'border-white/10 text-[#A1A1AA] hover:border-white/20'}`}
                      title={i.label}>
                      {i.icon}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-xs text-[#A1A1AA] block mb-1.5">Color</label>
                <div className="flex gap-1.5 flex-wrap">
                  {COLOR_OPTIONS.map(c => (
                    <button key={c} type="button" onClick={() => setForm(f => ({ ...f, color: c }))}
                      className={`w-9 h-9 rounded-md border transition-all ${form.color === c ? 'border-white scale-110' : 'border-transparent hover:scale-105'}`}
                      style={{ backgroundColor: c }} />
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-white/5">
              <p className="text-xs text-[#A1A1AA]">This will send a notification to all users.</p>
              <Button type="submit" disabled={creating} className="bg-[#7C4DFF] hover:bg-[#7C4DFF]/80 text-white gap-2" data-testid="create-announcement-submit">
                {creating ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Megaphone className="w-4 h-4" />}
                Publish Announcement
              </Button>
            </div>
          </form>
        )}

        <div className="space-y-3" data-testid="announcements-list">
          {announcements.length === 0 ? (
            <div className="bg-[#141414] border border-white/10 rounded-lg p-12 text-center">
              <Megaphone className="w-10 h-10 text-[#A1A1AA] mx-auto mb-3" />
              <p className="text-[#A1A1AA]">No announcements yet. Create one to notify all users.</p>
            </div>
          ) : announcements.map(a => (
            <div key={a.id} className="bg-[#141414] border border-white/10 rounded-lg p-4 flex items-start gap-4" data-testid={`announcement-${a.id}`}>
              <div className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" style={{ backgroundColor: `${a.color || '#7C4DFF'}20`, color: a.color || '#7C4DFF' }}>
                {getIconComponent(a.icon)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-sm font-bold text-white">{a.title}</h3>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${a.min_plan === 'pro' ? 'bg-[#E040FB]/20 text-[#E040FB]' : a.min_plan === 'rise' ? 'bg-[#FFCC00]/20 text-[#FFCC00]' : 'bg-white/10 text-[#A1A1AA]'}`}>
                    {a.min_plan?.toUpperCase() || 'FREE'}
                  </span>
                  <span className="text-[10px] text-[#A1A1AA] px-2 py-0.5 rounded-full bg-white/5">{a.category || 'general'}</span>
                </div>
                <p className="text-xs text-[#A1A1AA] line-clamp-2">{a.description}</p>
                <p className="text-[10px] text-[#555] mt-2">{a.created_at ? new Date(a.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}</p>
              </div>
              <button onClick={() => handleDelete(a.id)}
                className="p-2 text-[#A1A1AA] hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all" data-testid={`delete-${a.id}`}>
                <Trash className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </AdminLayout>
  );
}
