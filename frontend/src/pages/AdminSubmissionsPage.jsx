import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import AdminLayout from '../components/AdminLayout';
import { CheckCircle, XCircle, Clock, Eye, CaretLeft, CaretRight, FunnelSimple, ClipboardText } from '@phosphor-icons/react';
import { Button } from '../components/ui/button';

const AdminSubmissionsPage = () => {
  const [submissions, setSubmissions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedSub, setSelectedSub] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [reviewNotes, setReviewNotes] = useState('');
  const [reviewing, setReviewing] = useState(false);

  const fetchSubmissions = async (p = 1, status = '') => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: p, limit: 15 });
      if (status) params.append('status', status);
      const res = await axios.get(`${API}/admin/submissions?${params}`);
      setSubmissions(res.data.submissions);
      setTotal(res.data.total);
      setPages(res.data.pages);
      setPage(p);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchSubmissions(1, filter); }, [filter]);

  const openDetail = async (releaseId) => {
    setSelectedSub(releaseId);
    setDetailLoading(true);
    try {
      const res = await axios.get(`${API}/admin/submissions/${releaseId}`);
      setDetail(res.data);
    } catch (err) { console.error(err); }
    finally { setDetailLoading(false); }
  };

  const handleReview = async (action) => {
    if (!selectedSub) return;
    setReviewing(true);
    try {
      await axios.put(`${API}/admin/submissions/${selectedSub}/review`, {
        action,
        notes: reviewNotes || null
      });
      setSelectedSub(null);
      setDetail(null);
      setReviewNotes('');
      fetchSubmissions(page, filter);
    } catch (err) { console.error(err); alert(err.response?.data?.detail || 'Review failed'); }
    finally { setReviewing(false); }
  };

  const statusColor = (s) => {
    if (s === 'pending_review') return 'bg-[#FFD700]/10 text-[#FFD700]';
    if (s === 'approved') return 'bg-[#4CAF50]/10 text-[#4CAF50]';
    if (s === 'rejected') return 'bg-[#E53935]/10 text-[#E53935]';
    return 'bg-gray-600/20 text-gray-400';
  };

  const statusIcon = (s) => {
    if (s === 'pending_review') return <Clock className="w-4 h-4 text-[#FFD700]" />;
    if (s === 'approved') return <CheckCircle className="w-4 h-4 text-[#4CAF50]" />;
    if (s === 'rejected') return <XCircle className="w-4 h-4 text-[#E53935]" />;
    return null;
  };

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="admin-submissions">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Ingestion <span className="text-[#E53935]">Queue</span></h1>
            <p className="text-gray-400 mt-1">Review and approve artist submissions</p>
          </div>
          <div className="flex items-center gap-2" data-testid="submission-filters">
            <FunnelSimple className="w-4 h-4 text-gray-400" />
            {['', 'pending_review', 'approved', 'rejected'].map((f) => (
              <button key={f} onClick={() => setFilter(f)}
                className={`text-xs px-3 py-1.5 rounded-full transition-all ${filter === f ? 'bg-[#E53935] text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
                data-testid={`filter-${f || 'all'}`}>
                {f ? f.replace('_', ' ') : 'All'}
              </button>
            ))}
          </div>
        </div>

        <div className="card-kalmori overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12"><div className="w-6 h-6 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" /></div>
          ) : submissions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <ClipboardText className="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <p>No submissions {filter ? `with status "${filter.replace('_', ' ')}"` : ''}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="submissions-table">
                <thead>
                  <tr className="border-b border-white/10 bg-white/5">
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Release</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Artist</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Type</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Tracks</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Status</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Submitted</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {submissions.map((sub) => (
                    <tr key={sub.release_id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4 text-sm font-medium">{sub.release_title}</td>
                      <td className="py-3 px-4 text-sm text-gray-400">{sub.artist_name}</td>
                      <td className="py-3 px-4 text-sm text-gray-400 capitalize">{sub.release_type}</td>
                      <td className="py-3 px-4 text-sm text-gray-400">{sub.track_count}</td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${statusColor(sub.status)}`}>
                          {statusIcon(sub.status)} {sub.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs text-gray-500">{new Date(sub.submitted_at).toLocaleDateString()}</td>
                      <td className="py-3 px-4">
                        <button onClick={() => openDetail(sub.release_id)}
                          className="text-xs text-[#7C4DFF] hover:underline flex items-center gap-1"
                          data-testid={`review-btn-${sub.release_id}`}>
                          <Eye className="w-4 h-4" /> Review
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {pages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-white/10">
              <p className="text-xs text-gray-500">{total} total submissions</p>
              <div className="flex items-center gap-2">
                <button onClick={() => fetchSubmissions(page - 1, filter)} disabled={page <= 1} className="p-1 text-gray-400 hover:text-white disabled:opacity-30"><CaretLeft className="w-5 h-5" /></button>
                <span className="text-sm text-gray-400">Page {page} of {pages}</span>
                <button onClick={() => fetchSubmissions(page + 1, filter)} disabled={page >= pages} className="p-1 text-gray-400 hover:text-white disabled:opacity-30"><CaretRight className="w-5 h-5" /></button>
              </div>
            </div>
          )}
        </div>

        {/* Review Modal */}
        {selectedSub && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="review-modal">
            <div className="absolute inset-0 bg-black/70" onClick={() => { setSelectedSub(null); setDetail(null); setReviewNotes(''); }} />
            <div className="relative bg-[#111] border border-white/10 rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              {detailLoading ? (
                <div className="flex items-center justify-center py-16"><div className="w-6 h-6 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" /></div>
              ) : detail ? (
                <div className="p-6 space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold">Review Submission</h2>
                    <span className={`text-xs px-2 py-1 rounded-full ${statusColor(detail.submission.status)}`}>{detail.submission.status.replace('_', ' ')}</span>
                  </div>

                  {/* Release Info */}
                  <div className="bg-white/5 p-4 rounded-lg space-y-2">
                    <h3 className="font-medium text-sm text-gray-300">Release Details</h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div><span className="text-gray-500">Title:</span> <span className="ml-2">{detail.release?.title}</span></div>
                      <div><span className="text-gray-500">Type:</span> <span className="ml-2 capitalize">{detail.release?.release_type}</span></div>
                      <div><span className="text-gray-500">Genre:</span> <span className="ml-2">{detail.release?.genre}</span></div>
                      <div><span className="text-gray-500">Release Date:</span> <span className="ml-2">{detail.release?.release_date}</span></div>
                      <div><span className="text-gray-500">UPC:</span> <span className="ml-2 font-mono">{detail.release?.upc}</span></div>
                      <div><span className="text-gray-500">Explicit:</span> <span className="ml-2">{detail.release?.explicit ? 'Yes' : 'No'}</span></div>
                    </div>
                  </div>

                  {/* Artist Info */}
                  <div className="bg-white/5 p-4 rounded-lg space-y-2">
                    <h3 className="font-medium text-sm text-gray-300">Artist</h3>
                    <div className="text-sm">
                      <span className="text-gray-500">Name:</span> <span className="ml-2">{detail.artist?.artist_name || detail.artist?.name}</span>
                      <br />
                      <span className="text-gray-500">Email:</span> <span className="ml-2">{detail.artist?.email}</span>
                      <br />
                      <span className="text-gray-500">Plan:</span> <span className="ml-2 capitalize">{detail.artist?.plan}</span>
                    </div>
                  </div>

                  {/* Tracks */}
                  <div className="bg-white/5 p-4 rounded-lg space-y-2">
                    <h3 className="font-medium text-sm text-gray-300">Tracks ({detail.tracks?.length || 0})</h3>
                    {detail.tracks?.length > 0 ? (
                      <div className="space-y-2">
                        {detail.tracks.map((t, i) => (
                          <div key={t.id} className="flex items-center justify-between text-sm p-2 bg-white/5 rounded">
                            <span>{t.track_number}. {t.title}</span>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span className="font-mono">{t.isrc}</span>
                              <span className={t.audio_url ? 'text-[#4CAF50]' : 'text-[#E53935]'}>{t.audio_url ? 'Audio uploaded' : 'No audio'}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">No tracks</p>
                    )}
                  </div>

                  {/* Review Action */}
                  {detail.submission.status === 'pending_review' && (
                    <div className="space-y-3 pt-2 border-t border-white/10">
                      <label className="block text-sm text-gray-400">Review Notes (optional)</label>
                      <textarea value={reviewNotes} onChange={(e) => setReviewNotes(e.target.value)}
                        className="w-full p-3 rounded-lg text-sm resize-none h-20" placeholder="Add notes about this submission..."
                        data-testid="review-notes-input" />
                      <div className="flex gap-3">
                        <Button onClick={() => handleReview('approve')} disabled={reviewing}
                          className="flex-1 bg-[#4CAF50] hover:bg-[#45a049] text-white" data-testid="approve-btn">
                          <CheckCircle className="w-4 h-4 mr-2" /> {reviewing ? 'Processing...' : 'Approve'}
                        </Button>
                        <Button onClick={() => handleReview('reject')} disabled={reviewing}
                          className="flex-1 bg-[#E53935] hover:bg-[#d32f2f] text-white" data-testid="reject-btn">
                          <XCircle className="w-4 h-4 mr-2" /> {reviewing ? 'Processing...' : 'Reject'}
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Already reviewed */}
                  {detail.submission.status !== 'pending_review' && (
                    <div className="p-4 bg-white/5 rounded-lg text-sm">
                      <p className="text-gray-400">Reviewed on {new Date(detail.submission.reviewed_at).toLocaleString()}</p>
                      {detail.submission.review_notes && <p className="mt-1 text-gray-300">Notes: {detail.submission.review_notes}</p>}
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminSubmissionsPage;
