import React, { useState, useEffect, useCallback, useRef } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { ChatCircle, PaperPlaneTilt, User, ArrowLeft, Paperclip, FileArrowDown, Play, Pause, Checks, Check } from '@phosphor-icons/react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

function AudioPlayer({ src, fileName }) {
  const [playing, setPlaying] = useState(false);
  const audioRef = useRef(null);
  const togglePlay = () => {
    if (!audioRef.current) return;
    playing ? audioRef.current.pause() : audioRef.current.play().catch(() => {});
    setPlaying(!playing);
  };
  useEffect(() => {
    const a = audioRef.current;
    if (!a) return;
    const onEnd = () => setPlaying(false);
    a.addEventListener('ended', onEnd);
    return () => a.removeEventListener('ended', onEnd);
  }, []);
  const audioSrc = src.startsWith('http') ? src : `${API}/api/messages/file/${src}`;
  return (
    <div className="flex items-center gap-3 bg-black/30 rounded-lg p-2.5 min-w-[220px]">
      <audio ref={audioRef} src={audioSrc} preload="none" />
      <button onClick={togglePlay} className="w-9 h-9 rounded-full bg-[#7C4DFF] flex items-center justify-center shrink-0 hover:brightness-110" data-testid="audio-play-btn">
        {playing ? <Pause className="w-4 h-4 text-white" weight="fill" /> : <Play className="w-4 h-4 text-white" weight="fill" />}
      </button>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium truncate">{fileName}</p>
        <p className="text-[10px] text-gray-500">Audio file</p>
      </div>
    </div>
  );
}

function FileAttachment({ msg, isMe }) {
  const fileUrl = msg.file_url?.startsWith('http') ? msg.file_url : `${API}/api/messages/file/${msg.file_url}`;
  const formatSize = (bytes) => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };
  if (msg.file_type === 'audio') return <AudioPlayer src={msg.file_url} fileName={msg.file_name} />;
  if (msg.file_type === 'image') {
    return (
      <div className="space-y-1.5">
        <img src={fileUrl} alt={msg.file_name} className="max-w-[280px] rounded-lg border border-white/10" loading="lazy" />
        <p className="text-[10px] opacity-60">{msg.file_name} &middot; {formatSize(msg.file_size)}</p>
      </div>
    );
  }
  return (
    <a href={fileUrl} target="_blank" rel="noopener noreferrer"
      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg border ${isMe ? 'border-white/20 bg-white/10' : 'border-[#333] bg-[#0a0a0a]'} hover:brightness-110 transition`}
      data-testid="file-download-link">
      <FileArrowDown className="w-5 h-5 shrink-0" />
      <div className="min-w-0">
        <p className="text-xs font-medium truncate">{msg.file_name}</p>
        <p className="text-[10px] opacity-60">{formatSize(msg.file_size)}</p>
      </div>
    </a>
  );
}

function ReadReceipt({ msg, isMe }) {
  if (!isMe || msg.sender_id === 'system') return null;
  return (
    <span className="inline-flex items-center ml-1" data-testid={`receipt-${msg.id}`}>
      {msg.read ? (
        <Checks className="w-3.5 h-3.5 text-[#7C4DFF]" weight="bold" />
      ) : (
        <Check className="w-3.5 h-3.5 text-white/40" weight="bold" />
      )}
    </span>
  );
}

function TypingIndicator({ name }) {
  return (
    <div className="flex justify-start" data-testid="typing-indicator">
      <div className="bg-[#1a1a1a] border border-[#222] rounded-2xl rounded-bl-md px-4 py-2.5">
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-gray-400">{name} is typing</span>
          <span className="flex gap-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }} />
          </span>
        </div>
      </div>
    </div>
  );
}

export default function MessagesPage() {
  const [conversations, setConversations] = useState([]);
  const [activeConvo, setActiveConvo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [otherTyping, setOtherTyping] = useState(false);
  const [newMsg, setNewMsg] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef(null);
  const pollRef = useRef(null);
  const typingRef = useRef(null);
  const fileInputRef = useRef(null);

  const token = localStorage.getItem('token') || localStorage.getItem('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  const userId = (() => {
    try { return JSON.parse(atob(token.split('.')[1])).sub; } catch { return ''; }
  })();

  const fetchConversations = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/messages/conversations`, { headers });
      if (res.ok) setConversations(await res.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [token]);

  const fetchMessages = useCallback(async (convoId) => {
    try {
      const res = await fetch(`${API}/api/messages/${convoId}`, { headers });
      if (res.ok) {
        const data = await res.json();
        // Handle both old format (array) and new format ({messages, typing})
        if (Array.isArray(data)) {
          setMessages(data);
          setOtherTyping(false);
        } else {
          setMessages(data.messages || []);
          setOtherTyping((data.typing || []).length > 0);
        }
        setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
      }
    } catch (e) { console.error(e); }
  }, [token]);

  useEffect(() => { fetchConversations(); }, [fetchConversations]);

  useEffect(() => {
    if (!activeConvo) return;
    fetchMessages(activeConvo);
    pollRef.current = setInterval(() => {
      fetchMessages(activeConvo);
      fetchConversations();
    }, 3000);
    return () => clearInterval(pollRef.current);
  }, [activeConvo, fetchMessages, fetchConversations]);

  const sendTypingSignal = useCallback(() => {
    if (!activeConvo) return;
    // Throttle: send at most once per 2 seconds
    if (typingRef.current) return;
    typingRef.current = true;
    fetch(`${API}/api/messages/${activeConvo}/typing`, {
      method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' },
    }).catch(() => {});
    setTimeout(() => { typingRef.current = false; }, 2000);
  }, [activeConvo, token]);

  const handleSend = async () => {
    if (!newMsg.trim() || !activeConvo) return;
    setSending(true);
    try {
      const res = await fetch(`${API}/api/messages/${activeConvo}`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: newMsg }),
      });
      if (res.ok) {
        setNewMsg('');
        fetchMessages(activeConvo);
        fetchConversations();
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed to send');
      }
    } catch (e) { toast.error('Failed to send message'); }
    setSending(false);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !activeConvo) return;
    if (file.size > 50 * 1024 * 1024) { toast.error('File too large. Max 50MB.'); return; }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API}/api/messages/${activeConvo}/upload`, {
        method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: formData,
      });
      if (res.ok) { toast.success('File shared!'); fetchMessages(activeConvo); fetchConversations(); }
      else { const err = await res.json(); toast.error(err.detail || 'Upload failed'); }
    } catch (e) { toast.error('Upload failed'); }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleInputChange = (e) => {
    setNewMsg(e.target.value);
    sendTypingSignal();
  };

  const activeConvoData = conversations.find(c => c.id === activeConvo);

  const formatTime = (iso) => {
    if (!iso) return '';
    const d = new Date(iso);
    const now = new Date();
    const diff = now - d;
    if (diff < 60000) return 'just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-100px)] flex" data-testid="messages-page">
        {/* Conversation List */}
        <div className={`${activeConvo ? 'hidden md:flex' : 'flex'} flex-col w-full md:w-80 border-r border-[#222] bg-[#0a0a0a]`}>
          <div className="p-4 border-b border-[#222]">
            <h2 className="text-white font-bold text-lg" data-testid="messages-title">Messages</h2>
            <p className="text-gray-500 text-xs mt-0.5">Chat with your collaborators</p>
          </div>
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="p-6 text-center text-gray-500 text-sm">Loading...</div>
            ) : conversations.length === 0 ? (
              <div className="p-6 text-center">
                <ChatCircle className="w-10 h-10 text-gray-600 mx-auto mb-2" />
                <p className="text-gray-400 text-sm">No conversations yet</p>
                <p className="text-gray-600 text-xs mt-1">Accept a collab invite to start chatting</p>
              </div>
            ) : conversations.map(c => (
              <button key={c.id} onClick={() => setActiveConvo(c.id)}
                className={`w-full p-3 flex items-center gap-3 border-b border-[#181818] text-left transition hover:bg-[#151515] ${activeConvo === c.id ? 'bg-[#151515] border-l-2 border-l-[#7C4DFF]' : ''}`}
                data-testid={`convo-${c.id}`}>
                <div className="w-10 h-10 rounded-full bg-[#7C4DFF]/20 flex items-center justify-center shrink-0">
                  <User className="w-5 h-5 text-[#7C4DFF]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-white text-sm font-medium truncate">{c.other_user?.artist_name || 'Unknown'}</p>
                    <span className="text-[10px] text-gray-600 shrink-0">{formatTime(c.last_message?.created_at)}</span>
                  </div>
                  <p className="text-gray-500 text-xs truncate">
                    {c.last_message?.file_url ? (c.last_message?.file_type === 'audio' ? 'Shared an audio file' : 'Shared a file') : c.last_message?.text || c.post_title}
                  </p>
                </div>
                {c.unread_count > 0 && (
                  <span className="w-5 h-5 rounded-full bg-[#7C4DFF] text-white text-[10px] font-bold flex items-center justify-center shrink-0" data-testid={`unread-${c.id}`}>
                    {c.unread_count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div className={`${!activeConvo ? 'hidden md:flex' : 'flex'} flex-col flex-1 bg-black`}>
          {!activeConvo ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <ChatCircle className="w-16 h-16 text-gray-700 mx-auto mb-3" />
                <p className="text-gray-400 text-lg font-medium">Select a conversation</p>
                <p className="text-gray-600 text-sm mt-1">Pick a collaborator to start messaging</p>
              </div>
            </div>
          ) : (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-[#222] flex items-center gap-3">
                <button onClick={() => setActiveConvo(null)} className="md:hidden text-gray-400 hover:text-white" data-testid="back-btn">
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <div className="w-9 h-9 rounded-full bg-[#E040FB]/20 flex items-center justify-center">
                  <User className="w-4 h-4 text-[#E040FB]" />
                </div>
                <div>
                  <p className="text-white font-semibold text-sm" data-testid="chat-partner-name">
                    {activeConvoData?.other_user?.artist_name || 'Collaborator'}
                  </p>
                  <p className="text-gray-500 text-xs">
                    {otherTyping ? (
                      <span className="text-[#7C4DFF]" data-testid="header-typing">typing...</span>
                    ) : activeConvoData?.post_title}
                  </p>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3" data-testid="messages-list">
                {messages.map(msg => {
                  const isMe = msg.sender_id === userId;
                  const isSystem = msg.sender_id === 'system';
                  if (isSystem) {
                    return (
                      <div key={msg.id} className="flex justify-center">
                        <span className="px-3 py-1.5 rounded-full bg-[#7C4DFF]/10 text-[#7C4DFF] text-xs border border-[#7C4DFF]/20">
                          {msg.text}
                        </span>
                      </div>
                    );
                  }
                  return (
                    <div key={msg.id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`} data-testid={`msg-${msg.id}`}>
                      <div className={`max-w-[70%] rounded-2xl px-4 py-2.5 ${
                        isMe ? 'bg-[#7C4DFF] text-white rounded-br-md' : 'bg-[#1a1a1a] text-gray-200 border border-[#222] rounded-bl-md'
                      }`}>
                        {msg.file_url ? (
                          <FileAttachment msg={msg} isMe={isMe} />
                        ) : (
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.text}</p>
                        )}
                        <div className={`flex items-center gap-0.5 mt-1 ${isMe ? 'justify-end' : ''}`}>
                          <span className={`text-[10px] ${isMe ? 'text-white/50' : 'text-gray-600'}`}>
                            {formatTime(msg.created_at)}
                          </span>
                          <ReadReceipt msg={msg} isMe={isMe} />
                        </div>
                      </div>
                    </div>
                  );
                })}
                {otherTyping && (
                  <TypingIndicator name={activeConvoData?.other_user?.artist_name || 'Someone'} />
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-[#222]">
                {uploading && (
                  <div className="mb-2 px-3 py-1.5 bg-[#7C4DFF]/10 border border-[#7C4DFF]/20 rounded-lg text-[#7C4DFF] text-xs flex items-center gap-2">
                    <div className="w-3 h-3 border-2 border-[#7C4DFF] border-t-transparent rounded-full animate-spin" />
                    Uploading file...
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden"
                    accept="audio/*,image/*,.pdf,.zip,.wav,.mp3,.flac,.aif,.aiff,.stem,.txt,.doc,.docx" data-testid="file-input" />
                  <button onClick={() => fileInputRef.current?.click()} disabled={uploading}
                    className="w-10 h-10 rounded-xl bg-[#1a1a1a] border border-[#333] text-gray-400 flex items-center justify-center hover:text-white hover:border-[#7C4DFF] disabled:opacity-40 transition"
                    data-testid="attach-file-btn" title="Share file or audio">
                    <Paperclip className="w-5 h-5" />
                  </button>
                  <input type="text" value={newMsg} onChange={handleInputChange} onKeyDown={handleKeyDown}
                    placeholder="Type a message..."
                    className="flex-1 bg-[#111] border border-[#333] rounded-xl px-4 py-2.5 text-white text-sm focus:outline-none focus:border-[#7C4DFF] placeholder-gray-600"
                    data-testid="message-input" disabled={sending || uploading} />
                  <button onClick={handleSend} disabled={!newMsg.trim() || sending}
                    className="w-10 h-10 rounded-xl bg-[#7C4DFF] text-white flex items-center justify-center hover:brightness-110 disabled:opacity-40 transition"
                    data-testid="send-message-btn">
                    <PaperPlaneTilt className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
