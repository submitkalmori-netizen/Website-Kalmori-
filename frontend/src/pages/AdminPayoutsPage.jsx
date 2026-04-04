import React, { useState, useEffect, useCallback } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Wallet, Check, Clock, Warning, ArrowsClockwise, DownloadSimple, MagnifyingGlass, CurrencyDollar, Export } from '@phosphor-icons/react';
import axios from 'axios';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_STYLES = {
  pending: { bg: 'bg-[#FFD700]/15', text: 'text-[#FFD700]', icon: Clock },
  processing: { bg: 'bg-[#2196F3]/15', text: 'text-[#2196F3]', icon: ArrowsClockwise },
  completed: { bg: 'bg-[#4CAF50]/15', text: 'text-[#4CAF50]', icon: Check },
  failed: { bg: 'bg-[#F44336]/15', text: 'text-[#F44336]', icon: Warning },
};

export default function AdminPayoutsPage() {
  const [withdrawals, setWithdrawals] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(new Set());
  const [processing, setProcessing] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [wRes, sRes] = await Promise.all([
        axios.get(`${API}/api/admin/payouts?status=${filterStatus}`, { withCredentials: true }),
        axios.get(`${API}/api/admin/payouts/summary`, { withCredentials: true }),
      ]);
      setWithdrawals(wRes.data.withdrawals || []);
      setSummary(sRes.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  }, [filterStatus]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = withdrawals.filter(w => {
    if (!search) return true;
    const s = search.toLowerCase();
    return w.user_name?.toLowerCase().includes(s) || w.user_email?.toLowerCase().includes(s) || w.id?.toLowerCase().includes(s);
  });

  const handleUpdateStatus = async (id, status, extra = {}) => {
    try {
      await axios.put(`${API}/api/admin/payouts/${id}`, { status, ...extra }, { withCredentials: true });
      toast.success(`Payout ${status}`);
      fetchData();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed'); }
  };

  const handleBatchProcess = async (status) => {
    if (selected.size === 0) { toast.error('Select payouts first'); return; }
    setProcessing(true);
    try {
      const res = await axios.post(`${API}/api/admin/payouts/batch`, {
        withdrawal_ids: [...selected], status,
      }, { withCredentials: true });
      toast.success(res.data.message);
      setSelected(new Set());
      fetchData();
    } catch (err) { toast.error(err.response?.data?.detail || 'Batch failed'); }
    setProcessing(false);
  };

  const handleExport = async () => {
    try {
      const res = await axios.get(`${API}/api/admin/payouts/export?status=${filterStatus}`, {
        withCredentials: true, responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `Kalmori_Payouts_${filterStatus}_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('CSV exported');
    } catch (err) { toast.error('Export failed'); }
  };

  const toggleSelect = (id) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const toggleAll = () => {
    if (selected.size === filtered.length) setSelected(new Set());
    else setSelected(new Set(filtered.map(w => w.id)));
  };

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="admin-payouts-page">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-2xl font-bold">Payout Dashboard</h1>
            <p className="text-gray-400 text-sm mt-1">Manage artist and producer payouts</p>
          </div>
          <button onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#7C4DFF] text-white text-sm font-medium hover:brightness-110 transition"
            data-testid="export-csv-btn">
            <Export className="w-4 h-4" /> Export CSV
          </button>
        </div>

        {/* Stats */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <p className="text-xs text-gray-500">Pending</p>
              <p className="text-xl font-bold text-[#FFD700]">{summary.pending_count}</p>
              <p className="text-xs text-gray-600">${summary.pending_amount.toFixed(2)}</p>
            </div>
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <p className="text-xs text-gray-500">Processing</p>
              <p className="text-xl font-bold text-[#2196F3]">{summary.processing_count}</p>
              <p className="text-xs text-gray-600">${summary.processing_amount.toFixed(2)}</p>
            </div>
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <p className="text-xs text-gray-500">Completed</p>
              <p className="text-xl font-bold text-[#4CAF50]">{summary.completed_count}</p>
              <p className="text-xs text-gray-600">${summary.completed_amount.toFixed(2)}</p>
            </div>
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <p className="text-xs text-gray-500">Failed</p>
              <p className="text-xl font-bold text-[#F44336]">{summary.failed_count}</p>
            </div>
            <div className="bg-[#111] border border-white/10 rounded-xl p-4">
              <p className="text-xs text-gray-500">Total User Balances</p>
              <p className="text-xl font-bold text-white">${summary.total_user_balances.toFixed(2)}</p>
            </div>
          </div>
        )}

        {/* Filters + Batch Actions */}
        <div className="flex flex-wrap gap-3 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <MagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, email, ID..."
              className="w-full bg-[#111] border border-[#333] rounded-lg pl-9 pr-4 py-2.5 text-white text-sm focus:outline-none focus:border-[#7C4DFF]"
              data-testid="payout-search" />
          </div>
          <select value={filterStatus} onChange={(e) => { setFilterStatus(e.target.value); setSelected(new Set()); }}
            className="bg-[#111] border border-[#333] rounded-lg px-4 py-2.5 text-white text-sm"
            data-testid="payout-filter-status">
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          {selected.size > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{selected.size} selected</span>
              <button onClick={() => handleBatchProcess('processing')} disabled={processing}
                className="px-3 py-1.5 rounded-lg bg-[#2196F3] text-white text-xs font-bold hover:brightness-110 disabled:opacity-40"
                data-testid="batch-processing-btn">Mark Processing</button>
              <button onClick={() => handleBatchProcess('completed')} disabled={processing}
                className="px-3 py-1.5 rounded-lg bg-[#4CAF50] text-white text-xs font-bold hover:brightness-110 disabled:opacity-40"
                data-testid="batch-completed-btn">Mark Completed</button>
              <button onClick={() => handleBatchProcess('failed')} disabled={processing}
                className="px-3 py-1.5 rounded-lg bg-[#F44336] text-white text-xs font-bold hover:brightness-110 disabled:opacity-40"
                data-testid="batch-failed-btn">Mark Failed</button>
            </div>
          )}
        </div>

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center h-40">
            <div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 bg-[#111] border border-white/10 rounded-xl">
            <Wallet className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No payouts found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-[#222]">
                  <th className="pb-3 pr-3">
                    <input type="checkbox" checked={selected.size === filtered.length && filtered.length > 0}
                      onChange={toggleAll} className="rounded border-[#333] accent-[#7C4DFF]" data-testid="select-all-checkbox" />
                  </th>
                  <th className="text-xs text-gray-500 font-medium pb-3 pr-4">User</th>
                  <th className="text-xs text-gray-500 font-medium pb-3 pr-4">Amount</th>
                  <th className="text-xs text-gray-500 font-medium pb-3 pr-4">Method</th>
                  <th className="text-xs text-gray-500 font-medium pb-3 pr-4">PayPal</th>
                  <th className="text-xs text-gray-500 font-medium pb-3 pr-4">Status</th>
                  <th className="text-xs text-gray-500 font-medium pb-3 pr-4">Requested</th>
                  <th className="text-xs text-gray-500 font-medium pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(w => {
                  const style = STATUS_STYLES[w.status] || STATUS_STYLES.pending;
                  const Icon = style.icon;
                  return (
                    <tr key={w.id} className="border-b border-[#181818] hover:bg-white/[0.02]" data-testid={`payout-row-${w.id}`}>
                      <td className="py-3 pr-3">
                        <input type="checkbox" checked={selected.has(w.id)}
                          onChange={() => toggleSelect(w.id)} className="rounded border-[#333] accent-[#7C4DFF]" />
                      </td>
                      <td className="py-3 pr-4">
                        <p className="text-sm text-white">{w.user_name}</p>
                        <p className="text-xs text-gray-500">{w.user_email}</p>
                      </td>
                      <td className="py-3 pr-4">
                        <span className="text-sm font-bold text-white font-mono">${w.amount?.toFixed(2)}</span>
                      </td>
                      <td className="py-3 pr-4">
                        <span className="text-xs text-gray-400 capitalize">{w.method || 'paypal'}</span>
                      </td>
                      <td className="py-3 pr-4">
                        <span className="text-xs text-gray-400 font-mono">{w.paypal_email || '-'}</span>
                      </td>
                      <td className="py-3 pr-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${style.bg} ${style.text}`}>
                          <Icon className="w-3 h-3" />
                          {w.status?.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3 pr-4">
                        <p className="text-xs text-gray-400">{w.created_at?.slice(0, 10)}</p>
                        {w.paid_at && <p className="text-[10px] text-gray-600">Paid: {w.paid_at.slice(0, 10)}</p>}
                      </td>
                      <td className="py-3">
                        <div className="flex gap-1.5">
                          {w.status === 'pending' && (
                            <button onClick={() => handleUpdateStatus(w.id, 'processing')}
                              className="px-2 py-1 rounded text-[10px] font-bold bg-[#2196F3]/15 text-[#2196F3] hover:bg-[#2196F3]/25 transition"
                              data-testid={`process-${w.id}`}>Process</button>
                          )}
                          {(w.status === 'pending' || w.status === 'processing') && (
                            <button onClick={() => handleUpdateStatus(w.id, 'completed')}
                              className="px-2 py-1 rounded text-[10px] font-bold bg-[#4CAF50]/15 text-[#4CAF50] hover:bg-[#4CAF50]/25 transition"
                              data-testid={`complete-${w.id}`}>Complete</button>
                          )}
                          {(w.status === 'pending' || w.status === 'processing') && (
                            <button onClick={() => handleUpdateStatus(w.id, 'failed')}
                              className="px-2 py-1 rounded text-[10px] font-bold bg-[#F44336]/15 text-[#F44336] hover:bg-[#F44336]/25 transition"
                              data-testid={`fail-${w.id}`}>Fail</button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
