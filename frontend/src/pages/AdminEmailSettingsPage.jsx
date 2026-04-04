import React, { useState, useEffect, useCallback } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Envelope, Globe, CheckCircle, XCircle, ArrowClockwise, Trash, Plus, Copy, Lightning, WarningCircle } from '@phosphor-icons/react';

const API = process.env.REACT_APP_BACKEND_URL;

const StatusBadge = ({ status }) => {
  const colors = {
    verified: 'bg-green-500/20 text-green-400 border-green-500/30',
    not_started: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    failed: 'bg-red-500/20 text-red-400 border-red-500/30',
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${colors[status] || colors.pending}`}>
      {status || 'pending'}
    </span>
  );
};

export default function AdminEmailSettingsPage() {
  const [domains, setDomains] = useState([]);
  const [currentSender, setCurrentSender] = useState('');
  const [newDomain, setNewDomain] = useState('');
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [verifying, setVerifying] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [copied, setCopied] = useState('');

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const fetchDomains = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/admin/email/domain`, { headers });
      if (res.ok) {
        const data = await res.json();
        setDomains(data.domains || []);
        setCurrentSender(data.current_sender || '');
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchDomains(); }, [fetchDomains]);

  const addDomain = async () => {
    if (!newDomain.trim()) return;
    setAdding(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${API}/api/admin/email/domain`, {
        method: 'POST', headers, body: JSON.stringify({ domain: newDomain.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to add domain');
      setSuccess(`Domain "${newDomain}" added. Add the DNS records below, then click Verify.`);
      setNewDomain('');
      fetchDomains();
    } catch (e) { setError(e.message); }
    setAdding(false);
  };

  const verifyDomain = async (domainId) => {
    setVerifying(domainId);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${API}/api/admin/email/domain/${domainId}/verify`, {
        method: 'POST', headers,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Verification failed');
      if (data.status === 'verified') {
        setSuccess('Domain verified! You can now activate it.');
      } else {
        setSuccess('Verification triggered. DNS records may take up to 48 hours to propagate. Try again later.');
      }
      fetchDomains();
    } catch (e) { setError(e.message); }
    setVerifying(null);
  };

  const activateDomain = async (domainId) => {
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${API}/api/admin/email/domain/${domainId}/activate`, {
        method: 'POST', headers,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Activation failed');
      setSuccess(data.message);
      fetchDomains();
    } catch (e) { setError(e.message); }
  };

  const deleteDomain = async (domainId) => {
    if (!window.confirm('Remove this domain? Emails will revert to the default sender.')) return;
    try {
      await fetch(`${API}/api/admin/email/domain/${domainId}`, { method: 'DELETE', headers });
      fetchDomains();
    } catch (e) { console.error(e); }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(''), 2000);
  };

  const isTestDomain = currentSender === 'onboarding@resend.dev';

  return (
    <AdminLayout>
      <div className="max-w-4xl mx-auto space-y-6" data-testid="admin-email-settings">
        <div>
          <h1 className="text-2xl font-bold text-white" data-testid="email-settings-title">Email Domain Settings</h1>
          <p className="text-gray-400 text-sm mt-1">Configure a custom sending domain for full email delivery to all users.</p>
        </div>

        {/* Current Status */}
        <div className={`rounded-xl border p-5 ${isTestDomain ? 'bg-yellow-500/5 border-yellow-500/20' : 'bg-green-500/5 border-green-500/20'}`} data-testid="current-sender-status">
          <div className="flex items-start gap-3">
            {isTestDomain ? (
              <WarningCircle className="w-6 h-6 text-yellow-400 mt-0.5 shrink-0" />
            ) : (
              <CheckCircle className="w-6 h-6 text-green-400 mt-0.5 shrink-0" />
            )}
            <div>
              <h3 className={`font-semibold ${isTestDomain ? 'text-yellow-300' : 'text-green-300'}`}>
                {isTestDomain ? 'Using Test Domain (Limited)' : 'Custom Domain Active'}
              </h3>
              <p className="text-sm text-gray-400 mt-1">
                Current sender: <span className="text-white font-mono text-xs">{currentSender}</span>
              </p>
              {isTestDomain && (
                <p className="text-sm text-yellow-400/70 mt-2">
                  Resend's test domain only delivers to the account owner's verified email. Add a custom domain below to send emails to all your users.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm flex items-center gap-2" data-testid="email-error">
            <XCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}
        {success && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 text-green-400 text-sm flex items-center gap-2" data-testid="email-success">
            <CheckCircle className="w-4 h-4 shrink-0" /> {success}
          </div>
        )}

        {/* Add Domain */}
        <div className="bg-[#111] border border-[#222] rounded-xl p-5" data-testid="add-domain-section">
          <h2 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Plus className="w-5 h-5 text-[#E040FB]" /> Add Custom Domain
          </h2>
          <div className="flex gap-3">
            <input
              type="text"
              value={newDomain}
              onChange={(e) => setNewDomain(e.target.value)}
              placeholder="e.g. mail.yourdomain.com"
              className="flex-1 bg-black border border-[#333] rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-[#7C4DFF]"
              data-testid="domain-input"
              onKeyDown={(e) => e.key === 'Enter' && addDomain()}
            />
            <button
              onClick={addDomain}
              disabled={adding || !newDomain.trim()}
              className="px-6 py-2.5 rounded-lg bg-[#7C4DFF] text-white text-sm font-medium hover:brightness-110 transition disabled:opacity-50"
              data-testid="add-domain-btn"
            >
              {adding ? 'Adding...' : 'Add Domain'}
            </button>
          </div>
          <p className="text-gray-500 text-xs mt-2">
            After adding, you'll need to configure DNS records at your domain registrar (GoDaddy, Cloudflare, Namecheap, etc.)
          </p>
        </div>

        {/* Domain List */}
        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading domains...</div>
        ) : domains.length === 0 ? (
          <div className="bg-[#111] border border-[#222] rounded-xl p-8 text-center" data-testid="no-domains">
            <Globe className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No custom domains configured yet.</p>
            <p className="text-gray-500 text-sm mt-1">Add your domain above to start sending branded emails.</p>
          </div>
        ) : (
          domains.map((d) => (
            <div key={d.id} className="bg-[#111] border border-[#222] rounded-xl overflow-hidden" data-testid={`domain-card-${d.id}`}>
              {/* Domain Header */}
              <div className="flex items-center justify-between p-5 border-b border-[#222]">
                <div className="flex items-center gap-3">
                  <Globe className="w-5 h-5 text-[#E040FB]" />
                  <div>
                    <span className="text-white font-semibold">{d.domain}</span>
                    {d.activated && (
                      <span className="ml-2 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-500/20 text-green-400 border border-green-500/30">
                        ACTIVE
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={d.status} />
                  <button
                    onClick={() => verifyDomain(d.id)}
                    disabled={verifying === d.id}
                    className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition"
                    title="Verify DNS records"
                    data-testid={`verify-btn-${d.id}`}
                  >
                    <ArrowClockwise className={`w-4 h-4 ${verifying === d.id ? 'animate-spin' : ''}`} />
                  </button>
                  {d.status === 'verified' && !d.activated && (
                    <button
                      onClick={() => activateDomain(d.id)}
                      className="px-3 py-1.5 rounded-lg bg-green-600 text-white text-xs font-medium hover:bg-green-500 transition"
                      data-testid={`activate-btn-${d.id}`}
                    >
                      <Lightning className="w-3 h-3 inline mr-1" /> Activate
                    </button>
                  )}
                  <button
                    onClick={() => deleteDomain(d.id)}
                    className="p-2 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400 transition"
                    data-testid={`delete-btn-${d.id}`}
                  >
                    <Trash className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* DNS Records */}
              {d.records && d.records.length > 0 && (
                <div className="p-5">
                  <h3 className="text-sm font-medium text-gray-300 mb-3">DNS Records to Add</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm" data-testid={`dns-table-${d.id}`}>
                      <thead>
                        <tr className="text-gray-500 text-xs uppercase tracking-wider">
                          <th className="text-left pb-2 pr-4">Type</th>
                          <th className="text-left pb-2 pr-4">Name / Host</th>
                          <th className="text-left pb-2 pr-4">Value</th>
                          <th className="text-left pb-2 pr-4">TTL</th>
                          <th className="text-left pb-2">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {d.records.map((rec, i) => (
                          <tr key={i} className="border-t border-[#1a1a1a]">
                            <td className="py-2.5 pr-4">
                              <span className="px-2 py-0.5 rounded bg-[#7C4DFF]/20 text-[#7C4DFF] text-xs font-mono font-bold">
                                {rec.type || rec.record || 'TXT'}
                              </span>
                            </td>
                            <td className="py-2.5 pr-4">
                              <div className="flex items-center gap-1">
                                <span className="text-white font-mono text-xs truncate max-w-[200px]">{rec.name}</span>
                                <button onClick={() => copyToClipboard(rec.name, `name-${i}`)} className="text-gray-600 hover:text-white">
                                  <Copy className="w-3 h-3" />
                                </button>
                                {copied === `name-${i}` && <span className="text-green-400 text-[10px]">Copied</span>}
                              </div>
                            </td>
                            <td className="py-2.5 pr-4">
                              <div className="flex items-center gap-1">
                                <span className="text-gray-300 font-mono text-xs truncate max-w-[250px]">{rec.value}</span>
                                <button onClick={() => copyToClipboard(rec.value, `val-${i}`)} className="text-gray-600 hover:text-white">
                                  <Copy className="w-3 h-3" />
                                </button>
                                {copied === `val-${i}` && <span className="text-green-400 text-[10px]">Copied</span>}
                              </div>
                            </td>
                            <td className="py-2.5 pr-4 text-gray-500 text-xs">{rec.ttl || 'Auto'}</td>
                            <td className="py-2.5"><StatusBadge status={rec.status} /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <p className="text-gray-600 text-xs mt-3">
                    Add these records at your DNS provider (Cloudflare, GoDaddy, Namecheap, etc.). Propagation can take up to 48 hours.
                  </p>
                </div>
              )}

              {/* No records yet */}
              {(!d.records || d.records.length === 0) && (
                <div className="p-5 text-gray-500 text-sm">
                  Click the refresh icon to load DNS records from Resend.
                </div>
              )}
            </div>
          ))
        )}

        {/* Instructions */}
        <div className="bg-[#111] border border-[#222] rounded-xl p-5" data-testid="setup-instructions">
          <h2 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Envelope className="w-5 h-5 text-[#7C4DFF]" /> Setup Instructions
          </h2>
          <ol className="text-gray-400 text-sm space-y-2 list-decimal list-inside">
            <li>Enter your domain name above and click <strong className="text-white">Add Domain</strong></li>
            <li>Copy the DNS records shown and add them at your domain registrar</li>
            <li>Wait for DNS propagation (usually 5-30 minutes, up to 48 hours)</li>
            <li>Click the <strong className="text-white">refresh</strong> icon to check verification status</li>
            <li>Once verified, click <strong className="text-white">Activate</strong> to start sending from your domain</li>
          </ol>
          <div className="mt-4 p-3 bg-[#0a0a0a] rounded-lg border border-[#1a1a1a]">
            <p className="text-gray-500 text-xs">
              <strong className="text-gray-300">Tip:</strong> Use a subdomain like <span className="text-[#E040FB] font-mono">mail.yourdomain.com</span> to keep your main domain's email reputation clean.
              Your emails will be sent from <span className="text-white font-mono">noreply@mail.yourdomain.com</span>.
            </p>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
