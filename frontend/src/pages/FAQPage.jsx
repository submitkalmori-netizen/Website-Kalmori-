import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { CaretDown, MusicNote, CurrencyDollar, Gear, ShieldCheck, Users, ChartLineUp, Headphones, Lightning, Rocket, Crown } from '@phosphor-icons/react';

const faqSections = [
  {
    title: 'Getting Started',
    icon: <Lightning className="w-5 h-5" />,
    color: '#7C4DFF',
    items: [
      {
        q: 'What is Kalmori?',
        a: 'Kalmori is an AI-powered music distribution service that helps artists, producers, and labels distribute their music to 150+ streaming platforms worldwide including Spotify, Apple Music, YouTube Music, Amazon Music, TikTok, and more.'
      },
      {
        q: 'Who can use Kalmori?',
        a: 'Anyone involved in music creation and distribution. We serve three account types: Artists (who create and release music), Producers (who create beats and instrumentals for licensing), and Labels (who manage rosters of artists and their catalogs).'
      },
      {
        q: 'How do I create an account?',
        a: 'Click "Get Started" on the homepage, fill in your details, and select your account type (Artist, Producer, or Label). You can start on the Free plan immediately with no credit card required.'
      },
      {
        q: 'Can I switch my account type later?',
        a: 'Your account type (Artist, Producer, Label) is set during onboarding. If you need to change it, contact our support team and we will assist you.'
      },
    ]
  },
  {
    title: 'Subscription Plans',
    icon: <CurrencyDollar className="w-5 h-5" />,
    color: '#FFD700',
    items: [
      {
        q: 'What plans does Kalmori offer?',
        a: 'We offer three plans:\n\nFree Plan ($0) — Unlimited releases with no upfront cost. Kalmori keeps 20% of your streaming revenue. Includes basic analytics and standard support.\n\nRise Plan ($24.99/release) — Pay per single release. Kalmori keeps only 5% of your revenue. Includes advanced analytics, fan analytics, beat marketplace, in-app messaging, goal tracking, and priority support.\n\nPro Plan ($49.99/month) — Albums and singles with unlimited releases. You keep 100% of your royalties. Includes AI Release Strategy, revenue exports, YouTube Content ID, Spotify Canvas, pre-save campaigns, collaborations, royalty splits, and a dedicated account manager.'
      },
      {
        q: 'What does "Kalmori keeps 20%" mean on the Free plan?',
        a: 'On the Free plan, there is no upfront cost to distribute your music. Instead, Kalmori takes 20% of the streaming royalties your music earns. For example, if your song earns $100 in royalties, you receive $80 and Kalmori keeps $20. This allows anyone to start distributing music with zero investment.'
      },
      {
        q: 'What does "pay per release" mean on the Rise plan?',
        a: 'On the Rise plan, you pay $24.99 each time you release a single. There is no monthly subscription fee. Kalmori only keeps 5% of your streaming revenue, so you keep significantly more of your earnings compared to the Free plan.'
      },
      {
        q: 'Can I release albums on the Rise plan?',
        a: 'The Rise plan supports single releases only. If you want to release albums or EPs, you will need to upgrade to the Pro plan, which supports all release types (singles, EPs, and albums) with unlimited releases.'
      },
      {
        q: 'What makes the Pro plan worth it?',
        a: 'The Pro plan is designed for serious artists and labels who want maximum control. You keep 100% of your royalties (Kalmori takes 0%), get unlimited album and single releases, AI-powered release strategies, revenue exports, YouTube Content ID, Spotify Canvas uploads, pre-save campaigns, collaboration tools, royalty splits, and a dedicated account manager.'
      },
      {
        q: 'Can I upgrade or downgrade my plan?',
        a: 'Yes! You can upgrade or downgrade at any time from the Pricing page. If you upgrade, you get immediate access to the new features. If you downgrade, you will retain access until the end of your current billing period.'
      },
      {
        q: 'Is there a free trial for paid plans?',
        a: 'We do not offer free trials, but the Free plan lets you distribute unlimited music at no upfront cost. You can try the platform risk-free and upgrade when you are ready for more features and lower revenue share.'
      },
    ]
  },
  {
    title: 'Distribution & Releases',
    icon: <MusicNote className="w-5 h-5" />,
    color: '#E040FB',
    items: [
      {
        q: 'How do I release my music?',
        a: 'Go to your Dashboard, click "New Release," fill in the release details (title, artwork, genre), upload your tracks, select which stores to distribute to, and submit for review. Our team reviews submissions within 24-48 hours.'
      },
      {
        q: 'What streaming platforms does Kalmori distribute to?',
        a: 'We distribute to 150+ platforms including Spotify, Apple Music, YouTube Music, Amazon Music, TikTok, Tidal, Deezer, SoundCloud, Pandora, iHeartRadio, and many more.'
      },
      {
        q: 'How long does it take for my music to go live?',
        a: 'After your release is approved by our team (24-48 hours), it typically takes 3-7 business days for your music to appear on all streaming platforms. Some platforms are faster than others.'
      },
      {
        q: 'What audio formats are accepted?',
        a: 'We accept WAV and FLAC files at 16-bit/44.1kHz or higher quality. MP3 files are not recommended for distribution as they may be rejected by some platforms.'
      },
      {
        q: 'Do I get ISRC and UPC codes?',
        a: 'Yes! Kalmori provides free ISRC codes for every track and UPC codes for every release on all plans. These are required by streaming platforms and we handle this automatically.'
      },
      {
        q: 'Can I take down a release?',
        a: 'Yes. You can request a takedown from your release dashboard. The removal process takes 3-7 business days across all platforms.'
      },
    ]
  },
  {
    title: 'Revenue & Royalties',
    icon: <ChartLineUp className="w-5 h-5" />,
    color: '#22C55E',
    items: [
      {
        q: 'How do royalties work?',
        a: 'When your music is streamed on platforms like Spotify or Apple Music, those platforms pay royalties. Kalmori collects these royalties and deposits them into your Kalmori wallet, minus the revenue share based on your plan (20% for Free, 5% for Rise, 0% for Pro).'
      },
      {
        q: 'When do I get paid?',
        a: 'Royalties are typically processed monthly. Streaming platforms report earnings with a 2-3 month delay (this is standard across the industry). Once funds are in your wallet, you can withdraw at any time.'
      },
      {
        q: 'What is the minimum withdrawal amount?',
        a: 'The minimum withdrawal amount is $25. You can withdraw via bank transfer or PayPal.'
      },
      {
        q: 'Can I see detailed analytics of my streams?',
        a: 'Yes! All plans include basic analytics (total streams, earnings, daily breakdown). Rise and Pro plans include advanced analytics with fan demographics, geographic breakdown, platform comparison, and trending reports.'
      },
      {
        q: 'How does the revenue calculator work?',
        a: 'The revenue calculator (available on Rise and Pro plans) lets you estimate your earnings based on stream counts across different platforms. It accounts for your plan\'s revenue share to show your actual take-home amount.'
      },
    ]
  },
  {
    title: 'Features & Tools',
    icon: <Gear className="w-5 h-5" />,
    color: '#0095FF',
    items: [
      {
        q: 'What is the AI Release Strategy?',
        a: 'Available on the Pro plan, AI Release Strategy uses artificial intelligence to analyze your music and audience to recommend the best release date, target markets, playlist pitching strategies, and promotional tactics to maximize your reach.'
      },
      {
        q: 'What is the Beat Marketplace?',
        a: 'The Beat Marketplace (Rise and Pro plans) is where producers can list beats and instrumentals for sale, and artists can browse and purchase beats for their projects. Producers earn revenue from each sale.'
      },
      {
        q: 'How do Collaborations & Royalty Splits work?',
        a: 'On the Pro plan, you can set up royalty splits with collaborators on a release. When the release earns royalties, the earnings are automatically split according to the agreed percentages and deposited into each collaborator\'s wallet.'
      },
      {
        q: 'What are Pre-Save Campaigns?',
        a: 'Pre-Save Campaigns (Pro plan) let you create a landing page where fans can pre-save your upcoming release on their preferred streaming platform. This helps boost your day-one streams and chart positions.'
      },
      {
        q: 'What is YouTube Content ID?',
        a: 'YouTube Content ID (Pro plan) automatically identifies when your music is used in YouTube videos and claims revenue on your behalf. This ensures you get paid whenever someone uses your music in their content.'
      },
      {
        q: 'What is Spotify Canvas?',
        a: 'Spotify Canvas (Pro plan) lets you upload short looping videos that play alongside your tracks on Spotify. This enhances the listener experience and can increase engagement with your music.'
      },
      {
        q: 'How does In-App Messaging work?',
        a: 'In-App Messaging (Rise and Pro plans) lets you communicate directly with other artists, producers, and collaborators on the platform without needing to share personal contact information.'
      },
    ]
  },
  {
    title: 'For Labels & Producers',
    icon: <Users className="w-5 h-5" />,
    color: '#FF9500',
    items: [
      {
        q: 'How does the Label account work?',
        a: 'Label accounts can manage multiple artists under one roof. You can distribute releases for your artists, track analytics across your roster, manage royalty splits, and handle payouts all from a centralized dashboard.'
      },
      {
        q: 'How does the Producer account work?',
        a: 'Producer accounts are optimized for beat makers and instrumentalists. You can sell beats through the marketplace, distribute your own music, manage licensing agreements, and track earnings from both sales and streams.'
      },
      {
        q: 'Can I import streaming data via CSV?',
        a: 'CSV data import is an admin-only feature. If you need to import historical streaming data, contact our team and we will assist you with the import process.'
      },
    ]
  },
  {
    title: 'Account & Security',
    icon: <ShieldCheck className="w-5 h-5" />,
    color: '#EF4444',
    items: [
      {
        q: 'Is my music and data secure?',
        a: 'Yes. We use industry-standard encryption for all data, secure cloud storage for your audio files, and follow best practices for data protection. Your music files are stored securely and only distributed to the platforms you choose.'
      },
      {
        q: 'Can I delete my account?',
        a: 'Yes. Contact our support team to request account deletion. Please note that any active releases will need to be taken down from stores before account deletion can be completed.'
      },
      {
        q: 'Do I retain ownership of my music?',
        a: 'Absolutely. You retain 100% ownership of your music at all times. Kalmori is a distribution service — we distribute your music on your behalf but never claim ownership or copyright over your content.'
      },
    ]
  },
];

const FAQItem = ({ q, a }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-b border-white/5 last:border-0">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between py-5 px-1 text-left group" data-testid={`faq-q-${q.slice(0,20).replace(/\s/g,'-').toLowerCase()}`}>
        <span className="text-sm font-medium text-white group-hover:text-[#7C4DFF] transition-colors pr-4">{q}</span>
        <CaretDown className={`w-4 h-4 text-[#A1A1AA] shrink-0 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="pb-5 px-1">
          <p className="text-sm text-[#A1A1AA] leading-relaxed whitespace-pre-line">{a}</p>
        </div>
      )}
    </div>
  );
};

export default function FAQPage() {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState(0);

  return (
    <PublicLayout>
      <div className="min-h-screen bg-[#0a0a0a]">
        {/* Hero */}
        <div className="pt-24 pb-12 text-center px-4">
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">Frequently Asked <span className="text-[#E53935]">Questions</span></h1>
          <p className="text-base text-[#A1A1AA] max-w-xl mx-auto">Everything you need to know about Kalmori, our plans, features, and how to get the most out of your music distribution.</p>
        </div>

        {/* Quick Plan Summary Cards */}
        <div className="max-w-5xl mx-auto px-4 pb-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { name: 'Free', price: '$0', note: 'Kalmori keeps 20%', icon: <Lightning className="w-5 h-5" weight="fill" />, color: '#888', desc: 'Unlimited releases, no upfront cost' },
              { name: 'Rise', price: '$24.99', note: 'per release \u2022 5% revenue', icon: <Rocket className="w-5 h-5" weight="fill" />, color: '#7C4DFF', desc: 'Singles, advanced tools, priority support' },
              { name: 'Pro', price: '$49.99', note: '/month \u2022 0% revenue', icon: <Crown className="w-5 h-5" weight="fill" />, color: '#FFD700', desc: 'Albums + singles, AI tools, keep 100%' },
            ].map((p, i) => (
              <div key={i} className="bg-[#141414] border border-white/10 rounded-xl p-5 hover:border-white/20 transition-all cursor-pointer" onClick={() => navigate('/pricing')} data-testid={`faq-plan-${p.name.toLowerCase()}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${p.color}15`, color: p.color }}>{p.icon}</div>
                  <div>
                    <p className="text-sm font-bold text-white">{p.name}</p>
                    <p className="text-[10px] text-[#A1A1AA]">{p.note}</p>
                  </div>
                  <span className="ml-auto text-lg font-bold" style={{ color: p.color }}>{p.price}</span>
                </div>
                <p className="text-xs text-[#A1A1AA]">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ Content */}
        <div className="max-w-4xl mx-auto px-4 pb-24">
          {/* Section Tabs */}
          <div className="flex flex-wrap gap-2 mb-8 justify-center" data-testid="faq-section-tabs">
            {faqSections.map((s, i) => (
              <button key={i} onClick={() => setActiveSection(i)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium border transition-all ${activeSection === i ? 'border-white/30 bg-white/10 text-white' : 'border-white/10 text-[#A1A1AA] hover:border-white/20 hover:text-white'}`}
                data-testid={`faq-tab-${i}`}>
                <span style={{ color: activeSection === i ? s.color : undefined }}>{s.icon}</span>
                {s.title}
              </button>
            ))}
          </div>

          {/* Active Section */}
          <div className="bg-[#141414] border border-white/10 rounded-xl overflow-hidden" data-testid="faq-content">
            <div className="px-6 py-4 border-b border-white/10 flex items-center gap-3">
              <span style={{ color: faqSections[activeSection].color }}>{faqSections[activeSection].icon}</span>
              <h2 className="text-lg font-bold text-white">{faqSections[activeSection].title}</h2>
              <span className="text-xs text-[#A1A1AA] bg-white/5 px-2 py-0.5 rounded-full">{faqSections[activeSection].items.length} questions</span>
            </div>
            <div className="px-6">
              {faqSections[activeSection].items.map((item, i) => (
                <FAQItem key={i} q={item.q} a={item.a} />
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="mt-12 text-center">
            <p className="text-sm text-[#A1A1AA] mb-4">Still have questions? We are here to help.</p>
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <button onClick={() => navigate('/pricing')} className="px-6 py-3 bg-[#E53935] text-white rounded-full text-sm font-bold hover:bg-[#d32f2f] transition-all" data-testid="faq-view-pricing">
                View Plans & Pricing
              </button>
              <button onClick={() => navigate('/register')} className="px-6 py-3 bg-white/10 text-white rounded-full text-sm font-bold hover:bg-white/20 transition-all border border-white/10" data-testid="faq-get-started">
                Get Started Free
              </button>
            </div>
          </div>
        </div>
      </div>
      <GlobalFooter />
    </PublicLayout>
  );
}
