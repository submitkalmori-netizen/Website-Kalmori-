import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '../App';
import { CheckCircle, XCircle, SpinnerGap } from '@phosphor-icons/react';

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) { setStatus('error'); setMessage('No verification token found.'); return; }
    const verify = async () => {
      try {
        const res = await axios.get(`${API}/auth/verify-email?token=${token}`);
        setStatus('success');
        setMessage(res.data.message || 'Email verified successfully!');
        setTimeout(() => navigate('/dashboard'), 3000);
      } catch (err) {
        setStatus('error');
        setMessage(err.response?.data?.detail || 'Verification failed');
      }
    };
    verify();
  }, [token, navigate]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <div className="bg-[#111] border border-white/10 rounded-2xl p-10 max-w-md w-full text-center" data-testid="verify-email-page">
        {status === 'verifying' && (
          <>
            <div className="w-16 h-16 border-3 border-[#7C4DFF] border-t-transparent rounded-full animate-spin mx-auto mb-6" />
            <h1 className="text-xl font-bold text-white mb-2">Verifying Your Email</h1>
            <p className="text-gray-500 text-sm">Please wait...</p>
          </>
        )}
        {status === 'success' && (
          <>
            <CheckCircle className="w-16 h-16 text-[#1DB954] mx-auto mb-6" />
            <h1 className="text-xl font-bold text-white mb-2">Email Verified!</h1>
            <p className="text-gray-400 text-sm mb-4">{message}</p>
            <p className="text-gray-600 text-xs">Redirecting to dashboard...</p>
          </>
        )}
        {status === 'error' && (
          <>
            <XCircle className="w-16 h-16 text-[#FF6B6B] mx-auto mb-6" />
            <h1 className="text-xl font-bold text-white mb-2">Verification Failed</h1>
            <p className="text-gray-400 text-sm mb-6">{message}</p>
            <button onClick={() => navigate('/dashboard')}
              className="px-6 py-2.5 bg-[#7C4DFF] text-white rounded-lg text-sm font-bold hover:opacity-90"
              data-testid="go-dashboard-btn">Go to Dashboard</button>
          </>
        )}
      </div>
    </div>
  );
}
