import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { GoogleLogo, Envelope, Lock, User, MusicNotes, ArrowRight } from '@phosphor-icons/react';
import { toast } from 'sonner';

const RegisterPage = () => {
  const [formData, setFormData] = useState({ name: '', artist_name: '', email: '', password: '', confirmPassword: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    if (formData.password !== formData.confirmPassword) { setError('Passwords do not match'); return; }
    if (formData.password.length < 6) { setError('Password must be at least 6 characters'); return; }
    setLoading(true);
    try {
      await register({ name: formData.name, artist_name: formData.artist_name || formData.name, email: formData.email, password: formData.password });
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Registration failed';
      setError(typeof errorMsg === 'string' ? errorMsg : 'Registration failed');
      toast.error(typeof errorMsg === 'string' ? errorMsg : 'Registration failed');
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
      <div className="hidden lg:block lg:w-1/2 bg-cover bg-center" style={{ backgroundImage: 'url(https://images.pexels.com/photos/1763075/pexels-photo-1763075.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260)' }}>
        <div className="h-full w-full bg-gradient-to-l from-black to-transparent" />
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <Link to="/" className="flex items-center gap-2 mb-12">
            <span className="text-2xl font-black tracking-[4px] gradient-text">KALMORI</span>
          </Link>

          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Create account</h1>
          <p className="text-gray-400 mb-8">Start distributing your music today</p>

          {error && <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm">{error}</div>}

          <form onSubmit={handleRegister} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name" className="text-white mb-2 block">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <Input id="name" name="name" type="text" value={formData.name} onChange={handleChange} placeholder="John Doe" className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500" required data-testid="register-name-input" />
                </div>
              </div>
              <div>
                <Label htmlFor="artist_name" className="text-white mb-2 block">Artist Name</Label>
                <div className="relative">
                  <MusicNotes className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <Input id="artist_name" name="artist_name" type="text" value={formData.artist_name} onChange={handleChange} placeholder="Stage name" className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500" data-testid="register-artist-input" />
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="email" className="text-white mb-2 block">Email</Label>
              <div className="relative">
                <Envelope className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input id="email" name="email" type="email" value={formData.email} onChange={handleChange} placeholder="artist@example.com" className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500" required data-testid="register-email-input" />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-white mb-2 block">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input id="password" name="password" type="password" value={formData.password} onChange={handleChange} placeholder="Min 6 characters" className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500" required data-testid="register-password-input" />
              </div>
            </div>

            <div>
              <Label htmlFor="confirmPassword" className="text-white mb-2 block">Confirm Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input id="confirmPassword" name="confirmPassword" type="password" value={formData.confirmPassword} onChange={handleChange} placeholder="Confirm password" className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500" required data-testid="register-confirm-password-input" />
              </div>
            </div>

            <button type="submit" disabled={loading} className="w-full btn-animated py-3 rounded-lg text-white font-semibold flex items-center justify-center gap-2" data-testid="register-submit-btn">
              {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <>Create Account <ArrowRight className="w-4 h-4" /></>}
            </button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/10" /></div>
            <div className="relative flex justify-center"><span className="px-4 bg-black text-sm text-gray-500">or</span></div>
          </div>

          <button type="button" onClick={handleGoogleLogin} className="w-full border border-white/10 hover:bg-white/5 text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors" data-testid="google-register-btn">
            <GoogleLogo className="w-5 h-5" weight="bold" /> Continue with Google
          </button>

          <p className="mt-6 text-center text-sm text-gray-400">
            Already have an account? <Link to="/login" className="text-[#7C4DFF] hover:underline" data-testid="login-link">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
