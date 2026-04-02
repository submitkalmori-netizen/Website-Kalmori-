import React from 'react';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';

const sections = [
  { title: 'Information We Collect', content: 'We collect information you provide directly, including: name, email address, payment information, and any music or content you upload. We also automatically collect usage data, device information, and analytics data when you use our platform.' },
  { title: 'How We Use Your Information', content: 'We use your information to: provide and maintain our services; process transactions and distribute your music; send service notifications and updates; improve our platform and user experience; comply with legal obligations; and protect against fraud and abuse.' },
  { title: 'Information Sharing', content: 'We share your information with: digital service providers (DSPs) as necessary for music distribution; payment processors for transaction handling; analytics providers to improve our services. We do not sell your personal information to third parties.' },
  { title: 'Data Security', content: 'We implement industry-standard security measures to protect your information, including encryption, secure servers, and access controls. However, no method of transmission over the Internet is 100% secure, and we cannot guarantee absolute security.' },
  { title: 'Your Rights', content: 'You have the right to: access your personal data; correct inaccurate data; delete your account and data; export your data; opt out of marketing communications. Contact us to exercise these rights.' },
  { title: 'Cookies and Tracking', content: 'We use cookies and similar technologies to improve your experience, analyze usage, and personalize content. You can control cookie settings through your browser preferences.' },
  { title: 'Third-Party Services', content: 'Our platform may integrate with third-party services (streaming platforms, payment processors, etc.). These services have their own privacy policies, and we encourage you to review them.' },
  { title: 'Children\'s Privacy', content: 'Our Service is not directed to children under 13. We do not knowingly collect personal information from children under 13. If you believe we have collected such information, please contact us immediately.' },
  { title: 'International Data Transfers', content: 'Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place for such transfers.' },
  { title: 'Changes to This Policy', content: 'We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new policy on this page and updating the "Last updated" date.' },
  { title: 'Contact Us', content: 'For privacy-related questions or concerns, please contact our privacy team at privacy@kalmori.org or through our Contact Support page.' },
];

export default function PrivacyPage() {
  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto" data-testid="privacy-page">
        <div className="p-6">
          <h1 className="text-[28px] font-extrabold text-white text-center mb-2">Privacy Policy</h1>
          <p className="text-[13px] text-gray-400 text-center mb-5">Last updated: March 2026</p>
          <div className="h-px bg-[#333] mb-6" />
          <p className="text-[15px] text-[#aaa] leading-relaxed mb-6">At Kalmori, we take your privacy seriously. This Privacy Policy describes how we collect, use, and protect your personal information when you use our music distribution platform.</p>
          <div className="space-y-6">
            {sections.map((s, i) => (
              <div key={i}>
                <h2 className="text-xl font-bold text-white mb-2.5">{`${i + 1}. ${s.title}`}</h2>
                <p className="text-[15px] text-[#aaa] leading-relaxed">{s.content}</p>
              </div>
            ))}
          </div>
        </div>
        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
