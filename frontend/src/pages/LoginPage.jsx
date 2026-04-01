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

  const formatApiErrorDetail = (detail) => {
    if (detail == null) return "Something went wrong. Please try again.";
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail))
      return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
    if (detail && typeof detail.msg === "string") return detail.msg;
    return String(detail);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err) {
      const errorMsg = formatApiErrorDetail(err.response?.data?.detail) || err.message;
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] flex">
      {/* Left Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <Link to="/" className="flex items-center gap-2 mb-12">
            <div className="w-8 h-8 bg-[#FF3B30] rounded-md flex items-center justify-center">
              <MusicNotes className="w-5 h-5 text-white" weight="bold" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">TuneDrop</span>
          </Link>

          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Welcome back</h1>
          <p className="text-[#A1A1AA] mb-8">Sign in to manage your releases</p>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md mb-6 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <Label htmlFor="email" className="text-white mb-2 block">Email</Label>
              <div className="relative">
                <Envelope className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#71717A]" />
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="artist@example.com"
                  className="pl-10 bg-[#141414] border-white/10 text-white placeholder:text-[#71717A] focus:border-[#FF3B30] focus:ring-[#FF3B30]/20"
                  required
                  data-testid="login-email-input"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-white mb-2 block">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#71717A]" />
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="pl-10 bg-[#141414] border-white/10 text-white placeholder:text-[#71717A] focus:border-[#FF3B30] focus:ring-[#FF3B30]/20"
                  required
                  data-testid="login-password-input"
                />
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white"
              disabled={loading}
              data-testid="login-submit-btn"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>Sign In <ArrowRight className="ml-2 w-4 h-4" /></>
              )}
            </Button>
          </form>

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10" />
            </div>
            <div className="relative flex justify-center">
              <span className="px-4 bg-[#0A0A0A] text-sm text-[#71717A]">or continue with</span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            className="w-full border-white/10 hover:bg-white/5 text-white"
            onClick={handleGoogleLogin}
            data-testid="google-login-btn"
          >
            <GoogleLogo className="mr-2 w-5 h-5" weight="bold" />
            Continue with Google
          </Button>

          <p className="mt-8 text-center text-sm text-[#A1A1AA]">
            Don't have an account?{' '}
            <Link to="/register" className="text-[#FF3B30] hover:underline" data-testid="signup-link">
              Sign up
            </Link>
          </p>
        </div>
      </div>

      {/* Right Panel - Image */}
      <div 
        className="hidden lg:block lg:w-1/2 bg-cover bg-center"
        style={{
          backgroundImage: 'url(https://images.pexels.com/photos/5749200/pexels-photo-5749200.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940)'
        }}
      >
        <div className="h-full w-full bg-gradient-to-r from-[#0A0A0A] to-transparent" />
      </div>
    </div>
  );
};

export default LoginPage;
