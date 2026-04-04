import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { API, BACKEND_URL } from '../App';
import {
  MusicNotes, ChartLineUp, Users, Star, Rocket, ChatTeardropDots,
  ArrowRight, Check, SpotifyLogo, AppleLogo, YoutubeLogo, TiktokLogo,
  Play, CurrencyDollar, Brain, Trophy, Target, ShareNetwork,
  ChatCircleDots, FileText, Waveform, HandCoins, Palette, Lightning
} from '@phosphor-icons/react';

const ICON_MAP = {
  MusicNotes, ChartLineUp, Users, Star, Rocket, ChatTeardropDots,
  CurrencyDollar, Brain, Trophy, Target, ShareNetwork, ChatCircleDots,
  FileText, Waveform, HandCoins, Palette, Lightning, ArrowRight
};

const resolveUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `${BACKEND_URL}/api/files/${url}`;
};

const DynamicBlock = ({ block }) => {
  const { type, content, styles: s = {} } = block;
  const pad = `${s.padding || 40}px`;
  const bg = s.backgroundColor || '#0A0A0A';
  const tc = s.textColor || '#fff';
  const accent = s.accentColor || '#7C4DFF';
  const customCss = s.customCss || '';
  const blockId = `dyn-${block.id}`;

  const wrap = (el) => (
    <div id={blockId}>
      {customCss && <style>{`#${blockId} { ${customCss} }`}</style>}
      {el}
    </div>
  );

  if (type === 'hero') return wrap(
    <section style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: s.textAlign || 'center' }}>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-[1.05] tracking-tight mb-4" style={{ color: tc }}>{content.title}</h1>
        <p className="text-lg md:text-xl mb-8 opacity-70 max-w-2xl mx-auto" style={{ color: tc }}>{content.subtitle}</p>
        {content.buttonText && (
          <Link to={content.buttonUrl || '/register'} className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full text-white text-sm font-bold tracking-wide hover:brightness-110 transition-all"
            style={{ backgroundColor: accent }}>{content.buttonText} <ArrowRight className="w-4 h-4" /></Link>
        )}
      </div>
    </section>
  );

  if (type === 'text') return wrap(
    <section style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: s.textAlign || 'left' }}>
      <div className="mx-auto" style={{ maxWidth: `${s.maxWidth || 800}px` }}>
        {content.heading && <h2 className="text-2xl sm:text-3xl font-bold mb-4" style={{ color: s.headingColor || tc }}>{content.heading}</h2>}
        <p className="text-base leading-relaxed opacity-80" style={{ color: tc }}>{content.body}</p>
      </div>
    </section>
  );

  if (type === 'image') return wrap(
    <section style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: 'center' }}>
      {content.imageUrl && <img src={resolveUrl(content.imageUrl)} alt={content.altText || ''} className="max-w-full mx-auto" style={{ borderRadius: `${s.borderRadius || 16}px`, maxWidth: `${s.maxWidth || 900}px` }} />}
      {content.caption && <p className="text-sm mt-3 opacity-50" style={{ color: tc }}>{content.caption}</p>}
    </section>
  );

  if (type === 'features') return (
    <section style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-black mb-3" style={{ color: tc }}>{content.heading}</h2>
          <p className="text-lg opacity-60" style={{ color: tc }}>{content.subtitle}</p>
        </div>
        <div className="grid gap-5" style={{ gridTemplateColumns: `repeat(${s.columns || 3}, 1fr)` }}>
          {(content.items || []).map((item, i) => {
            const Icon = ICON_MAP[item.icon] || MusicNotes;
            return (
              <div key={i} className="bg-white/5 rounded-2xl p-6 border border-white/5 hover:border-white/15 transition-all">
                <div className="w-12 h-12 rounded-xl mb-4 flex items-center justify-center" style={{ backgroundColor: `${item.color}15`, color: item.color }}>
                  <Icon className="w-6 h-6" weight="fill" />
                </div>
                <h3 className="text-base font-bold mb-2" style={{ color: tc }}>{item.title}</h3>
                <p className="text-sm opacity-60 leading-relaxed" style={{ color: tc }}>{item.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );

  if (type === 'cta') return (
    <section style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: 'center' }}>
      <div className="max-w-3xl mx-auto">
        <h2 className="text-3xl sm:text-4xl font-black mb-4" style={{ color: tc }}>{content.heading}</h2>
        <p className="text-lg mb-8 opacity-70" style={{ color: tc }}>{content.subtitle}</p>
        {content.buttonText && (
          <Link to={content.buttonUrl || '/register'} className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full text-white text-sm font-bold hover:brightness-110 transition-all"
            style={{ backgroundColor: accent }}>{content.buttonText} <ArrowRight className="w-4 h-4" /></Link>
        )}
      </div>
    </section>
  );

  if (type === 'testimonials') return (
    <section style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="max-w-5xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-bold mb-8 text-center" style={{ color: tc }}>{content.heading}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {(content.items || []).map((item, i) => (
            <div key={i} className="bg-white/5 rounded-2xl p-6 border border-white/5">
              <p className="text-sm italic mb-4 opacity-80 leading-relaxed" style={{ color: tc }}>"{item.quote}"</p>
              <p className="text-sm font-bold" style={{ color: accent }}>{item.author}</p>
              {item.role && <p className="text-xs opacity-40" style={{ color: tc }}>{item.role}</p>}
            </div>
          ))}
        </div>
      </div>
    </section>
  );

  if (type === 'stats') return (
    <section style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="flex flex-wrap justify-center gap-12 max-w-4xl mx-auto">
        {(content.items || []).map((item, i) => (
          <div key={i} className="text-center">
            <p className="text-4xl font-black" style={{ color: accent }}>{item.value}</p>
            <p className="text-sm uppercase tracking-wider mt-2 opacity-50" style={{ color: tc }}>{item.label}</p>
          </div>
        ))}
      </div>
    </section>
  );

  if (type === 'spacer') return <div style={{ height: `${s.height || 60}px`, backgroundColor: s.backgroundColor || 'transparent' }} />;

  if (type === 'two_column') return (
    <section style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-6xl mx-auto">
        <div>
          <h3 className="text-xl font-bold mb-3" style={{ color: tc }}>{content.leftHeading}</h3>
          <p className="text-sm opacity-70 leading-relaxed" style={{ color: tc }}>{content.leftBody}</p>
        </div>
        <div>
          <h3 className="text-xl font-bold mb-3" style={{ color: tc }}>{content.rightHeading}</h3>
          <p className="text-sm opacity-70 leading-relaxed" style={{ color: tc }}>{content.rightBody}</p>
        </div>
      </div>
    </section>
  );

  if (type === 'logo_bar') return (
    <section style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: 'center' }}>
      <p className="text-xs uppercase tracking-[4px] mb-6 opacity-30 font-bold" style={{ color: tc }}>{content.heading}</p>
      <div className="flex flex-wrap justify-center gap-8">
        {(content.items || []).map((name, i) => {
          const icons = { 'Spotify': SpotifyLogo, 'Apple Music': AppleLogo, 'YouTube Music': YoutubeLogo, 'TikTok': TiktokLogo };
          const Icon = icons[name];
          return (
            <div key={i} className="flex items-center gap-2 opacity-40" style={{ color: tc }}>
              {Icon && <Icon className="w-5 h-5" weight="fill" />}
              <span className="text-sm font-medium">{name}</span>
            </div>
          );
        })}
      </div>
    </section>
  );

  if (type === 'pricing') return (
    <section style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-black mb-3" style={{ color: tc }}>{content.heading}</h2>
          <p className="text-lg opacity-60" style={{ color: tc }}>{content.subtitle}</p>
        </div>
        <div className="flex flex-wrap justify-center gap-6">
          {(content.items || []).map((plan, i) => (
            <div key={i} className={`rounded-2xl p-8 w-72 ${plan.highlighted ? 'border-2' : 'border border-white/10'}`}
              style={{ borderColor: plan.highlighted ? accent : undefined, backgroundColor: plan.highlighted ? `${accent}08` : 'rgba(255,255,255,0.02)' }}>
              <p className="text-sm font-bold opacity-60" style={{ color: tc }}>{plan.name}</p>
              <p className="text-4xl font-black mt-2" style={{ color: tc }}>{plan.price}<span className="text-sm opacity-40">{plan.period}</span></p>
              <ul className="mt-6 space-y-3">
                {(plan.features || []).map((f, fi) => <li key={fi} className="text-sm flex items-center gap-2 opacity-70" style={{ color: tc }}><Check className="w-4 h-4 flex-shrink-0" weight="bold" style={{ color: '#1DB954' }} />{f}</li>)}
              </ul>
              {plan.buttonText && (
                <Link to="/register" className="block text-center mt-6 px-6 py-2.5 rounded-full text-sm font-bold text-white"
                  style={{ backgroundColor: plan.highlighted ? accent : 'rgba(255,255,255,0.1)' }}>{plan.buttonText}</Link>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );

  if (type === 'video') return (
    <section style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: 'center' }}>
      {content.videoUrl && (
        <div className="aspect-video mx-auto rounded-2xl overflow-hidden" style={{ maxWidth: `${s.maxWidth || 900}px` }}>
          <iframe src={content.videoUrl} className="w-full h-full" allow="autoplay; encrypted-media" allowFullScreen title={content.title || 'Video'} />
        </div>
      )}
    </section>
  );

  return null;
};

export const DynamicPageRenderer = ({ slug }) => {
  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/pages/${slug}`)
      .then(res => res.json())
      .then(data => { setPage(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [slug]);

  if (loading) return null;
  if (!page || !page.published || !page.blocks?.length) return null;

  return (
    <div data-testid="dynamic-page">
      {page.blocks.sort((a, b) => (a.order || 0) - (b.order || 0)).map((block) => (
        <DynamicBlock key={block.id} block={block} />
      ))}
    </div>
  );
};

export default DynamicPageRenderer;
