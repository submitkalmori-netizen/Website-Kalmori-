import React, { useState } from 'react';
import PublicLayout from '../components/PublicLayout';
import GlobalFooter from '../components/GlobalFooter';
import { Envelope, Phone, MapPin, PaperPlaneTilt } from '@phosphor-icons/react';

const contactItems = [
  { icon: <Envelope className="w-6 h-6" />, label: 'Email', value: 'support@kalmori.org', color: '#7C4DFF' },
  { icon: <Phone className="w-6 h-6" />, label: 'Phone', value: '+1 (555) 123-4567', color: '#E040FB' },
  { icon: <MapPin className="w-6 h-6" />, label: 'Address', value: '123 Music Street, LA', color: '#FF4081' },
];

export default function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', message: '' });
  const [sent, setSent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.message) return;
    setSent(true);
    setForm({ name: '', email: '', message: '' });
    setTimeout(() => setSent(false), 4000);
  };

  return (
    <PublicLayout>
      <div className="max-w-2xl mx-auto" data-testid="contact-page">
        {/* Hero */}
        <div className="py-10 px-6 text-center bg-gradient-to-b from-[#E040FB]/10 to-transparent">
          <p className="text-xs font-bold text-[#E040FB] tracking-[3px] mb-3">CONTACT US</p>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white">We're Here to <span className="text-[#E040FB]">Help</span></h1>
        </div>

        {/* Contact Info */}
        <div className="p-6 bg-[#0a0a0a] space-y-5">
          {contactItems.map((item, i) => (
            <div key={i} className="flex items-center gap-4" data-testid={`contact-${item.label.toLowerCase()}`}>
              <div className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${item.color}20`, color: item.color }}>
                {item.icon}
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">{item.label}</p>
                <p className="text-base font-semibold text-white">{item.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Form */}
        <div className="p-6 bg-[#111]">
          <h2 className="text-xl font-bold text-white mb-5">Send us a Message</h2>
          {sent && <div className="p-4 rounded-xl bg-[#4CAF50]/10 border border-[#4CAF50]/30 text-[#4CAF50] text-sm mb-4" data-testid="contact-success">Thank you! We'll get back to you soon.</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <input type="text" placeholder="Your Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full bg-black border border-[#333] rounded-xl px-4 py-4 text-white text-base placeholder-gray-600 focus:border-[#E040FB] focus:outline-none" data-testid="contact-name" />
            <input type="email" placeholder="Your Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full bg-black border border-[#333] rounded-xl px-4 py-4 text-white text-base placeholder-gray-600 focus:border-[#E040FB] focus:outline-none" data-testid="contact-email" />
            <textarea placeholder="Your Message" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} rows={5}
              className="w-full bg-black border border-[#333] rounded-xl px-4 py-4 text-white text-base placeholder-gray-600 focus:border-[#E040FB] focus:outline-none resize-none" data-testid="contact-message" />
            <button type="submit" className="w-full py-4 rounded-xl bg-[#E040FB] text-white text-base font-bold tracking-wider flex items-center justify-center gap-2" data-testid="contact-submit">
              <PaperPlaneTilt className="w-5 h-5" /> SEND MESSAGE
            </button>
          </form>
        </div>

        <GlobalFooter />
      </div>
    </PublicLayout>
  );
}
