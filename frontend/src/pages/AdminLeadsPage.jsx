import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Megaphone, PaperPlaneTilt, Clock, CheckCircle, WarningCircle, User, MusicNote, Disc } from '@phosphor-icons/react';
import { toast } from 'sonner';

const AdminLeadsPage = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, stale_count: 0 });
  const [sendingAll, setSendingAll] = useState(false);
  const [sendingId, setSendingId] = useState(null);
  const [filter, setFilter] = useState('all');

  const fetchLeads = async () => {
    try {
      const res = await axios.get(`${API}/admin/leads`, { withCredentials: true });
      setLeads(res.data.leads || []);
      setStats({ total: res.data.total, stale_count: res.data.stale_count });
    } catch (err) { console.error(err); toast.error('Failed to load leads'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchLeads(); }, []);

  const sendReminder = async (leadId, leadType) => {
    setSendingId(leadId);
    try {
      const res = await axios.post(`${API}/admin/leads/send-reminder`, { lead_id: leadId, lead_type: leadType }, { withCredentials: true });
      toast.success(res.data.message);
      fetchLeads();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed'); }
    finally { setSendingId(null); }
  };

  const sendAllReminders = async () => {
    if (!window.confirm('Send reminders to all stale leads? This will email everyone with abandoned drafts.')) return;
    setSendingAll(true);
    try {
      const res = await axios.post(`${API}/admin/leads/send-all-reminders`, {}, { withCredentials: true });
      toast.success(res.data.message);
      fetchLeads();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed'); }
    finally { setSendingAll(false); }
  };

  const filteredLeads = filter === 'all' ? leads
    : filter === 'stale' ? leads.filter(l => l.stale)
    : leads.filter(l => l.type === filter);

  const TYPE_ICONS = {
    draft_release: <MusicNote className="w-4 h-4 text-[#7C4DFF]" />,
    draft_beat: <Disc className="w-4 h-4 text-[#E040FB]" />,
  };
  const TYPE_LABELS = { draft_release: 'Draft Release', draft_beat: 'Draft Beat' };

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="leads-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Lead <span className="text-[#FFD700]">Follow-Up</span></h1>
            <p className="text-xs text-gray-500 mt-1">Track abandoned drafts and send reminders to re-engage users.</p>
          </div>
          <Button onClick={sendAllReminders} disabled={sendingAll || stats.stale_count === 0}
            className="bg-[#FFD700] hover:bg-[#FFD700]/80 text-black text-xs font-bold gap-1" data-testid="send-all-reminders-btn">
            <Megaphone className="w-4 h-4" /> {sendingAll ? 'Sending...' : `Remind All Stale (${stats.stale_count})`}
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4" data-testid="lead-stats">
          <div className="bg-[#141414] border border-white/10 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold font-mono text-white">{stats.total}</p>
            <p className="text-[10px] text-gray-500 mt-1">Total Drafts</p>
          </div>
          <div className="bg-[#141414] border border-white/10 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold font-mono text-[#FF6B6B]">{stats.stale_count}</p>
            <p className="text-[10px] text-gray-500 mt-1">Stale (24h+)</p>
          </div>
          <div className="bg-[#141414] border border-white/10 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold font-mono text-[#1DB954]">{leads.filter(l => l.reminder_sent).length}</p>
            <p className="text-[10px] text-gray-500 mt-1">Reminded</p>
          </div>
        </div>

        {/* Filter */}
        <div className="flex gap-1 bg-[#0a0a0a] border border-white/10 rounded-xl p-1 w-fit" data-testid="lead-filters">
          {[
            { id: 'all', label: 'All' },
            { id: 'stale', label: 'Stale Only' },
            { id: 'draft_release', label: 'Releases' },
            { id: 'draft_beat', label: 'Beats' },
          ].map(f => (
            <button key={f.id} onClick={() => setFilter(f.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filter === f.id ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-gray-300'}`}
              data-testid={`filter-${f.id}`}>
              {f.label}
            </button>
          ))}
        </div>

        {/* Leads List */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-2 border-[#FFD700] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filteredLeads.length === 0 ? (
          <div className="bg-[#141414] border border-white/10 rounded-xl p-10 text-center">
            <CheckCircle className="w-12 h-12 text-[#1DB954]/20 mx-auto mb-3" />
            <p className="text-sm text-gray-500">No abandoned drafts found. All users are active!</p>
          </div>
        ) : (
          <div className="space-y-3" data-testid="leads-list">
            {filteredLeads.map(l => (
              <div key={l.id} className={`bg-[#141414] border rounded-xl p-4 flex items-center gap-4 ${l.stale ? 'border-[#FF6B6B]/30 bg-[#FF6B6B]/[0.02]' : 'border-white/10'}`}
                data-testid={`lead-${l.id}`}>
                <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                  {TYPE_ICONS[l.type] || <Clock className="w-4 h-4 text-gray-500" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-white truncate">{l.title}</h4>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-gray-400 font-medium">
                      {TYPE_LABELS[l.type] || l.type}
                    </span>
                    {l.stale && <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#FF6B6B]/10 text-[#FF6B6B] font-bold">STALE</span>}
                    {l.reminder_sent && <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#1DB954]/10 text-[#1DB954] font-bold">REMINDED</span>}
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-2">
                    <User className="w-3 h-3" /> {l.user_name} ({l.user_email})
                    {l.created_at && <span className="ml-2">· {new Date(l.created_at).toLocaleDateString()}</span>}
                  </p>
                </div>
                <Button size="sm" disabled={sendingId === l.id || l.reminder_sent}
                  onClick={() => sendReminder(l.id, l.type)}
                  className={`text-xs font-bold gap-1 ${l.reminder_sent ? 'bg-gray-800 text-gray-500' : 'bg-[#FFD700] hover:bg-[#FFD700]/80 text-black'}`}
                  data-testid={`remind-${l.id}`}>
                  <PaperPlaneTilt className="w-3.5 h-3.5" />
                  {sendingId === l.id ? 'Sending...' : l.reminder_sent ? 'Sent' : 'Remind'}
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminLeadsPage;
