import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { GoogleLogo, Envelope, Lock, User, MusicNotes, ArrowRight, Eye, EyeSlash, MapPin, Flag, Buildings, Hash, CaretDown } from '@phosphor-icons/react';
import { toast } from 'sonner';

const COUNTRIES = [
  'United States', 'United Kingdom', 'Canada', 'Australia', 'Nigeria', 'Ghana', 'South Africa',
  'Jamaica', 'Trinidad and Tobago', 'Barbados', 'Kenya', 'Tanzania', 'Uganda', 'India',
  'Germany', 'France', 'Brazil', 'Mexico', 'Japan', 'South Korea', 'Netherlands', 'Sweden',
  'Norway', 'Denmark', 'Italy', 'Spain', 'Portugal', 'Ireland', 'New Zealand', 'Philippines',
  'Colombia', 'Argentina', 'Chile', 'Peru', 'Dominican Republic', 'Puerto Rico', 'Haiti',
  'Cuba', 'Panama', 'Costa Rica', 'Ecuador', 'Venezuela', 'Bolivia', 'Paraguay', 'Uruguay',
  'Egypt', 'Morocco', 'Ethiopia', 'Cameroon', 'Senegal', 'Zimbabwe', 'Zambia', 'Mozambique',
  'Angola', 'Democratic Republic of Congo', 'Rwanda', 'Ivory Coast', 'Mali', 'Burkina Faso',
  'Sierra Leone', 'Liberia', 'Gambia', 'Guinea', 'Togo', 'Benin', 'Niger', 'Chad',
  'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan',
  'Bahamas', 'Bahrain', 'Bangladesh', 'Belarus', 'Belgium', 'Belize', 'Bhutan', 'Bosnia',
  'Botswana', 'Brunei', 'Bulgaria', 'Cambodia', 'China', 'Croatia', 'Cyprus', 'Czech Republic',
  'Estonia', 'Fiji', 'Finland', 'Georgia', 'Greece', 'Grenada', 'Guatemala', 'Guyana',
  'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'Indonesia', 'Iran', 'Iraq', 'Israel',
  'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Libya',
  'Lithuania', 'Luxembourg', 'Madagascar', 'Malaysia', 'Maldives', 'Malta', 'Mauritius',
  'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Myanmar', 'Namibia', 'Nepal', 'Nicaragua',
  'North Macedonia', 'Oman', 'Pakistan', 'Palestine', 'Poland', 'Qatar', 'Romania', 'Russia',
  'Saudi Arabia', 'Serbia', 'Singapore', 'Slovakia', 'Slovenia', 'Somalia', 'Sri Lanka',
  'Sudan', 'Suriname', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Thailand',
  'Tunisia', 'Turkey', 'Turkmenistan', 'Ukraine', 'United Arab Emirates', 'Uzbekistan',
  'Vietnam', 'Yemen'
].sort();

const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [legalName, setLegalName] = useState('');
  const [stageName, setStageName] = useState('');
  const [country, setCountry] = useState('');
  const [state, setState] = useState('');
  const [town, setTown] = useState('');
  const [postCode, setPostCode] = useState('');
  const [userRole, setUserRole] = useState('artist');
  const [showPassword, setShowPassword] = useState(false);
  const [showCountryPicker, setShowCountryPicker] = useState(false);
  const [countrySearch, setCountrySearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const filteredCountries = COUNTRIES.filter(c =>
    c.toLowerCase().includes(countrySearch.toLowerCase())
  );

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!legalName.trim()) { setError('Legal name is required'); return; }
    if (!email.trim()) { setError('Email is required'); return; }
    if (password.length < 6) { setError('Password must be at least 6 characters'); return; }
    if (password !== confirmPassword) { setError('Passwords do not match'); return; }

    setLoading(true);
    try {
      await register({
        name: legalName,
        artist_name: stageName || legalName,
        email,
        password,
        user_role: userRole,
        legal_name: legalName,
        country,
        state,
        town,
        post_code: postCode,
      });
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
      {/* Left side image - desktop only */}
      <div className="hidden lg:block lg:w-1/2 bg-cover bg-center" style={{ backgroundImage: 'url(https://images.pexels.com/photos/1763075/pexels-photo-1763075.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260)' }}>
        <div className="h-full w-full bg-gradient-to-l from-black to-transparent" />
      </div>

      {/* Registration form */}
      <div className="flex-1 flex items-start justify-center p-6 sm:p-8 overflow-y-auto">
        <div className="w-full max-w-md py-8">
          <Link to="/" className="flex items-center gap-2 mb-8">
            <span className="text-2xl font-black tracking-[4px] gradient-text">KALMORI</span>
          </Link>

          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Create account</h1>
          <p className="text-gray-400 mb-6">Start distributing your music today</p>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-5 text-sm" data-testid="register-error">
              {error}
            </div>
          )}

          {/* Role Toggle */}
          <div className="mb-6">
            <Label className="text-white mb-3 block text-sm">I am a</Label>
            <div className="flex gap-3">
              {['artist', 'producer'].map((role) => (
                <button
                  key={role}
                  type="button"
                  onClick={() => setUserRole(role)}
                  className={`flex-1 py-3 rounded-full text-sm font-bold tracking-[1px] uppercase transition-all ${
                    userRole === role
                      ? 'bg-[#E040FB] text-white shadow-lg shadow-[#E040FB]/20'
                      : 'bg-[#111] border border-white/10 text-gray-400 hover:border-white/30'
                  }`}
                  data-testid={`role-${role}-btn`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            {/* Legal Name & Stage Name */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="legalName" className="text-white mb-1.5 block text-sm">Legal Name *</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <Input
                    id="legalName" value={legalName} onChange={(e) => setLegalName(e.target.value)}
                    placeholder="Full legal name"
                    className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 h-11"
                    required data-testid="register-legal-name"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="stageName" className="text-white mb-1.5 block text-sm">Stage Name</Label>
                <div className="relative">
                  <MusicNotes className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <Input
                    id="stageName" value={stageName} onChange={(e) => setStageName(e.target.value)}
                    placeholder="Artist / producer name"
                    className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 h-11"
                    data-testid="register-stage-name"
                  />
                </div>
              </div>
            </div>

            {/* Email */}
            <div>
              <Label htmlFor="email" className="text-white mb-1.5 block text-sm">Email *</Label>
              <div className="relative">
                <Envelope className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input
                  id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="artist@example.com"
                  className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 h-11"
                  required data-testid="register-email-input"
                />
              </div>
            </div>

            {/* Country Picker */}
            <div className="relative">
              <Label htmlFor="country" className="text-white mb-1.5 block text-sm">Country</Label>
              <button
                type="button"
                onClick={() => setShowCountryPicker(!showCountryPicker)}
                className="w-full flex items-center gap-3 bg-[#111] border border-white/10 rounded-md px-3 h-11 text-left hover:border-white/20 transition-colors"
                data-testid="register-country-picker"
              >
                <Flag className="w-5 h-5 text-gray-500 flex-shrink-0" />
                <span className={`flex-1 text-sm ${country ? 'text-white' : 'text-gray-500'}`}>
                  {country || 'Select your country'}
                </span>
                <CaretDown className={`w-4 h-4 text-gray-500 transition-transform ${showCountryPicker ? 'rotate-180' : ''}`} />
              </button>

              {showCountryPicker && (
                <div className="absolute z-50 mt-1 w-full bg-[#111] border border-white/10 rounded-lg shadow-2xl max-h-60 overflow-hidden">
                  <div className="p-2 border-b border-white/10">
                    <Input
                      placeholder="Search country..."
                      value={countrySearch}
                      onChange={(e) => setCountrySearch(e.target.value)}
                      className="bg-[#0a0a0a] border-white/10 text-white placeholder:text-gray-500 h-9 text-sm"
                      autoFocus
                      data-testid="country-search-input"
                    />
                  </div>
                  <div className="overflow-y-auto max-h-48">
                    {filteredCountries.map((c) => (
                      <button
                        key={c} type="button"
                        onClick={() => { setCountry(c); setShowCountryPicker(false); setCountrySearch(''); }}
                        className={`w-full text-left px-4 py-2.5 text-sm hover:bg-white/5 transition-colors ${
                          country === c ? 'text-[#E040FB] bg-[#E040FB]/5' : 'text-gray-300'
                        }`}
                      >
                        {c}
                      </button>
                    ))}
                    {filteredCountries.length === 0 && (
                      <p className="px-4 py-3 text-sm text-gray-500">No countries found</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* State & Town */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="state" className="text-white mb-1.5 block text-sm">State / Province</Label>
                <div className="relative">
                  <Buildings className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <Input
                    id="state" value={state} onChange={(e) => setState(e.target.value)}
                    placeholder="State"
                    className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 h-11"
                    data-testid="register-state"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="town" className="text-white mb-1.5 block text-sm">Town / City</Label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <Input
                    id="town" value={town} onChange={(e) => setTown(e.target.value)}
                    placeholder="City"
                    className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 h-11"
                    data-testid="register-town"
                  />
                </div>
              </div>
            </div>

            {/* Post Code */}
            <div>
              <Label htmlFor="postCode" className="text-white mb-1.5 block text-sm">Post Code / ZIP</Label>
              <div className="relative">
                <Hash className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input
                  id="postCode" value={postCode} onChange={(e) => setPostCode(e.target.value)}
                  placeholder="12345"
                  className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 h-11"
                  data-testid="register-postcode"
                />
              </div>
            </div>

            {/* Password with show/hide */}
            <div>
              <Label htmlFor="password" className="text-white mb-1.5 block text-sm">Password *</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input
                  id="password" type={showPassword ? 'text' : 'password'}
                  value={password} onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 6 characters"
                  className="pl-10 pr-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 h-11"
                  required data-testid="register-password-input"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                  data-testid="toggle-password-visibility"
                >
                  {showPassword ? <EyeSlash className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <Label htmlFor="confirmPassword" className="text-white mb-1.5 block text-sm">Confirm Password *</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <Input
                  id="confirmPassword" type={showPassword ? 'text' : 'password'}
                  value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm password"
                  className="pl-10 bg-[#111] border-white/10 text-white placeholder:text-gray-500 h-11"
                  required data-testid="register-confirm-password-input"
                />
              </div>
            </div>

            <button
              type="submit" disabled={loading}
              className="w-full bg-[#E040FB] hover:brightness-110 py-3.5 rounded-full text-white font-bold tracking-[1px] flex items-center justify-center gap-2 transition-all mt-2"
              data-testid="register-submit-btn"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>Create Account <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/10" /></div>
            <div className="relative flex justify-center"><span className="px-4 bg-black text-sm text-gray-500">or</span></div>
          </div>

          <button type="button" onClick={handleGoogleLogin}
            className="w-full border-2 border-white/10 hover:bg-white/5 text-white py-3.5 rounded-full flex items-center justify-center gap-2 transition-all font-bold"
            data-testid="google-register-btn"
          >
            <GoogleLogo className="w-5 h-5" weight="bold" /> Continue with Google
          </button>

          <p className="mt-5 text-center text-sm text-gray-400">
            Already have an account? <Link to="/login" className="text-[#7C4DFF] hover:underline" data-testid="login-link">Sign in</Link>
          </p>

          <p className="mt-3 text-center text-xs text-gray-600">
            By creating an account you agree to our{' '}
            <Link to="/terms" className="text-gray-500 hover:text-gray-400 underline">Terms</Link> and{' '}
            <Link to="/privacy" className="text-gray-500 hover:text-gray-400 underline">Privacy Policy</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
