import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { GoogleLogo, Eye, EyeSlash } from '@phosphor-icons/react';
import { toast } from 'sonner';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Login failed';
      setError(typeof errorMsg === 'string' ? errorMsg : 'Login failed');
      toast.error(typeof errorMsg === 'string' ? errorMsg : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center">
      {/* Purple-pink gradient background */}
      <div className="absolute inset-0" style={{ background: 'linear-gradient(180deg, #7C4DFF 0%, #9C27B0 30%, #E040FB 70%, #FF4081 100%)' }} />
      <div className="absolute inset-0 bg-black/50" />

      {/* Form */}
      <div className="relative z-10 w-full max-w-[420px] mx-auto px-6 py-12 text-center">
        {/* Logo */}
        <Link to="/" className="inline-block mb-10">
          <span className="text-3xl font-black tracking-[6px]" style={{ color: '#E040FB', textShadow: '0 0 20px rgba(224,64,251,0.3)' }}>
            KALMORI
          </span>
        </Link>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm text-left" data-testid="login-error">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5 text-left">
          <div>
            <label className="block text-gray-400 text-sm mb-1.5">Email Address</label>
            <input
              type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors"
              required data-testid="login-email-input"
            />
          </div>

          <div>
            <label className="block text-gray-400 text-sm mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors pr-10"
                required data-testid="login-password-input"
              />
              <button type="button" onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                data-testid="toggle-password-visibility"
              >
                {showPassword ? <EyeSlash className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <div className="flex justify-center pt-2">
            <button
              type="submit" disabled={loading}
              className="bg-[#E040FB] hover:brightness-110 text-white text-sm font-bold tracking-[1.5px] uppercase px-10 py-3 rounded-full transition-all min-w-[140px]"
              data-testid="login-submit-btn"
            >
              {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto" /> : 'LOG IN'}
            </button>
          </div>
        </form>

        <div className="mt-5">
          <Link to="/forgot-password" className="text-sm text-gray-400 hover:text-[#E040FB] underline transition-colors" data-testid="forgot-password-link">
            Forgot your password?
          </Link>
        </div>

        <div className="mt-4">
          <Link to="/register" className="text-sm text-[#E040FB] hover:brightness-125 transition-colors" data-testid="signup-link">
            I need an account
          </Link>
        </div>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-700" /></div>
          <div className="relative flex justify-center"><span className="px-4 bg-black/50 text-xs text-gray-500 backdrop-blur-sm">or</span></div>
        </div>

        <button type="button" onClick={handleGoogleLogin}
          className="w-full border border-gray-600 hover:border-gray-400 text-white py-3 rounded-full flex items-center justify-center gap-2 transition-all text-sm font-medium"
          data-testid="google-login-btn"
        >
          <GoogleLogo className="w-5 h-5" weight="bold" /> Continue with Google
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
