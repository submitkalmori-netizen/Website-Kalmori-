import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { GoogleLogo, Eye, EyeSlash, CaretDown, Check } from '@phosphor-icons/react';
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
  const [legalName, setLegalName] = useState('');
  const [stageName, setStageName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [country, setCountry] = useState('');
  const [state, setState] = useState('');
  const [town, setTown] = useState('');
  const [postCode, setPostCode] = useState('');
  const [userRole, setUserRole] = useState('artist');
  const [showPassword, setShowPassword] = useState(false);
  const [showCountryPicker, setShowCountryPicker] = useState(false);
  const [countrySearch, setCountrySearch] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);
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

    if (!legalName.trim()) { setError('Name is required'); return; }
    if (!email.trim()) { setError('Email is required'); return; }
    if (password.length < 8) { setError('Password must be at least 8 characters long and contain at least 1 upper case letter, 1 number, and one special character'); return; }
    if (password !== confirmPassword) { setError('Passwords do not match'); return; }
    if (!agreedToTerms) { setError('You must agree to the Terms & Conditions'); return; }

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
    <div className="min-h-screen relative flex items-start justify-center overflow-y-auto">
      {/* Purple-pink gradient background */}
      <div className="absolute inset-0" style={{ background: 'linear-gradient(180deg, #7C4DFF 0%, #9C27B0 30%, #E040FB 70%, #FF4081 100%)' }} />
      <div className="absolute inset-0 bg-black/50" />

      <div className="relative z-10 w-full max-w-[460px] mx-auto px-6 py-10 text-center">
        {/* Header */}
        <h1 className="text-2xl sm:text-3xl font-bold text-white mb-1">
          Join <span style={{ color: '#E040FB' }}>Kalmori</span>
        </h1>
        <p className="text-gray-500 text-sm mb-6">Start distributing your music worldwide</p>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-5 text-sm text-left" data-testid="register-error">
            {error}
          </div>
        )}

        {/* Dark card container */}
        <div className="bg-[#0d0d0d] border border-gray-800 rounded-xl p-6 sm:p-8 text-left">
          {/* Role Toggle */}
          <div className="mb-5">
            <label className="block text-gray-400 text-sm mb-2">I am a</label>
            <div className="flex gap-3">
              {['artist', 'producer'].map((role) => (
                <button
                  key={role} type="button" onClick={() => setUserRole(role)}
                  className={`flex-1 py-2.5 rounded-full text-sm font-bold tracking-[1px] uppercase transition-all ${
                    userRole === role
                      ? 'bg-[#E040FB] text-white'
                      : 'bg-transparent border border-gray-600 text-gray-400 hover:border-gray-400'
                  }`}
                  data-testid={`role-${role}-btn`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-gray-400 text-sm mb-1.5">Name *</label>
              <input
                type="text" value={legalName} onChange={(e) => setLegalName(e.target.value)}
                className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors"
                required data-testid="register-legal-name"
              />
            </div>

            {/* Stage Name */}
            <div>
              <label className="block text-gray-400 text-sm mb-1.5">Stage / Artist Name</label>
              <input
                type="text" value={stageName} onChange={(e) => setStageName(e.target.value)}
                className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors"
                data-testid="register-stage-name"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-gray-400 text-sm mb-1.5">Email Address *</label>
              <input
                type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors"
                required data-testid="register-email-input"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-gray-400 text-sm mb-1.5">Password *</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors pr-10"
                  required data-testid="register-password-input"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                  data-testid="toggle-password-visibility"
                >
                  {showPassword ? <EyeSlash className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              <p className="text-gray-600 text-xs mt-1.5 leading-relaxed">
                Password must be at least 8 characters long and contain at least 1 upper case letter, 1 number, and one of these special characters: !&quot;#$%&amp;'()*+,-./:;&lt;=&gt;?@[\]^_`{'{|}'}~
              </p>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-gray-400 text-sm mb-1.5">Confirm Password *</label>
              <input
                type={showPassword ? 'text' : 'password'} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors"
                required data-testid="register-confirm-password-input"
              />
            </div>

            {/* Country Picker */}
            <div className="relative">
              <label className="block text-gray-400 text-sm mb-1.5">Country/Territory</label>
              <button
                type="button" onClick={() => setShowCountryPicker(!showCountryPicker)}
                className="w-full flex items-center justify-between bg-transparent border border-gray-600 rounded px-4 py-3 text-left hover:border-gray-400 transition-colors"
                data-testid="register-country-picker"
              >
                <span className={`text-sm ${country ? 'text-white' : 'text-gray-500'}`}>
                  {country || 'Choose Country/Territory'}
                </span>
                <CaretDown className={`w-4 h-4 text-gray-500 transition-transform ${showCountryPicker ? 'rotate-180' : ''}`} />
              </button>

              {showCountryPicker && (
                <div className="absolute z-50 mt-1 w-full bg-[#111] border border-gray-700 rounded-lg shadow-2xl max-h-56 overflow-hidden">
                  <div className="p-2 border-b border-gray-700">
                    <input
                      placeholder="Search country..."
                      value={countrySearch} onChange={(e) => setCountrySearch(e.target.value)}
                      className="w-full bg-[#0a0a0a] border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-[#E040FB]"
                      autoFocus data-testid="country-search-input"
                    />
                  </div>
                  <div className="overflow-y-auto max-h-44">
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

            {/* State & Town - side by side */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-gray-400 text-sm mb-1.5">State / Province</label>
                <input
                  type="text" value={state} onChange={(e) => setState(e.target.value)}
                  className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors"
                  data-testid="register-state"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-1.5">Town / City</label>
                <input
                  type="text" value={town} onChange={(e) => setTown(e.target.value)}
                  className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors"
                  data-testid="register-town"
                />
              </div>
            </div>

            {/* Post Code */}
            <div>
              <label className="block text-gray-400 text-sm mb-1.5">Post Code / ZIP</label>
              <input
                type="text" value={postCode} onChange={(e) => setPostCode(e.target.value)}
                className="w-full bg-transparent border border-gray-600 rounded px-4 py-3 text-white text-sm focus:outline-none focus:border-[#E040FB] transition-colors"
                data-testid="register-postcode"
              />
            </div>

            {/* Terms checkbox */}
            <div className="flex items-start gap-3 pt-1">
              <button
                type="button" onClick={() => setAgreedToTerms(!agreedToTerms)}
                className={`w-5 h-5 rounded border flex-shrink-0 mt-0.5 flex items-center justify-center transition-all ${
                  agreedToTerms ? 'bg-[#E040FB] border-[#E040FB]' : 'border-gray-600 hover:border-gray-400'
                }`}
                data-testid="terms-checkbox"
              >
                {agreedToTerms && <Check className="w-3.5 h-3.5 text-white" weight="bold" />}
              </button>
              <span className="text-sm text-gray-400">
                I Agree to the Kalmori{' '}
                <Link to="/terms" className="text-[#E040FB] hover:underline">Terms & Conditions</Link>
              </span>
            </div>

            {/* Submit */}
            <div className="flex justify-center pt-2">
              <button
                type="submit" disabled={loading}
                className="bg-[#E040FB] hover:brightness-110 text-white text-sm font-bold tracking-[1.5px] uppercase px-12 py-3 rounded-full transition-all min-w-[140px]"
                data-testid="register-submit-btn"
              >
                {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto" /> : 'SIGN UP'}
              </button>
            </div>
          </form>
        </div>

        <p className="mt-5 text-sm text-gray-400">
          Already have an account?{' '}
          <Link to="/login" className="text-[#E040FB] hover:underline" data-testid="login-link">Login</Link>
        </p>

        {/* Divider */}
        <div className="relative my-5">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-800" /></div>
          <div className="relative flex justify-center"><span className="px-4 bg-black text-xs text-gray-500">or</span></div>
        </div>

        <button type="button" onClick={handleGoogleLogin}
          className="w-full max-w-[460px] border border-gray-700 hover:border-gray-500 text-white py-3 rounded-full flex items-center justify-center gap-2 transition-all text-sm font-medium"
          data-testid="google-register-btn"
        >
          <GoogleLogo className="w-5 h-5" weight="bold" /> Continue with Google
        </button>
      </div>
    </div>
  );
};

export default RegisterPage;
