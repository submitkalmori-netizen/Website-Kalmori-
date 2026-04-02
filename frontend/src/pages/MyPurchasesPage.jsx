import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';
import { API, useAuth } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { toast } from 'sonner';
import { DownloadSimple, Play, Pause, MusicNotes, Receipt, Check, Clock, ShoppingBag, ArrowRight } from '@phosphor-icons/react';

const LICENSE_LABELS = {
  basic_lease: 'Basic Lease',
  premium_lease: 'Premium Lease',
  unlimited_lease: 'Unlimited Lease',
  exclusive: 'Exclusive Rights',
};

const LICENSE_COLORS = {
  basic_lease: '#7C4DFF',
  premium_lease: '#E040FB',
  unlimited_lease: '#FF4081',
  exclusive: '#FFD700',
};

const PurchaseCard = ({ purchase, onDownload, downloading, playingId, onTogglePlay, audioRef }) => {
  const beat = purchase.beat || {};
  const isPaid = purchase.payment_status === 'paid';
  const isPlaying = playingId === purchase.id;
  const licenseColor = LICENSE_COLORS[purchase.license_type] || '#7C4DFF';

  return (
    <div className="bg-[#111] border border-white/10 rounded-2xl p-5 transition-all hover:border-white/20" data-testid={`purchase-${purchase.id}`}>
      <div className="flex items-start gap-4">
        {/* Beat Cover / Play */}
        <div className="relative w-16 h-16 rounded-xl bg-[#1a1a1a] flex items-center justify-center flex-shrink-0 overflow-hidden">
          {beat.audio_url && isPaid ? (
            <button
              onClick={() => onTogglePlay(purchase)}
              className="w-full h-full flex items-center justify-center transition-all hover:bg-white/5"
              data-testid={`play-purchase-${purchase.id}`}
            >
              {isPlaying ? (
                <Pause className="w-6 h-6 text-white" weight="fill" />
              ) : (
                <Play className="w-6 h-6 text-white" weight="fill" />
              )}
            </button>
          ) : (
            <MusicNotes className="w-7 h-7 text-gray-600" />
          )}
          {isPlaying && (
            <div className="absolute bottom-1 left-1 right-1 flex items-end justify-center gap-0.5">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="w-1 rounded-full animate-pulse" style={{
                  backgroundColor: licenseColor,
                  height: `${4 + Math.random() * 8}px`,
                  animationDelay: `${i * 0.1}s`,
                  animationDuration: `${0.4 + Math.random() * 0.3}s`
                }} />
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-bold text-white truncate">{beat.title || purchase.beat_title}</h3>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            {beat.genre && <span className="text-xs text-gray-400">{beat.genre}</span>}
            {beat.bpm > 0 && <span className="text-xs text-gray-500">{beat.bpm} BPM</span>}
            {beat.key && <span className="text-xs text-gray-500">Key: {beat.key}</span>}
          </div>
          <div className="flex items-center gap-3 mt-2">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wider" style={{ backgroundColor: `${licenseColor}20`, color: licenseColor }}>
              {LICENSE_LABELS[purchase.license_type] || purchase.license_type}
            </span>
            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wider ${isPaid ? 'bg-[#4CAF50]/15 text-[#4CAF50]' : 'bg-[#FFD700]/15 text-[#FFD700]'}`}>
              {isPaid ? <Check className="w-3 h-3" weight="bold" /> : <Clock className="w-3 h-3" />}
              {isPaid ? 'PAID' : 'PENDING'}
            </span>
          </div>
        </div>

        {/* Price + Download */}
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <span className="text-lg font-bold text-white font-mono">${purchase.amount?.toFixed(2)}</span>
          {isPaid && beat.audio_url && (
            <button
              onClick={() => onDownload(purchase)}
              disabled={downloading === purchase.id}
              className="flex items-center gap-1.5 px-4 py-2 rounded-full text-white text-xs font-bold transition-all hover:brightness-110"
              style={{ backgroundColor: licenseColor }}
              data-testid={`download-purchase-${purchase.id}`}
            >
              {downloading === purchase.id ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <DownloadSimple className="w-4 h-4" weight="bold" />
              )}
              Download
            </button>
          )}
          {!isPaid && (
            <span className="text-xs text-gray-500">Awaiting payment</span>
          )}
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
        <span className="text-xs text-gray-500">
          {purchase.created_at ? new Date(purchase.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : ''}
        </span>
        <span className="text-xs text-gray-600 font-mono">{purchase.id}</span>
      </div>
    </div>
  );
};

export default function MyPurchasesPage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [purchases, setPurchases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(null);
  const [playingId, setPlayingId] = useState(null);
  const audioRef = useRef(null);

  useEffect(() => {
    fetchPurchases();
    // Handle purchase success return from Stripe
    const purchaseStatus = searchParams.get('purchase');
    const sessionId = searchParams.get('session_id');
    if (purchaseStatus === 'success' && sessionId) {
      verifyPurchase(sessionId);
    } else if (purchaseStatus === 'cancelled') {
      toast.error('Purchase was cancelled');
    }
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const fetchPurchases = async () => {
    try {
      const res = await axios.get(`${API}/purchases`, { withCredentials: true });
      setPurchases(res.data.purchases || []);
    } catch (err) {
      console.error('Failed to fetch purchases:', err);
    } finally {
      setLoading(false);
    }
  };

  const verifyPurchase = async (sessionId) => {
    try {
      await axios.get(`${API}/purchases/verify/${sessionId}`, { withCredentials: true });
      toast.success('Beat purchased successfully! You can now download your files.');
      fetchPurchases();
    } catch (err) {
      console.error('Verify failed:', err);
      toast.info('Purchase is being processed. It may take a moment to appear.');
      fetchPurchases();
    }
  };

  const handleDownload = async (purchase) => {
    setDownloading(purchase.id);
    try {
      const res = await axios.get(`${API}/purchases/${purchase.id}/download`, {
        withCredentials: true,
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      const contentDisposition = res.headers['content-disposition'];
      const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
      link.download = filenameMatch ? filenameMatch[1] : `${purchase.beat_title || 'beat'}.mp3`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Download started!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Download failed');
    } finally {
      setDownloading(null);
    }
  };

  const togglePlay = (purchase) => {
    if (playingId === purchase.id) {
      if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; }
      setPlayingId(null);
    } else {
      if (audioRef.current) { audioRef.current.pause(); }
      const beatId = purchase.beat_id;
      const audio = new Audio(`${API}/beats/${beatId}/stream`);
      audio.play().catch(e => console.log('Audio play failed:', e));
      audio.onended = () => setPlayingId(null);
      audioRef.current = audio;
      setPlayingId(purchase.id);
    }
  };

  const paidPurchases = purchases.filter(p => p.payment_status === 'paid');
  const pendingPurchases = purchases.filter(p => p.payment_status !== 'paid');

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8" data-testid="my-purchases-page">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">My Purchases</h1>
          <p className="text-gray-400 mt-1">Download your purchased beats and view transaction history</p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="card-kalmori p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#7C4DFF]/20 flex items-center justify-center">
                <ShoppingBag className="w-5 h-5 text-[#7C4DFF]" />
              </div>
              <div>
                <p className="text-2xl font-bold font-mono">{purchases.length}</p>
                <p className="text-sm text-gray-400">Total Purchases</p>
              </div>
            </div>
          </div>
          <div className="card-kalmori p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#4CAF50]/20 flex items-center justify-center">
                <Check className="w-5 h-5 text-[#4CAF50]" weight="bold" />
              </div>
              <div>
                <p className="text-2xl font-bold font-mono">{paidPurchases.length}</p>
                <p className="text-sm text-gray-400">Completed</p>
              </div>
            </div>
          </div>
          <div className="card-kalmori p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#E040FB]/20 flex items-center justify-center">
                <Receipt className="w-5 h-5 text-[#E040FB]" />
              </div>
              <div>
                <p className="text-2xl font-bold font-mono">
                  ${paidPurchases.reduce((sum, p) => sum + (p.amount || 0), 0).toFixed(2)}
                </p>
                <p className="text-sm text-gray-400">Total Spent</p>
              </div>
            </div>
          </div>
        </div>

        {/* Purchases List */}
        {purchases.length === 0 ? (
          <div className="card-kalmori p-12 text-center">
            <ShoppingBag className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">No purchases yet</h2>
            <p className="text-gray-400 mb-6">Browse our beat catalog and find the perfect instrumental for your next project.</p>
            <Link to="/instrumentals" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-[#7C4DFF] to-[#E040FB] text-white font-bold text-sm hover:brightness-110 transition-all" data-testid="browse-beats-btn">
              Browse Beats <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {paidPurchases.length > 0 && (
              <>
                <h2 className="text-sm font-bold text-[#4CAF50] tracking-[2px]">READY TO DOWNLOAD</h2>
                <div className="space-y-3">
                  {paidPurchases.map(p => (
                    <PurchaseCard key={p.id} purchase={p} onDownload={handleDownload}
                      downloading={downloading} playingId={playingId} onTogglePlay={togglePlay} audioRef={audioRef} />
                  ))}
                </div>
              </>
            )}
            {pendingPurchases.length > 0 && (
              <>
                <h2 className="text-sm font-bold text-[#FFD700] tracking-[2px] mt-8">PENDING</h2>
                <div className="space-y-3">
                  {pendingPurchases.map(p => (
                    <PurchaseCard key={p.id} purchase={p} onDownload={handleDownload}
                      downloading={downloading} playingId={playingId} onTogglePlay={togglePlay} audioRef={audioRef} />
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
