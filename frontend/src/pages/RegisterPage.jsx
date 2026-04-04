import React, { useState, useRef } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../App';
import { GoogleLogo, Eye, EyeSlash, CaretDown, Check, CheckCircle, WarningCircle, MusicNotes, ArrowRight, Plus, Gift } from '@phosphor-icons/react';
import { toast } from 'sonner';
import ReCAPTCHA from 'react-google-recaptcha';

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
  const [step, setStep] = useState(1);
  const [searchParams] = useSearchParams();
  const refCode = searchParams.get('ref') || '';

  // Step 1 fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [recaptchaToken, setRecaptchaToken] = useState(null);
  const recaptchaRef = useRef(null);

  // Step 2 fields
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [showCompany, setShowCompany] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [country, setCountry] = useState('');
  const [showCountryPicker, setShowCountryPicker] = useState(false);
  const [countrySearch, setCountrySearch] = useState('');
  const [address, setAddress] = useState('');
  const [address2, setAddress2] = useState('');
  const [showAddress2, setShowAddress2] = useState(false);
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [postCode, setPostCode] = useState('');
  const [phone, setPhone] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  // Password validation
  const pwChecks = {
    length: password.length >= 12,
    number: /\d/.test(password),
    capital: /[A-Z]/.test(password),
    noSpaces: !password.includes(' '),
  };
  const pwValid = pwChecks.length && pwChecks.number && pwChecks.capital && pwChecks.noSpaces;

  const filteredCountries = COUNTRIES.filter(c => c.toLowerCase().includes(countrySearch.toLowerCase()));

  const handleStep1 = (e) => {
    e.preventDefault();
    setError('');
    if (!email.trim()) { setError('Email is required'); return; }
    if (!pwValid) { setError('Password does not meet the requirements'); return; }
    if (!agreedToTerms) { setError('You must agree to the Terms & Conditions'); return; }
    if (!recaptchaToken && process.env.REACT_APP_RECAPTCHA_SITE_KEY) { setError('Please complete the reCAPTCHA verification'); return; }
    setStep(2);
  };

  const handleStep2 = async (e) => {
    e.preventDefault();
    setError('');
    if (!firstName.trim()) { setError('First name is required'); return; }
    if (!lastName.trim()) { setError('Last name is required'); return; }

    setLoading(true);
    try {
      await register({
        name: `${firstName} ${lastName}`,
        artist_name: `${firstName} ${lastName}`,
        email,
        password,
        user_role: 'artist',
        legal_name: `${firstName} ${lastName}`,
        company_name: companyName,
        country,
        state,
        town: city,
        address,
        address_2: address2,
        post_code: postCode,
        phone,
        recaptcha_token: recaptchaToken,
      });
      // Complete referral if code was used
      if (refCode) {
        try {
          const token = localStorage.getItem('token') || localStorage.getItem('access_token');
          await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/referral/complete`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: refCode }),
          });
        } catch (e) { /* Referral completion is best-effort */ }
      }
      toast.success('Account created!');
      navigate('/select-role');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed';
      setError(typeof msg === 'string' ? msg : 'Registration failed');
      toast.error(typeof msg === 'string' ? msg : 'Registration failed');
    } finally { setLoading(false); }
  };

  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/select-role';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const inputCls = "w-full bg-transparent border border-gray-600 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-[#0095FF] focus:ring-2 focus:ring-[#0095FF]/20 transition-all placeholder-gray-500";

  return (
    <div className="min-h-screen relative flex items-start justify-center overflow-y-auto">
      {/* Same gradient background as login */}
      <div className="absolute inset-0" style={{ background: 'linear-gradient(180deg, #7C4DFF 0%, #9C27B0 30%, #E040FB 70%, #FF4081 100%)' }} />
      <div className="absolute inset-0 bg-black/50" />

      <style>{`
        @keyframes shimmer-blue {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        .btn-animated-blue {
          background: linear-gradient(90deg, #0095FF, #7468F8, #0095FF, #7468F8);
          background-size: 300% 100%;
          animation: shimmer-blue 3s ease-in-out infinite;
        }
        .logo-animated-blue {
          background: linear-gradient(90deg, #0095FF, #7468F8, #0095FF, #7468F8);
          background-size: 300% 100%;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: shimmer-blue 3s ease-in-out infinite;
        }
      `}</style>

      <div className="relative z-10 w-full max-w-lg mx-auto px-4 py-10">
        {/* Referral Banner */}
        {refCode && (
          <div className="mb-4 bg-[#7C4DFF]/20 border border-[#7C4DFF]/40 rounded-xl p-3 text-center" data-testid="referral-banner">
            <p className="text-white text-sm font-medium">
              <Gift className="w-4 h-4 inline mr-1 text-[#E040FB]" />
              You were referred! Sign up to get a <strong className="text-[#E040FB]">free month of Rise</strong>
            </p>
          </div>
        )}
        {/* Step 1: Email + Password */}
        {step === 1 && (
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-6">
              <MusicNotes className="w-6 h-6 text-[#0095FF]" weight="fill" />
              <span className="text-sm font-black tracking-[4px] logo-animated-blue">KALMORI</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white mb-1">Sign up for free.</h1>
            <p className="text-gray-300 text-lg mb-8">Create your Kalmori account.</p>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-4 text-sm text-left" data-testid="register-error">{error}</div>
            )}

            <div className="bg-black/30 backdrop-blur-md rounded-2xl p-6 sm:p-8 text-left border border-white/10">
              <form onSubmit={handleStep1} className="space-y-5">
                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">Email</label>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                    className={inputCls} required data-testid="register-email-input" />
                </div>

                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">Password</label>
                  <div className="relative">
                    <input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)}
                      className={`${inputCls} pr-10`} required data-testid="register-password-input" />
                    <button type="button" onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                      data-testid="toggle-password-visibility">
                      {showPassword ? <EyeSlash className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-2" data-testid="password-requirements">
                  <div className="flex items-center gap-2">
                    <CheckCircle className={`w-5 h-5 flex-shrink-0 ${password.length > 0 && pwChecks.length && pwChecks.number && pwChecks.capital ? 'text-[#0095FF]' : 'text-gray-500'}`} weight="fill" />
                    <span className="text-sm font-semibold text-gray-300">Your Password must use:</span>
                  </div>
                  <ul className="ml-7 space-y-1">
                    <li className={`text-sm flex items-center gap-1.5 ${pwChecks.length ? 'text-[#0095FF]' : 'text-gray-500'}`}>
                      {pwChecks.length && <Check className="w-3 h-3" weight="bold" />} at least 12 characters
                    </li>
                    <li className={`text-sm flex items-center gap-1.5 ${pwChecks.number ? 'text-[#0095FF]' : 'text-gray-500'}`}>
                      {pwChecks.number && <Check className="w-3 h-3" weight="bold" />} at least 1 number
                    </li>
                    <li className={`text-sm flex items-center gap-1.5 ${pwChecks.capital ? 'text-[#0095FF]' : 'text-gray-500'}`}>
                      {pwChecks.capital && <Check className="w-3 h-3" weight="bold" />} at least 1 capital letter
                    </li>
                  </ul>
                  <div className="flex items-center gap-2 mt-2">
                    <WarningCircle className={`w-5 h-5 flex-shrink-0 ${password.length > 0 && !pwChecks.noSpaces ? 'text-red-500' : 'text-red-400'}`} weight="fill" />
                    <span className="text-sm font-semibold text-gray-300">Do NOT use spaces or a recently used password</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <button type="button" onClick={() => setAgreedToTerms(!agreedToTerms)}
                    className={`w-5 h-5 rounded border-2 flex-shrink-0 mt-0.5 flex items-center justify-center transition-all ${
                      agreedToTerms ? 'bg-[#0095FF] border-[#0095FF]' : 'border-gray-500 hover:border-gray-300'
                    }`} data-testid="terms-checkbox">
                    {agreedToTerms && <Check className="w-3.5 h-3.5 text-white" weight="bold" />}
                  </button>
                  <span className="text-sm text-gray-400 leading-relaxed">
                    I have read, understood, and agree to the{' '}
                    <Link to="/terms" className="text-[#0095FF] font-semibold hover:underline">Terms of Service</Link>,{' '}
                    <Link to="/privacy" className="text-[#0095FF] font-semibold hover:underline">Privacy Policy</Link>, and{' '}
                    <Link to="/agreement" className="text-[#0095FF] font-semibold hover:underline">Kalmori Artist Agreement</Link>, and I am at least 13 years old.
                  </span>
                </div>

                {process.env.REACT_APP_RECAPTCHA_SITE_KEY && (
                  <div className="flex justify-center" data-testid="recaptcha-container">
                    <ReCAPTCHA ref={recaptchaRef} sitekey={process.env.REACT_APP_RECAPTCHA_SITE_KEY}
                      onChange={(token) => setRecaptchaToken(token)} onExpired={() => setRecaptchaToken(null)}
                      theme="dark" size="normal" />
                  </div>
                )}

                <button type="submit"
                  className="w-full btn-animated-blue text-white text-base font-bold py-3.5 rounded-full transition-all active:scale-[0.98]"
                  data-testid="register-submit-btn">
                  Sign Up
                </button>
              </form>
            </div>

            <p className="mt-5 text-sm text-gray-400">
              Already have an account? <Link to="/login" className="text-[#0095FF] hover:underline font-semibold" data-testid="login-link">Log in</Link>
            </p>

            <div className="relative my-5">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-700" /></div>
              <div className="relative flex justify-center"><span className="px-4 bg-black/30 text-xs text-gray-500 backdrop-blur-sm">or</span></div>
            </div>

            <button type="button" onClick={handleGoogleLogin}
              className="w-full border border-gray-600 hover:border-[#0095FF] text-white py-3 rounded-full flex items-center justify-center gap-2 transition-all text-sm font-medium"
              data-testid="google-register-btn">
              <GoogleLogo className="w-5 h-5" weight="bold" /> Continue with Google
            </button>
          </div>
        )}

        {/* Step 2: Personal Details */}
        {step === 2 && (
          <div className="text-center">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <MusicNotes className="w-5 h-5 text-[#0095FF]" weight="fill" />
                <span className="text-xs font-black tracking-[4px] logo-animated-blue">KALMORI</span>
              </div>
              <button onClick={() => { setStep(1); setError(''); }} className="text-sm text-gray-400 hover:text-white transition-colors" data-testid="back-to-step1">
                Back
              </button>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-white mb-1">You're one step closer.</h1>
            <p className="text-gray-300 text-lg mb-8">Let's finish creating your account.</p>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-4 text-sm text-left" data-testid="register-error-step2">{error}</div>
            )}

            <div className="bg-black/30 backdrop-blur-md rounded-2xl p-6 sm:p-8 text-left border border-white/10">
              <form onSubmit={handleStep2} className="space-y-5">
                {/* First Name */}
                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">First name</label>
                  <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)}
                    className={inputCls} required data-testid="register-first-name" />
                </div>

                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">Last name</label>
                  <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)}
                    className={inputCls} required data-testid="register-last-name" />
                </div>

                {!showCompany ? (
                  <button type="button" onClick={() => setShowCompany(true)}
                    className="flex items-center gap-2 text-[#0095FF] text-sm font-semibold hover:underline"
                    data-testid="add-company-btn">
                    <div className="w-6 h-6 rounded-full bg-[#0095FF] flex items-center justify-center">
                      <Plus className="w-3.5 h-3.5 text-white" weight="bold" />
                    </div>
                    Add a company or record label
                  </button>
                ) : (
                  <div>
                    <label className="block text-gray-400 text-sm font-medium mb-1.5">Company / Record Label</label>
                    <input type="text" value={companyName} onChange={(e) => setCompanyName(e.target.value)}
                      className={inputCls} placeholder="Enter company or label name" data-testid="register-company" />
                  </div>
                )}

                <div className="relative">
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">Country of residence</label>
                  <button type="button" onClick={() => setShowCountryPicker(!showCountryPicker)}
                    className="w-full flex items-center justify-between bg-transparent border border-gray-600 rounded-lg px-4 py-3 text-left hover:border-[#0095FF] transition-colors"
                    data-testid="register-country-picker">
                    <span className={`text-sm ${country ? 'text-white' : 'text-gray-400'}`}>
                      {country || '- Select a Country -'}
                    </span>
                    <CaretDown className={`w-4 h-4 text-gray-400 transition-transform ${showCountryPicker ? 'rotate-180' : ''}`} />
                  </button>
                  {showCountryPicker && (
                    <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-2xl max-h-56 overflow-hidden">
                      <div className="p-2 border-b border-gray-100">
                        <input placeholder="Search country..." value={countrySearch} onChange={(e) => setCountrySearch(e.target.value)}
                          className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-black text-sm focus:outline-none focus:border-[#00BCD4]"
                          autoFocus data-testid="country-search-input" />
                      </div>
                      <div className="overflow-y-auto max-h-44">
                        {filteredCountries.map((c) => (
                          <button key={c} type="button"
                            onClick={() => { setCountry(c); setShowCountryPicker(false); setCountrySearch(''); }}
                            className={`w-full text-left px-4 py-2.5 text-sm hover:bg-[#E0F7FA] transition-colors ${
                              country === c ? 'text-[#00BCD4] bg-[#E0F7FA] font-medium' : 'text-gray-700'
                            }`}>{c}</button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Address */}
                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">Address</label>
                  <input type="text" value={address} onChange={(e) => setAddress(e.target.value)}
                    className={inputCls} data-testid="register-address" />
                </div>

                {/* Add another address line */}
                {!showAddress2 ? (
                  <button type="button" onClick={() => setShowAddress2(true)}
                    className="flex items-center gap-2 text-[#00BCD4] text-sm font-semibold hover:underline"
                    data-testid="add-address2-btn">
                    <div className="w-6 h-6 rounded-full bg-[#00BCD4] flex items-center justify-center">
                      <Plus className="w-3.5 h-3.5 text-white" weight="bold" />
                    </div>
                    Add another address line
                  </button>
                ) : (
                  <div>
                    <label className="block text-gray-400 text-sm font-medium mb-1.5">Address line 2</label>
                    <input type="text" value={address2} onChange={(e) => setAddress2(e.target.value)}
                      className={inputCls} data-testid="register-address2" />
                  </div>
                )}

                {/* City / Town */}
                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">City / Town</label>
                  <input type="text" value={city} onChange={(e) => setCity(e.target.value)}
                    className={inputCls} data-testid="register-city" />
                </div>

                {/* State / Province */}
                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">State / Province / Territory</label>
                  <input type="text" value={state} onChange={(e) => setState(e.target.value)}
                    className={inputCls} data-testid="register-state" />
                </div>

                {/* ZIP / Postal Code */}
                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">ZIP / Postal Code</label>
                  <input type="text" value={postCode} onChange={(e) => setPostCode(e.target.value)}
                    className={inputCls} data-testid="register-postcode" />
                </div>

                {/* Phone */}
                <div>
                  <label className="block text-gray-400 text-sm font-medium mb-1.5">Phone</label>
                  <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)}
                    className={inputCls} data-testid="register-phone" />
                </div>

                {/* Submit */}
                <button type="submit" disabled={loading}
                  className="w-full btn-animated-blue text-white text-base font-bold py-3.5 rounded-full transition-all active:scale-[0.98] flex items-center justify-center gap-2"
                  data-testid="complete-signup-btn">
                  {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <>Complete Sign-Up <ArrowRight className="w-5 h-5" /></>}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RegisterPage;
