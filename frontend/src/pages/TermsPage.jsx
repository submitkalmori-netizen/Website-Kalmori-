import React from 'react';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';

const sections = [
  { title: 'Acceptance of Terms', content: 'By accessing and using the Kalmori platform ("Service"), you agree to be bound by these Terms and Conditions. If you do not agree to these terms, please do not use our Service.' },
  { title: 'Description of Service', content: 'Kalmori provides digital music distribution services, allowing artists to distribute their music to various streaming platforms and digital stores worldwide. Our services include music distribution, analytics, royalty collection, and promotional tools.' },
  { title: 'Account Registration', content: 'To use certain features of the Service, you must register for an account. You agree to provide accurate, current, and complete information during the registration process and to keep your account information updated. You are responsible for maintaining the confidentiality of your account credentials.' },
  { title: 'Content Ownership', content: 'You retain all ownership rights to the music and content you upload to Kalmori. By uploading content, you grant Kalmori a non-exclusive license to distribute, reproduce, and display your content solely for the purpose of providing our services. You represent and warrant that you have the right to distribute all content you upload.' },
  { title: 'Distribution Rights', content: 'When you submit content for distribution, you authorize Kalmori to distribute your content to the selected digital service providers (DSPs). You understand that each DSP may have its own terms of service that apply to the distribution and availability of your content.' },
  { title: 'Royalties and Payments', content: 'Kalmori collects royalties on your behalf from DSPs. Royalties are calculated based on the terms of your selected plan. Payments are processed according to the payment schedule outlined in your account settings. Minimum withdrawal amounts may apply.' },
  { title: 'Prohibited Content', content: 'You may not upload content that: infringes on any third party\'s intellectual property rights; contains illegal material; is defamatory, obscene, or otherwise objectionable; contains malware or harmful code; or violates any applicable laws or regulations.' },
  { title: 'Plan Terms', content: 'Kalmori offers various subscription plans. Each plan has specific features, limitations, and pricing. Plan details are subject to change with reasonable notice. Refunds are handled according to our refund policy.' },
  { title: 'Termination', content: 'Either party may terminate this agreement at any time. Upon termination, Kalmori will make reasonable efforts to remove your content from DSPs, though removal timing depends on each DSP\'s processes. Outstanding royalties will be paid according to the regular payment schedule.' },
  { title: 'Limitation of Liability', content: 'Kalmori shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Service. Our total liability shall not exceed the amount you paid for the Service in the preceding 12 months.' },
  { title: 'Changes to Terms', content: 'Kalmori reserves the right to modify these Terms at any time. We will notify users of material changes via email or through the platform. Continued use of the Service after changes constitutes acceptance of the modified terms.' },
  { title: 'Contact Information', content: 'For questions about these Terms, please contact us at legal@kalmori.org or through our Contact Support page.' },
];

export default function TermsPage() {
  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto" data-testid="terms-page">
        <div className="p-6">
          <h1 className="text-[28px] font-extrabold text-white text-center mb-2">Terms & Conditions</h1>
          <p className="text-[13px] text-gray-400 text-center mb-5">Last updated: March 2026</p>
          <div className="h-px bg-[#333] mb-6" />
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
