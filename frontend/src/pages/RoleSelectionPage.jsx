import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API, useAuth } from '../App';
import { MusicNotes, Microphone, VinylRecord } from '@phosphor-icons/react';
import { toast } from 'sonner';

const RoleSelectionPage = () => {
  const navigate = useNavigate();
  const { user, setUser } = useAuth();
  const [loading, setLoading] = useState(false);

  const selectRole = async (role) => {
    setLoading(true);
    try {
      await axios.put(`${API}/auth/set-role`, { role }, { withCredentials: true });
      if (setUser && user) setUser({ ...user, user_role: role });
      toast.success(`Welcome, ${role === 'artist' ? 'Artist' : 'Label / Producer'}!`);
      navigate('/dashboard');
    } catch (err) {
      toast.error('Failed to set role');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0" style={{ background: 'linear-gradient(180deg, #1a1a2e 0%, #0a0a14 50%, #000 100%)' }} />
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSA2MCAwIEwgMCAwIDAgNjAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjAzKSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-40" />

      <div className="relative z-10 w-full max-w-lg mx-auto px-6 text-center" data-testid="role-selection-page">
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center justify-center gap-2 mb-6">
            <MusicNotes className="w-8 h-8 text-[#E040FB]" weight="fill" />
            <span className="text-xl font-black tracking-[4px] text-white">KALMORI</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-[#FFD700] leading-tight mb-3">
            How will you use Kalmori?
          </h1>
          <p className="text-gray-400 text-base">
            Choose your account type to get started
          </p>
        </div>

        {/* Role Buttons — stacked vertically */}
        <div className="space-y-4">
          <button
            onClick={() => selectRole('artist')}
            disabled={loading}
            className="w-full group relative overflow-hidden rounded-2xl border-2 border-[#FFD700]/30 hover:border-[#FFD700] transition-all duration-300"
            data-testid="role-artist-btn"
          >
            <div className="relative bg-[#111] hover:bg-[#1a1a1a] transition-colors px-8 py-7 flex items-center gap-5">
              <div className="w-16 h-16 rounded-xl bg-[#FFD700]/10 flex items-center justify-center flex-shrink-0 group-hover:bg-[#FFD700]/20 transition-colors">
                <Microphone className="w-8 h-8 text-[#FFD700]" weight="fill" />
              </div>
              <div className="text-left flex-1">
                <p className="text-xl font-bold text-[#FFD700]">I am an Artist</p>
                <p className="text-sm text-gray-400 mt-1">Distribute your music, track analytics, and grow your fanbase</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => selectRole('label_producer')}
            disabled={loading}
            className="w-full group relative overflow-hidden rounded-2xl border-2 border-[#FFD700]/30 hover:border-[#FFD700] transition-all duration-300"
            data-testid="role-label-producer-btn"
          >
            <div className="relative bg-[#111] hover:bg-[#1a1a1a] transition-colors px-8 py-7 flex items-center gap-5">
              <div className="w-16 h-16 rounded-xl bg-[#FFD700]/10 flex items-center justify-center flex-shrink-0 group-hover:bg-[#FFD700]/20 transition-colors">
                <VinylRecord className="w-8 h-8 text-[#FFD700]" weight="fill" />
              </div>
              <div className="text-left flex-1">
                <p className="text-xl font-bold text-[#FFD700]">I am a Label / Producer</p>
                <p className="text-sm text-gray-400 mt-1">Manage artists, distribute catalogs, and track royalties</p>
              </div>
            </div>
          </button>
        </div>

        {loading && (
          <div className="mt-6">
            <div className="w-6 h-6 border-2 border-[#FFD700] border-t-transparent rounded-full animate-spin mx-auto" />
          </div>
        )}
      </div>
    </div>
  );
};

export default RoleSelectionPage;
