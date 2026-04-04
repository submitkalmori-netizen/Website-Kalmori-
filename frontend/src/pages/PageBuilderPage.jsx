import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { toast } from 'sonner';
import axios from 'axios';
import { API } from '../App';
import {
  Plus, Trash, DotsSixVertical, FloppyDisk, Rocket, Eye, ArrowLeft,
  TextT, Image, Rows, ChatTeardropDots, ChartBar, ArrowsOutSimple,
  Star, CurrencyDollar, VideoCamera, MusicNotes, Columns, PaintBrush,
  CaretDown, CaretUp, Gear, X, PencilSimple, Check
} from '@phosphor-icons/react';

const BLOCK_TYPES = [
  { key: 'hero', label: 'Hero Banner', icon: <Star className="w-4 h-4" weight="fill" />, color: '#7C4DFF' },
  { key: 'text', label: 'Text Block', icon: <TextT className="w-4 h-4" weight="fill" />, color: '#2196F3' },
  { key: 'image', label: 'Image', icon: <Image className="w-4 h-4" weight="fill" />, color: '#E040FB' },
  { key: 'features', label: 'Feature Grid', icon: <Rows className="w-4 h-4" weight="fill" />, color: '#1DB954' },
  { key: 'cta', label: 'Call to Action', icon: <Rocket className="w-4 h-4" weight="fill" />, color: '#FF4081' },
  { key: 'testimonials', label: 'Testimonials', icon: <ChatTeardropDots className="w-4 h-4" weight="fill" />, color: '#FF9800' },
  { key: 'stats', label: 'Stats Row', icon: <ChartBar className="w-4 h-4" weight="fill" />, color: '#00BCD4' },
  { key: 'spacer', label: 'Spacer', icon: <ArrowsOutSimple className="w-4 h-4" weight="fill" />, color: '#666' },
  { key: 'two_column', label: 'Two Columns', icon: <Columns className="w-4 h-4" weight="fill" />, color: '#9C27B0' },
  { key: 'pricing', label: 'Pricing', icon: <CurrencyDollar className="w-4 h-4" weight="fill" />, color: '#FFD700' },
  { key: 'logo_bar', label: 'Logo Bar', icon: <MusicNotes className="w-4 h-4" weight="fill" />, color: '#E040FB' },
  { key: 'video', label: 'Video Embed', icon: <VideoCamera className="w-4 h-4" weight="fill" />, color: '#FF5722' },
];

/* ======== Inline Editable Text ======== */
const EditableText = ({ value, onChange, tag: Tag = 'p', className = '', style = {}, placeholder = 'Click to edit...' }) => {
  const ref = useRef(null);
  const [editing, setEditing] = useState(false);

  const handleBlur = () => {
    setEditing(false);
    if (ref.current) onChange(ref.current.innerText);
  };

  return (
    <Tag
      ref={ref}
      contentEditable={editing}
      suppressContentEditableWarning
      onClick={() => setEditing(true)}
      onBlur={handleBlur}
      onKeyDown={(e) => { if (e.key === 'Enter' && Tag !== 'p') { e.preventDefault(); ref.current?.blur(); } }}
      className={`outline-none transition-all ${editing ? 'ring-2 ring-[#7C4DFF] ring-offset-2 ring-offset-[#0A0A0A] rounded px-1' : 'cursor-pointer hover:ring-1 hover:ring-white/20 hover:rounded'} ${className}`}
      style={style}
      data-placeholder={!value ? placeholder : undefined}
    >
      {value || placeholder}
    </Tag>
  );
};

/* ======== Block Preview Renderers ======== */
const BlockPreview = ({ block, onUpdate }) => {
  const { type, content, styles } = block;
  const s = styles || {};
  const pad = `${s.padding || 40}px`;
  const bg = s.backgroundColor || '#0A0A0A';
  const tc = s.textColor || '#fff';

  const updateContent = (key, val) => onUpdate({ ...block, content: { ...content, [key]: val } });

  if (type === 'hero') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: s.textAlign || 'center' }}>
      <EditableText value={content.title} onChange={v => updateContent('title', v)} tag="h1" className="text-4xl font-black mb-3" style={{ color: tc }} />
      <EditableText value={content.subtitle} onChange={v => updateContent('subtitle', v)} tag="p" className="text-lg mb-6 opacity-70" style={{ color: tc }} />
      <EditableText value={content.buttonText} onChange={v => updateContent('buttonText', v)} tag="span"
        className="inline-block px-8 py-3 rounded-full text-white text-sm font-bold" style={{ backgroundColor: s.accentColor || '#7C4DFF' }} />
    </div>
  );

  if (type === 'text') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px`, maxWidth: `${s.maxWidth || 800}px`, margin: '0 auto', textAlign: s.textAlign || 'left' }}>
      <EditableText value={content.heading} onChange={v => updateContent('heading', v)} tag="h2" className="text-2xl font-bold mb-4" style={{ color: s.headingColor || tc }} />
      <EditableText value={content.body} onChange={v => updateContent('body', v)} tag="p" className="text-base leading-relaxed opacity-80" style={{ color: tc }} />
    </div>
  );

  if (type === 'image') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: 'center' }}>
      {content.imageUrl ? (
        <img src={content.imageUrl} alt={content.altText} className="max-w-full mx-auto" style={{ borderRadius: `${s.borderRadius || 16}px`, maxWidth: `${s.maxWidth || 900}px` }} />
      ) : (
        <div className="border-2 border-dashed border-white/20 rounded-2xl py-16 px-8 mx-auto" style={{ maxWidth: `${s.maxWidth || 900}px` }}>
          <Image className="w-12 h-12 text-white/20 mx-auto mb-3" />
          <p className="text-white/40 text-sm">Enter image URL in the style panel</p>
        </div>
      )}
      {content.caption && <EditableText value={content.caption} onChange={v => updateContent('caption', v)} tag="p" className="text-sm mt-3 opacity-50" style={{ color: tc }} />}
    </div>
  );

  if (type === 'features') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="text-center mb-8">
        <EditableText value={content.heading} onChange={v => updateContent('heading', v)} tag="h2" className="text-3xl font-bold mb-2" style={{ color: tc }} />
        <EditableText value={content.subtitle} onChange={v => updateContent('subtitle', v)} tag="p" className="text-base opacity-60" style={{ color: tc }} />
      </div>
      <div className={`grid gap-4`} style={{ gridTemplateColumns: `repeat(${s.columns || 3}, 1fr)` }}>
        {(content.items || []).map((item, i) => (
          <div key={i} className="bg-white/5 rounded-xl p-5 border border-white/5">
            <div className="w-10 h-10 rounded-lg mb-3 flex items-center justify-center" style={{ backgroundColor: `${item.color}20`, color: item.color }}>
              <MusicNotes className="w-5 h-5" weight="fill" />
            </div>
            <EditableText value={item.title} onChange={v => {
              const items = [...content.items]; items[i] = { ...items[i], title: v };
              onUpdate({ ...block, content: { ...content, items } });
            }} tag="h3" className="text-sm font-bold mb-1" style={{ color: tc }} />
            <EditableText value={item.description} onChange={v => {
              const items = [...content.items]; items[i] = { ...items[i], description: v };
              onUpdate({ ...block, content: { ...content, items } });
            }} tag="p" className="text-xs opacity-60" style={{ color: tc }} />
          </div>
        ))}
      </div>
    </div>
  );

  if (type === 'cta') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: 'center' }}>
      <EditableText value={content.heading} onChange={v => updateContent('heading', v)} tag="h2" className="text-3xl font-bold mb-3" style={{ color: tc }} />
      <EditableText value={content.subtitle} onChange={v => updateContent('subtitle', v)} tag="p" className="text-base mb-6 opacity-70" style={{ color: tc }} />
      <EditableText value={content.buttonText} onChange={v => updateContent('buttonText', v)} tag="span"
        className="inline-block px-8 py-3 rounded-full text-white text-sm font-bold" style={{ backgroundColor: s.accentColor || '#7C4DFF' }} />
    </div>
  );

  if (type === 'testimonials') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <EditableText value={content.heading} onChange={v => updateContent('heading', v)} tag="h2" className="text-2xl font-bold mb-6 text-center" style={{ color: tc }} />
      <div className="grid grid-cols-2 gap-4">
        {(content.items || []).map((item, i) => (
          <div key={i} className="bg-white/5 rounded-xl p-5 border border-white/5">
            <EditableText value={item.quote} onChange={v => {
              const items = [...content.items]; items[i] = { ...items[i], quote: v };
              onUpdate({ ...block, content: { ...content, items } });
            }} tag="p" className="text-sm italic mb-3 opacity-80" style={{ color: tc }} />
            <EditableText value={item.author} onChange={v => {
              const items = [...content.items]; items[i] = { ...items[i], author: v };
              onUpdate({ ...block, content: { ...content, items } });
            }} tag="span" className="text-xs font-bold" style={{ color: s.accentColor || '#7C4DFF' }} />
          </div>
        ))}
      </div>
    </div>
  );

  if (type === 'stats') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="flex justify-center gap-12">
        {(content.items || []).map((item, i) => (
          <div key={i} className="text-center">
            <EditableText value={item.value} onChange={v => {
              const items = [...content.items]; items[i] = { ...items[i], value: v };
              onUpdate({ ...block, content: { ...content, items } });
            }} tag="p" className="text-3xl font-black" style={{ color: s.accentColor || '#7C4DFF' }} />
            <EditableText value={item.label} onChange={v => {
              const items = [...content.items]; items[i] = { ...items[i], label: v };
              onUpdate({ ...block, content: { ...content, items } });
            }} tag="p" className="text-xs uppercase tracking-wider mt-1 opacity-60" style={{ color: tc }} />
          </div>
        ))}
      </div>
    </div>
  );

  if (type === 'spacer') return (
    <div style={{ height: `${s.height || 60}px`, backgroundColor: s.backgroundColor || 'transparent' }} className="flex items-center justify-center">
      <span className="text-[10px] text-white/20 uppercase tracking-wider">Spacer ({s.height || 60}px)</span>
    </div>
  );

  if (type === 'two_column') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="grid grid-cols-2 gap-8">
        <div>
          <EditableText value={content.leftHeading} onChange={v => updateContent('leftHeading', v)} tag="h3" className="text-xl font-bold mb-3" style={{ color: tc }} />
          <EditableText value={content.leftBody} onChange={v => updateContent('leftBody', v)} tag="p" className="text-sm opacity-70" style={{ color: tc }} />
        </div>
        <div>
          <EditableText value={content.rightHeading} onChange={v => updateContent('rightHeading', v)} tag="h3" className="text-xl font-bold mb-3" style={{ color: tc }} />
          <EditableText value={content.rightBody} onChange={v => updateContent('rightBody', v)} tag="p" className="text-sm opacity-70" style={{ color: tc }} />
        </div>
      </div>
    </div>
  );

  if (type === 'logo_bar') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: 'center' }}>
      <EditableText value={content.heading} onChange={v => updateContent('heading', v)} tag="p" className="text-xs uppercase tracking-[3px] mb-4 opacity-40 font-bold" style={{ color: tc }} />
      <div className="flex flex-wrap justify-center gap-6">
        {(content.items || []).map((name, i) => (
          <span key={i} className="text-sm font-medium opacity-40" style={{ color: tc }}>{name}</span>
        ))}
      </div>
    </div>
  );

  if (type === 'pricing') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px` }}>
      <div className="text-center mb-8">
        <EditableText value={content.heading} onChange={v => updateContent('heading', v)} tag="h2" className="text-3xl font-bold mb-2" style={{ color: tc }} />
        <EditableText value={content.subtitle} onChange={v => updateContent('subtitle', v)} tag="p" className="text-base opacity-60" style={{ color: tc }} />
      </div>
      <div className="flex justify-center gap-6">
        {(content.items || []).map((plan, i) => (
          <div key={i} className={`rounded-2xl p-6 w-64 ${plan.highlighted ? 'border-2' : 'border border-white/10'}`}
            style={{ borderColor: plan.highlighted ? (s.accentColor || '#7C4DFF') : undefined, backgroundColor: plan.highlighted ? `${s.accentColor || '#7C4DFF'}10` : 'rgba(255,255,255,0.03)' }}>
            <p className="text-sm font-bold text-white/60">{plan.name}</p>
            <p className="text-3xl font-black mt-1" style={{ color: tc }}>{plan.price}<span className="text-sm opacity-50">{plan.period}</span></p>
            <ul className="mt-4 space-y-2">
              {(plan.features || []).map((f, fi) => <li key={fi} className="text-xs text-white/60 flex items-center gap-2"><Check className="w-3 h-3 text-[#1DB954]" weight="bold" />{f}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );

  if (type === 'video') return (
    <div style={{ backgroundColor: bg, padding: `${pad} 24px`, textAlign: 'center' }}>
      {content.videoUrl ? (
        <div className="aspect-video mx-auto rounded-2xl overflow-hidden" style={{ maxWidth: `${s.maxWidth || 900}px` }}>
          <iframe src={content.videoUrl} className="w-full h-full" allow="autoplay; encrypted-media" allowFullScreen title={content.title} />
        </div>
      ) : (
        <div className="border-2 border-dashed border-white/20 rounded-2xl py-16 px-8 aspect-video mx-auto flex flex-col items-center justify-center" style={{ maxWidth: `${s.maxWidth || 900}px` }}>
          <VideoCamera className="w-12 h-12 text-white/20 mb-3" />
          <p className="text-white/40 text-sm">Add video URL in the style panel</p>
        </div>
      )}
    </div>
  );

  return <div className="p-8 text-white/40 text-center text-sm">Unknown block type: {type}</div>;
};

/* ======== Style Panel ======== */
const StylePanel = ({ block, onUpdate, onClose }) => {
  const s = block.styles || {};
  const c = block.content || {};
  const updateStyle = (key, val) => onUpdate({ ...block, styles: { ...s, [key]: val } });
  const updateContent = (key, val) => onUpdate({ ...block, content: { ...c, [key]: val } });

  return (
    <div className="bg-[#1a1a1a] border border-white/10 rounded-xl p-4 space-y-4" data-testid="style-panel">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold text-white uppercase tracking-wider">Block Settings</h4>
        <button onClick={onClose} className="text-white/40 hover:text-white"><X className="w-4 h-4" /></button>
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-[10px] text-white/50 uppercase">Background</label>
          <div className="flex items-center gap-2 mt-1">
            <input type="color" value={s.backgroundColor || '#0A0A0A'} onChange={e => updateStyle('backgroundColor', e.target.value)} className="w-8 h-8 rounded cursor-pointer bg-transparent border-0" />
            <input type="text" value={s.backgroundColor || '#0A0A0A'} onChange={e => updateStyle('backgroundColor', e.target.value)} className="flex-1 bg-[#0a0a0a] border border-white/10 rounded px-2 py-1 text-xs text-white font-mono" />
          </div>
        </div>

        <div>
          <label className="text-[10px] text-white/50 uppercase">Text Color</label>
          <div className="flex items-center gap-2 mt-1">
            <input type="color" value={s.textColor || '#FFFFFF'} onChange={e => updateStyle('textColor', e.target.value)} className="w-8 h-8 rounded cursor-pointer bg-transparent border-0" />
            <input type="text" value={s.textColor || '#FFFFFF'} onChange={e => updateStyle('textColor', e.target.value)} className="flex-1 bg-[#0a0a0a] border border-white/10 rounded px-2 py-1 text-xs text-white font-mono" />
          </div>
        </div>

        {s.accentColor !== undefined && (
          <div>
            <label className="text-[10px] text-white/50 uppercase">Accent Color</label>
            <div className="flex items-center gap-2 mt-1">
              <input type="color" value={s.accentColor || '#7C4DFF'} onChange={e => updateStyle('accentColor', e.target.value)} className="w-8 h-8 rounded cursor-pointer bg-transparent border-0" />
              <input type="text" value={s.accentColor || '#7C4DFF'} onChange={e => updateStyle('accentColor', e.target.value)} className="flex-1 bg-[#0a0a0a] border border-white/10 rounded px-2 py-1 text-xs text-white font-mono" />
            </div>
          </div>
        )}

        <div>
          <label className="text-[10px] text-white/50 uppercase">Padding (px)</label>
          <input type="range" min="0" max="200" value={s.padding || 60} onChange={e => updateStyle('padding', e.target.value)}
            className="w-full mt-1 accent-[#7C4DFF]" />
          <span className="text-[10px] text-white/40">{s.padding || 60}px</span>
        </div>

        {block.type === 'spacer' && (
          <div>
            <label className="text-[10px] text-white/50 uppercase">Height (px)</label>
            <input type="range" min="10" max="300" value={s.height || 60} onChange={e => updateStyle('height', e.target.value)}
              className="w-full mt-1 accent-[#7C4DFF]" />
            <span className="text-[10px] text-white/40">{s.height || 60}px</span>
          </div>
        )}

        {(s.textAlign !== undefined || ['hero', 'text'].includes(block.type)) && (
          <div>
            <label className="text-[10px] text-white/50 uppercase">Text Align</label>
            <div className="flex gap-2 mt-1">
              {['left', 'center', 'right'].map(a => (
                <button key={a} onClick={() => updateStyle('textAlign', a)}
                  className={`px-3 py-1 rounded text-[10px] font-bold uppercase ${s.textAlign === a ? 'bg-[#7C4DFF] text-white' : 'bg-white/5 text-white/40'}`}>{a}</button>
              ))}
            </div>
          </div>
        )}

        {block.type === 'features' && (
          <div>
            <label className="text-[10px] text-white/50 uppercase">Grid Columns</label>
            <div className="flex gap-2 mt-1">
              {['2', '3', '4'].map(n => (
                <button key={n} onClick={() => updateStyle('columns', n)}
                  className={`px-3 py-1 rounded text-[10px] font-bold ${String(s.columns) === n ? 'bg-[#7C4DFF] text-white' : 'bg-white/5 text-white/40'}`}>{n}</button>
              ))}
            </div>
          </div>
        )}

        {['hero', 'cta'].includes(block.type) && (
          <div>
            <label className="text-[10px] text-white/50 uppercase">Button URL</label>
            <input type="text" value={c.buttonUrl || ''} onChange={e => updateContent('buttonUrl', e.target.value)}
              className="w-full bg-[#0a0a0a] border border-white/10 rounded px-2 py-1 text-xs text-white mt-1" placeholder="/register" />
          </div>
        )}

        {block.type === 'image' && (
          <div>
            <label className="text-[10px] text-white/50 uppercase">Image URL</label>
            <input type="text" value={c.imageUrl || ''} onChange={e => updateContent('imageUrl', e.target.value)}
              className="w-full bg-[#0a0a0a] border border-white/10 rounded px-2 py-1 text-xs text-white mt-1" placeholder="https://..." />
          </div>
        )}

        {block.type === 'video' && (
          <div>
            <label className="text-[10px] text-white/50 uppercase">Video URL (YouTube embed)</label>
            <input type="text" value={c.videoUrl || ''} onChange={e => updateContent('videoUrl', e.target.value)}
              className="w-full bg-[#0a0a0a] border border-white/10 rounded px-2 py-1 text-xs text-white mt-1" placeholder="https://youtube.com/embed/..." />
          </div>
        )}
      </div>
    </div>
  );
};

/* ======== Sortable Block Wrapper ======== */
const SortableBlock = ({ block, isSelected, onSelect, onUpdate, onDelete, onOpenStyle }) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: block.id });
  const style = { transform: CSS.Transform.toString(transform), transition, zIndex: isDragging ? 50 : 1, opacity: isDragging ? 0.6 : 1 };

  return (
    <div ref={setNodeRef} style={style}
      className={`relative group rounded-xl overflow-hidden transition-all ${isSelected ? 'ring-2 ring-[#7C4DFF]' : 'hover:ring-1 hover:ring-white/20'}`}
      onClick={() => onSelect(block.id)}
      data-testid={`builder-block-${block.id}`}
    >
      {/* Toolbar */}
      <div className={`absolute top-2 right-2 z-10 flex items-center gap-1 transition-opacity ${isSelected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
        <div {...attributes} {...listeners} className="w-7 h-7 bg-[#0a0a0a]/80 backdrop-blur rounded-lg flex items-center justify-center cursor-grab active:cursor-grabbing text-white/60 hover:text-white" data-testid={`drag-handle-${block.id}`}>
          <DotsSixVertical className="w-4 h-4" weight="bold" />
        </div>
        <button onClick={(e) => { e.stopPropagation(); onOpenStyle(block.id); }} className="w-7 h-7 bg-[#0a0a0a]/80 backdrop-blur rounded-lg flex items-center justify-center text-white/60 hover:text-[#7C4DFF]" data-testid={`style-btn-${block.id}`}>
          <PaintBrush className="w-3.5 h-3.5" />
        </button>
        <button onClick={(e) => { e.stopPropagation(); onDelete(block.id); }} className="w-7 h-7 bg-[#0a0a0a]/80 backdrop-blur rounded-lg flex items-center justify-center text-white/60 hover:text-red-400" data-testid={`delete-btn-${block.id}`}>
          <Trash className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Block type label */}
      <div className="absolute top-2 left-2 z-10 px-2 py-0.5 bg-[#0a0a0a]/80 backdrop-blur rounded text-[9px] text-white/40 font-bold uppercase tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
        {block.type.replace('_', ' ')}
      </div>

      {/* Block preview */}
      <BlockPreview block={block} onUpdate={onUpdate} />
    </div>
  );
};

/* ======== Main Page Builder ======== */
const PageBuilderPage = () => {
  const { slug = 'landing' } = useParams();
  const navigate = useNavigate();
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [published, setPublished] = useState(false);
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [styleBlock, setStyleBlock] = useState(null);
  const [showAddPanel, setShowAddPanel] = useState(false);
  const [pageTitle, setPageTitle] = useState('');

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }));

  useEffect(() => { fetchLayout(); }, [slug]);

  const fetchLayout = async () => {
    try {
      const res = await axios.get(`${API}/admin/pages/${slug}`, { withCredentials: true });
      setBlocks(res.data.blocks || []);
      setPublished(res.data.published || false);
      setPageTitle(res.data.title || slug.replace('-', ' ').replace(/\b\w/g, c => c.toUpperCase()) + ' Page');
    } catch (err) { toast.error('Failed to load page'); }
    finally { setLoading(false); }
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIdx = blocks.findIndex(b => b.id === active.id);
      const newIdx = blocks.findIndex(b => b.id === over.id);
      setBlocks(arrayMove(blocks, oldIdx, newIdx));
    }
  };

  const addBlock = async (type) => {
    try {
      const res = await axios.post(`${API}/admin/pages/${slug}/add-block`, { type, order: blocks.length }, { withCredentials: true });
      setBlocks([...blocks, res.data]);
      setShowAddPanel(false);
      toast.success(`${type.replace('_', ' ')} block added`);
    } catch (err) { toast.error('Failed to add block'); }
  };

  const updateBlock = useCallback((updated) => {
    setBlocks(prev => prev.map(b => b.id === updated.id ? updated : b));
  }, []);

  const deleteBlock = async (blockId) => {
    try {
      await axios.delete(`${API}/admin/pages/${slug}/blocks/${blockId}`, { withCredentials: true });
      setBlocks(prev => prev.filter(b => b.id !== blockId));
      if (selectedBlock === blockId) setSelectedBlock(null);
      if (styleBlock === blockId) setStyleBlock(null);
      toast.success('Block deleted');
    } catch (err) { toast.error('Failed to delete block'); }
  };

  const saveLayout = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/admin/pages/${slug}`, { blocks, title: pageTitle }, { withCredentials: true });
      toast.success('Layout saved!');
    } catch (err) { toast.error('Failed to save'); }
    finally { setSaving(false); }
  };

  const publishLayout = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/admin/pages/${slug}`, { blocks, title: pageTitle }, { withCredentials: true });
      await axios.post(`${API}/admin/pages/${slug}/publish`, {}, { withCredentials: true });
      setPublished(true);
      toast.success('Page published! Changes are now live.');
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to publish'); }
    finally { setSaving(false); }
  };

  const unpublishLayout = async () => {
    try {
      await axios.post(`${API}/admin/pages/${slug}/unpublish`, {}, { withCredentials: true });
      setPublished(false);
      toast.success('Page unpublished. Default layout restored.');
    } catch (err) { toast.error('Failed to unpublish'); }
  };

  if (loading) return <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center"><div className="w-8 h-8 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" /></div>;

  const selectedBlockData = styleBlock ? blocks.find(b => b.id === styleBlock) : null;

  return (
    <div className="min-h-screen bg-[#0e0e0e] text-white" data-testid="page-builder">
      {/* Top Bar */}
      <div className="sticky top-0 z-40 bg-[#0A0A0A] border-b border-white/10 px-4 py-3 flex items-center justify-between" data-testid="builder-toolbar">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/admin')} className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center hover:bg-white/10 text-white/60" data-testid="back-btn">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              <PencilSimple className="w-4 h-4 text-[#7C4DFF]" /> {pageTitle}
            </h1>
            <p className="text-[10px] text-white/40">/{slug === 'landing' ? '' : slug} &middot; {blocks.length} blocks {published && <span className="text-[#1DB954]">&middot; Published</span>}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <a href={slug === 'landing' ? '/' : `/${slug}`} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 rounded-lg text-xs text-white/60 hover:text-white hover:bg-white/10" data-testid="preview-btn">
            <Eye className="w-3.5 h-3.5" /> Preview
          </a>
          <button onClick={saveLayout} disabled={saving}
            className="flex items-center gap-1.5 px-4 py-1.5 bg-white/10 rounded-lg text-xs font-medium text-white hover:bg-white/15" data-testid="save-btn">
            <FloppyDisk className="w-3.5 h-3.5" /> {saving ? 'Saving...' : 'Save Draft'}
          </button>
          <button onClick={publishLayout} disabled={saving}
            className="flex items-center gap-1.5 px-4 py-1.5 bg-[#7C4DFF] rounded-lg text-xs font-bold text-white hover:bg-[#7C4DFF]/80" data-testid="publish-btn">
            <Rocket className="w-3.5 h-3.5" weight="fill" /> Publish
          </button>
          {published && (
            <button onClick={unpublishLayout} className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 rounded-lg text-xs text-red-400 hover:bg-red-500/20" data-testid="unpublish-btn">
              Unpublish
            </button>
          )}
        </div>
      </div>

      <div className="flex">
        {/* Left Sidebar — Add Blocks */}
        <div className="w-56 flex-shrink-0 bg-[#0A0A0A] border-r border-white/10 p-3 h-[calc(100vh-53px)] overflow-y-auto sticky top-[53px]" data-testid="block-palette">
          <p className="text-[10px] uppercase tracking-[2px] text-white/30 font-bold mb-3 px-1">Add Blocks</p>
          <div className="space-y-1">
            {BLOCK_TYPES.map(bt => (
              <button key={bt.key} onClick={() => addBlock(bt.key)}
                className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left text-xs font-medium text-white/70 hover:bg-white/5 hover:text-white transition-all group"
                data-testid={`add-block-${bt.key}`}
              >
                <div className="w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform" style={{ backgroundColor: `${bt.color}20`, color: bt.color }}>
                  {bt.icon}
                </div>
                {bt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Main Canvas */}
        <div className="flex-1 min-h-[calc(100vh-53px)]">
          {blocks.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-6 py-24" data-testid="empty-canvas">
              <div className="w-20 h-20 rounded-2xl bg-[#7C4DFF]/10 flex items-center justify-center mb-5">
                <Plus className="w-8 h-8 text-[#7C4DFF]" />
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Start Building</h2>
              <p className="text-sm text-white/50 mb-6 max-w-md">Click any block type on the left to add it to your page. Drag blocks to reorder them. Click on text to edit it.</p>
              <button onClick={() => addBlock('hero')} className="px-6 py-2.5 bg-[#7C4DFF] rounded-full text-sm font-bold text-white hover:bg-[#7C4DFF]/80" data-testid="add-hero-cta">
                Add a Hero Block
              </button>
            </div>
          ) : (
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={blocks.map(b => b.id)} strategy={verticalListSortingStrategy}>
                <div className="max-w-5xl mx-auto py-4 px-4 space-y-2" data-testid="block-canvas">
                  {blocks.map((block) => (
                    <SortableBlock
                      key={block.id}
                      block={block}
                      isSelected={selectedBlock === block.id}
                      onSelect={setSelectedBlock}
                      onUpdate={updateBlock}
                      onDelete={deleteBlock}
                      onOpenStyle={setStyleBlock}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
          )}
        </div>

        {/* Right Sidebar — Style Panel */}
        {selectedBlockData && (
          <div className="w-64 flex-shrink-0 bg-[#0A0A0A] border-l border-white/10 p-3 h-[calc(100vh-53px)] overflow-y-auto sticky top-[53px]" data-testid="style-sidebar">
            <StylePanel
              block={selectedBlockData}
              onUpdate={(updated) => { updateBlock(updated); }}
              onClose={() => setStyleBlock(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default PageBuilderPage;
