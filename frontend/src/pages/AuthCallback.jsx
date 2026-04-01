import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';

const AuthCallback = () => {
  const { processGoogleSession } = useAuth();
  const navigate = useNavigate();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Prevent double processing in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processSession = async () => {
      const hash = window.location.hash;
      const sessionIdMatch = hash.match(/session_id=([^&]+)/);
      
      if (sessionIdMatch) {
        const sessionId = sessionIdMatch[1];
        try {
          await processGoogleSession(sessionId);
          // Clear the hash and navigate to dashboard
          window.history.replaceState(null, '', window.location.pathname);
          navigate('/dashboard', { replace: true });
        } catch (error) {
          console.error('Auth callback error:', error);
          navigate('/login', { replace: true });
        }
      } else {
        navigate('/login', { replace: true });
      }
    };

    processSession();
  }, [processGoogleSession, navigate]);

  return (
    <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-2 border-[#FF3B30] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-white">Completing sign in...</p>
      </div>
    </div>
  );
};

export default AuthCallback;
