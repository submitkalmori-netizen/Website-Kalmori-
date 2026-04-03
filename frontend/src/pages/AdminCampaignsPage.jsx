import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { PaperPlaneTilt, Plus, Trash, Eye, PaperPlaneRight, UsersThree, EnvelopeSimple, Clock } from '@phosphor-icons/react';
import { toast } from 'sonner';

const AdminCampaignsPage = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [subject, setSubject] = useState('');
  const [bodyHtml, setBodyHtml] = useState('');
  const [audience, setAudience] = useState('all');
  const [headerTitle, setHeaderTitle] = useState('');
  const [headerGradient, setHeaderGradient] = useState('linear-gradient(135deg,#7C4DFF 0%,#E040FB 100%)');
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(null);
  const [previewHtml, setPreviewHtml] = useState(null);

  const fetchCampaigns = async () => {
    try {
      const res = await axios.get(`${API}/admin/campaigns`, { withCredentials: true });
      setCampaigns(res.data.campaigns || []);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchCampaigns(); }, []);

  const createCampaign = async () => {
    if (!name.trim() || !subject.trim() || !bodyHtml.trim()) {
      toast.error('Name, subject, and body are required');
      return;
    }
    setSaving(true);
    try {
      await axios.post(`${API}/admin/campaigns`, {
        name, subject, body_html: bodyHtml, audience, header_title: headerTitle, header_gradient: headerGradient,
      }, { withCredentials: true });
      toast.success('Campaign created');
      setShowForm(false);
      setName(''); setSubject(''); setBodyHtml(''); setHeaderTitle('');
      fetchCampaigns();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed'); }
    finally { setSaving(false); }
  };

  const sendCampaign = async (id) => {
    if (!window.confirm('Send this campaign to all matching users? This cannot be undone.')) return;
    setSending(id);
    try {
      const res = await axios.post(`${API}/admin/campaigns/${id}/send`, {}, { withCredentials: true });
      toast.success(res.data.message);
      fetchCampaigns();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed'); }
    finally { setSending(null); }
  };

  const deleteCampaign = async (id) => {
    try {
      await axios.delete(`${API}/admin/campaigns/${id}`, { withCredentials: true });
      toast.success('Campaign deleted');
      fetchCampaigns();
    } catch (err) { toast.error('Failed'); }
  };

  const previewCampaign = async (id) => {
    try {
      const res = await axios.post(`${API}/admin/campaigns/${id}/preview`, {}, { withCredentials: true });
      setPreviewHtml(res.data.html);
    } catch (err) { toast.error('Preview failed'); }
  };

  const AUDIENCE_LABELS = { all: 'All Users', artist: 'Artists Only', label_producer: 'Producers / Labels Only' };
  const GRADIENT_OPTIONS = [
    { label: 'Purple', value: 'linear-gradient(135deg,#7C4DFF 0%,#E040FB 100%)' },
    { label: 'Green', value: 'linear-gradient(135deg,#1DB954 0%,#4CAF50 100%)' },
    { label: 'Red', value: 'linear-gradient(135deg,#E53935 0%,#FF5722 100%)' },
    { label: 'Gold', value: 'linear-gradient(135deg,#FFD700 0%,#FFA000 100%)' },
    { label: 'Blue', value: 'linear-gradient(135deg,#2196F3 0%,#03A9F4 100%)' },
  ];

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="campaigns-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Marketing <span className="text-[#E040FB]">Campaigns</span></h1>
            <p className="text-xs text-gray-500 mt-1">Create and send branded email campaigns to your users.</p>
          </div>
          <Button onClick={() => setShowForm(true)} className="bg-[#E040FB] hover:bg-[#E040FB]/80 text-white text-xs font-bold gap-1" data-testid="new-campaign-btn">
            <Plus className="w-4 h-4" /> New Campaign
          </Button>
        </div>

        {/* Create Form */}
        {showForm && (
          <div className="bg-[#141414] border border-[#E040FB]/20 rounded-xl p-6 space-y-4" data-testid="campaign-form">
            <h3 className="text-sm font-bold text-white">Create Campaign</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Campaign Name *</label>
                <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. New Year Promo"
                  className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-[#E040FB]/50 focus:outline-none"
                  data-testid="campaign-name" />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Subject Line *</label>
                <input value={subject} onChange={e => setSubject(e.target.value)} placeholder="e.g. Big news for Kalmori artists!"
                  className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-[#E040FB]/50 focus:outline-none"
                  data-testid="campaign-subject" />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Audience</label>
                <select value={audience} onChange={e => setAudience(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white" data-testid="campaign-audience">
                  <option value="all">All Users</option>
                  <option value="artist">Artists Only</option>
                  <option value="label_producer">Producers / Labels Only</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Header Color</label>
                <select value={headerGradient} onChange={e => setHeaderGradient(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white" data-testid="campaign-gradient">
                  {GRADIENT_OPTIONS.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Header Title (optional, defaults to subject)</label>
              <input value={headerTitle} onChange={e => setHeaderTitle(e.target.value)} placeholder="e.g. Exciting News!"
                className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-[#E040FB]/50 focus:outline-none" />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Email Body (HTML) * — Use {'{{name}}'} for personalization</label>
              <textarea value={bodyHtml} onChange={e => setBodyHtml(e.target.value)} rows={6}
                placeholder='<p style="color:#ccc;">Hey {{name}},</p><p style="color:#999;">Check out our new features...</p>'
                className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white font-mono placeholder-gray-600 focus:border-[#E040FB]/50 focus:outline-none resize-y"
                data-testid="campaign-body" />
            </div>
            <div className="flex items-center gap-3">
              <Button onClick={createCampaign} disabled={saving}
                className="bg-[#E040FB] hover:bg-[#E040FB]/80 text-white text-xs font-bold gap-1" data-testid="save-campaign-btn">
                {saving ? 'Saving...' : 'Save Campaign'}
              </Button>
              <Button variant="ghost" onClick={() => setShowForm(false)} className="text-xs text-gray-400">Cancel</Button>
            </div>
          </div>
        )}

        {/* Campaigns List */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-2 border-[#E040FB] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : campaigns.length === 0 ? (
          <div className="bg-[#141414] border border-white/10 rounded-xl p-10 text-center">
            <EnvelopeSimple className="w-12 h-12 text-white/10 mx-auto mb-3" />
            <p className="text-sm text-gray-500">No campaigns yet. Create one to reach your users.</p>
          </div>
        ) : (
          <div className="space-y-3" data-testid="campaigns-list">
            {campaigns.map(c => (
              <div key={c.id} className="bg-[#141414] border border-white/10 rounded-xl p-5 flex items-center gap-4" data-testid={`campaign-${c.id}`}>
                <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: c.header_gradient || '#7C4DFF' }}>
                  <PaperPlaneTilt className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-white truncate">{c.name}</h4>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${c.status === 'sent' ? 'bg-[#1DB954]/10 text-[#1DB954]' : 'bg-gray-800 text-gray-500'}`}>
                      {c.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mt-0.5 truncate">{c.subject}</p>
                  <p className="text-[10px] text-gray-600 mt-0.5">
                    {AUDIENCE_LABELS[c.audience] || c.audience}
                    {c.sent_count > 0 && <span className="ml-2">· Sent to {c.sent_count} users</span>}
                    {c.sent_at && <span className="ml-2">· {new Date(c.sent_at).toLocaleDateString()}</span>}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button onClick={() => previewCampaign(c.id)} title="Preview"
                    className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors" data-testid={`preview-${c.id}`}>
                    <Eye className="w-4 h-4" />
                  </button>
                  {c.status === 'draft' && (
                    <button onClick={() => sendCampaign(c.id)} title="Send" disabled={sending === c.id}
                      className="p-2 rounded-lg hover:bg-[#1DB954]/10 text-[#1DB954] transition-colors" data-testid={`send-${c.id}`}>
                      <PaperPlaneRight className="w-4 h-4" />
                    </button>
                  )}
                  <button onClick={() => deleteCampaign(c.id)} title="Delete"
                    className="p-2 rounded-lg hover:bg-[#FF6B6B]/10 text-gray-400 hover:text-[#FF6B6B] transition-colors" data-testid={`delete-${c.id}`}>
                    <Trash className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Preview Modal */}
        {previewHtml && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setPreviewHtml(null)} data-testid="preview-modal">
            <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-auto" onClick={e => e.stopPropagation()}>
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Email Preview</h3>
                <button onClick={() => setPreviewHtml(null)} className="text-gray-400 hover:text-white text-xs">Close</button>
              </div>
              <div className="p-4" dangerouslySetInnerHTML={{ __html: previewHtml }} />
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminCampaignsPage;
