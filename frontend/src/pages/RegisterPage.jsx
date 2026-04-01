import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { MusicNotes, GoogleLogo, Envelope, Lock, User, ArrowRight } from '@phosphor-icons/react';
import { toast } from 'sonner';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    artist_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const formatApiErrorDetail = (detail) => {
    if (detail == null) return "Something went wrong. Please try again.";
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail))
      return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
    if (detail && typeof detail.msg === "string") return detail.msg;
    return String(detail);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    
    try {
      await register({
        name: formData.name,
        artist_name: formData.artist_name || formData.name,
        email: formData.email,
        password: formData.password
      });
      toast.success('Account created successfully!');
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
      {/* Left Panel - Image */}
      <div 
        className="hidden lg:block lg:w-1/2 bg-cover bg-center"
        style={{
          backgroundImage: 'url(https://images.pexels.com/photos/196652/pexels-photo-196652.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940)'
        }}
      >
        <div className="h-full w-full bg-gradient-to-l from-[#0A0A0A] to-transparent" />
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <Link to="/" className="flex items-center gap-2 mb-12">
            <div className="w-8 h-8 bg-[#FF3B30] rounded-md flex items-center justify-center">
              <MusicNotes className="w-5 h-5 text-white" weight="bold" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">TuneDrop</span>
          </Link>

          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Create account</h1>
          <p className="text-[#A1A1AA] mb-8">Start distributing your music today</p>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md mb-6 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name" className="text-white mb-2 block">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#71717A]" />
                  <Input
                    id="name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="John Doe"
                    className="pl-10 bg-[#141414] border-white/10 text-white placeholder:text-[#71717A]"
                    required
                    data-testid="register-name-input"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="artist_name" className="text-white mb-2 block">Artist Name</Label>
                <div className="relative">
                  <MusicNotes className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#71717A]" />
                  <Input
                    id="artist_name"
                    name="artist_name"
                    type="text"
                    value={formData.artist_name}
                    onChange={handleChange}
                    placeholder="Stage name"
                    className="pl-10 bg-[#141414] border-white/10 text-white placeholder:text-[#71717A]"
                    data-testid="register-artist-input"
                  />
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="email" className="text-white mb-2 block">Email</Label>
              <div className="relative">
                <Envelope className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#71717A]" />
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="artist@example.com"
                  className="pl-10 bg-[#141414] border-white/10 text-white placeholder:text-[#71717A]"
                  required
                  data-testid="register-email-input"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-white mb-2 block">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#71717A]" />
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Min 6 characters"
                  className="pl-10 bg-[#141414] border-white/10 text-white placeholder:text-[#71717A]"
                  required
                  data-testid="register-password-input"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="confirmPassword" className="text-white mb-2 block">Confirm Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#71717A]" />
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Confirm password"
                  className="pl-10 bg-[#141414] border-white/10 text-white placeholder:text-[#71717A]"
                  required
                  data-testid="register-confirm-password-input"
                />
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white"
              disabled={loading}
              data-testid="register-submit-btn"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>Create Account <ArrowRight className="ml-2 w-4 h-4" /></>
              )}
            </Button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10" />
            </div>
            <div className="relative flex justify-center">
              <span className="px-4 bg-[#0A0A0A] text-sm text-[#71717A]">or</span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            className="w-full border-white/10 hover:bg-white/5 text-white"
            onClick={handleGoogleLogin}
            data-testid="google-register-btn"
          >
            <GoogleLogo className="mr-2 w-5 h-5" weight="bold" />
            Continue with Google
          </Button>

          <p className="mt-6 text-center text-sm text-[#A1A1AA]">
            Already have an account?{' '}
            <Link to="/login" className="text-[#FF3B30] hover:underline" data-testid="login-link">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
