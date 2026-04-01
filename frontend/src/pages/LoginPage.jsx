import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { MusicNotes, GoogleLogo, Envelope, Lock, ArrowRight } from '@phosphor-icons/react';
import { toast } from 'sonner';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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
    <div className="min-h-screen bg-black flex">
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <Link to="/" className="flex items-center gap-2 mb-12">
            <span className="text-2xl font-black tracking-[4px] gradient-text">KALMORI</span>
          </Link>

          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Welcome back</h1>
          <p className="text-gray-400 mb-8">Sign in to manage your releases</p>

          {error && <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm">{error}</div>}

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <Label htmlFor="email" className="text-white mb-2 block">Email</Label>
              <div className="relative">
                <Envelope className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="artist@example.com" className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 focus:border-[#7C4DFF]" required data-testid="login-email-input" />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-white mb-2 block">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 focus:border-[#7C4DFF]" required data-testid="login-password-input" />
              </div>
            </div>

            <button type="submit" disabled={loading} className="w-full btn-animated py-3 rounded-lg text-white font-semibold flex items-center justify-center gap-2" data-testid="login-submit-btn">
              {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <>Sign In <ArrowRight className="w-4 h-4" /></>}
            </button>
          </form>

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/10" /></div>
            <div className="relative flex justify-center"><span className="px-4 bg-black text-sm text-gray-500">or continue with</span></div>
          </div>

          <button type="button" onClick={handleGoogleLogin} className="w-full border border-white/10 hover:bg-white/5 text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors" data-testid="google-login-btn">
            <GoogleLogo className="w-5 h-5" weight="bold" /> Continue with Google
          </button>

          <p className="mt-8 text-center text-sm text-gray-400">
            Don't have an account? <Link to="/register" className="text-[#7C4DFF] hover:underline" data-testid="signup-link">Sign up</Link>
          </p>
        </div>
      </div>

      <div className="hidden lg:block lg:w-1/2 bg-cover bg-center" style={{ backgroundImage: 'url(https://images.pexels.com/photos/1644616/pexels-photo-1644616.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260)' }}>
        <div className="h-full w-full bg-gradient-to-r from-black to-transparent" />
      </div>
    </div>
  );
};

export default LoginPage;
