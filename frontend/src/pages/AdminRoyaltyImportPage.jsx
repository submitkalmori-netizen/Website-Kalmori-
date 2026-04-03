import React, { useEffect, useState, useRef, useCallback } from 'react';
import axios from 'axios';
import { API } from '../App';
import AdminLayout from '../components/AdminLayout';
import { Button } from '../components/ui/button';
import { Upload, FileArrowUp, FileCsv, CheckCircle, WarningCircle, Clock, Eye, X, Plus, Trash, PencilSimple, FloppyDisk, ShieldWarning, CopySimple, ArrowsLeftRight, CalendarBlank, Play, Pause, Timer } from '@phosphor-icons/react';
import { toast } from 'sonner';

const AdminRoyaltyImportPage = () => {
  const [activeSection, setActiveSection] = useState('import');
  const [imports, setImports] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [selectedImport, setSelectedImport] = useState(null);
  const [importDetail, setImportDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [assigningEntry, setAssigningEntry] = useState(null);
  const [assignArtistId, setAssignArtistId] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  // Template editor
  const [showTemplateEditor, setShowTemplateEditor] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [tplName, setTplName] = useState('');
  const [tplNotes, setTplNotes] = useState('');
  const [tplMapping, setTplMapping] = useState({ artist: '', track: '', platform: '', country: '', streams: '', revenue: '', period: '' });
  const [savingTemplate, setSavingTemplate] = useState(false);
  // Reconciliation
  const [reconData, setReconData] = useState(null);
  const [loadingRecon, setLoadingRecon] = useState(false);
  // Schedules
  const [schedules, setSchedules] = useState([]);
  const [loadingSchedules, setLoadingSchedules] = useState(false);
  const [showNewSchedule, setShowNewSchedule] = useState(false);
  const [schedName, setSchedName] = useState('');
  const [schedFrequency, setSchedFrequency] = useState('weekly');
  const [schedTemplateId, setSchedTemplateId] = useState('');
  const [schedArtistId, setSchedArtistId] = useState('');
  const [schedNotes, setSchedNotes] = useState('');
  const [savingSchedule, setSavingSchedule] = useState(false);
  // Bulk actions
  const [selectedDupEntries, setSelectedDupEntries] = useState([]);
  const [bulkResolveStrategy, setBulkResolveStrategy] = useState('keep_latest');
  const [bulkAssignArtist, setBulkAssignArtist] = useState('');
  const [selectedUnmatched, setSelectedUnmatched] = useState([]);
  const [bulkProcessing, setBulkProcessing] = useState(false);

  const fileInputRef = useRef(null);

  const fetchImports = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/admin/royalties/imports`);
      setImports(res.data.imports || []);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  }, []);

  const fetchUsers = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/admin/royalties/users`);
      setAllUsers(res.data.users || []);
    } catch (err) { console.error(err); }
  }, []);

  const fetchTemplates = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/admin/distributor-templates`);
      setTemplates(res.data.templates || []);
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => { fetchImports(); fetchUsers(); fetchTemplates(); }, [fetchImports, fetchUsers, fetchTemplates]);

  const fetchReconciliation = async () => {
    setLoadingRecon(true);
    try {
      const res = await axios.get(`${API}/admin/royalties/reconciliation`);
      setReconData(res.data);
    } catch (err) { toast.error('Failed to load reconciliation data'); }
    finally { setLoadingRecon(false); }
  };

  const fetchSchedules = async () => {
    setLoadingSchedules(true);
    try {
      const res = await axios.get(`${API}/admin/schedules`);
      setSchedules(res.data.schedules || []);
    } catch (err) { toast.error('Failed to load schedules'); }
    finally { setLoadingSchedules(false); }
  };

  const createSchedule = async () => {
    if (!schedName.trim()) { toast.error('Schedule name is required'); return; }
    setSavingSchedule(true);
    try {
      await axios.post(`${API}/admin/schedules`, {
        name: schedName, frequency: schedFrequency,
        template_id: schedTemplateId, artist_id: schedArtistId, notes: schedNotes,
      });
      toast.success('Schedule created');
      setShowNewSchedule(false);
      setSchedName(''); setSchedNotes(''); setSchedTemplateId(''); setSchedArtistId('');
      fetchSchedules();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to create schedule'); }
    finally { setSavingSchedule(false); }
  };

  const toggleSchedule = async (id) => {
    try {
      const res = await axios.put(`${API}/admin/schedules/${id}/toggle`);
      toast.success(`Schedule ${res.data.status}`);
      fetchSchedules();
    } catch (err) { toast.error('Failed to toggle schedule'); }
  };

  const deleteSchedule = async (id) => {
    try {
      await axios.delete(`${API}/admin/schedules/${id}`);
      toast.success('Schedule deleted');
      fetchSchedules();
    } catch (err) { toast.error('Failed to delete schedule'); }
  };

  const checkDueSchedules = async () => {
    try {
      const res = await axios.post(`${API}/admin/schedules/check-due`);
      if (res.data.reminders_sent > 0) toast.success(`${res.data.reminders_sent} reminder(s) sent`);
      else toast.info('No schedules are due right now');
      fetchSchedules();
    } catch (err) { toast.error('Failed to check schedules'); }
  };

  const bulkResolveDuplicates = async (entryIds) => {
    if (!entryIds.length) { toast.error('Select entries to resolve'); return; }
    setBulkProcessing(true);
    try {
      const res = await axios.post(`${API}/admin/royalties/reconciliation/resolve-duplicates`, {
        entry_ids: entryIds, strategy: bulkResolveStrategy,
      });
      toast.success(res.data.message);
      fetchReconciliation();
      setSelectedDupEntries([]);
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to resolve'); }
    finally { setBulkProcessing(false); }
  };

  const bulkAssignUnmatched = async () => {
    if (!selectedUnmatched.length || !bulkAssignArtist) { toast.error('Select entries and an artist'); return; }
    setBulkProcessing(true);
    try {
      const res = await axios.post(`${API}/admin/royalties/reconciliation/bulk-assign`, {
        entry_ids: selectedUnmatched, artist_id: bulkAssignArtist,
      });
      toast.success(res.data.message);
      fetchReconciliation();
      fetchImports();
      setSelectedUnmatched([]);
      setBulkAssignArtist('');
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to assign'); }
    finally { setBulkProcessing(false); }
  };

  const [selectedArtistId, setSelectedArtistId] = useState('');

  useEffect(() => { if (activeSection === 'reconciliation') fetchReconciliation(); }, [activeSection]);
  useEffect(() => { if (activeSection === 'schedules') fetchSchedules(); }, [activeSection]);

  const SUPPORTED_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.pdf'];

  const handleFileUpload = async (file) => {
    if (!file) return;
    const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
    if (!SUPPORTED_EXTENSIONS.includes(ext)) {
      toast.error('Unsupported format. Please upload CSV, XLSX, or PDF.');
      return;
    }
    setImporting(true);
    setImportResult(null);
    const formData = new FormData();
    formData.append('file', file);
    if (selectedTemplateId) formData.append('template_id', selectedTemplateId);
    if (selectedArtistId) formData.append('artist_id', selectedArtistId);
    try {
      const res = await axios.post(`${API}/admin/royalties/import`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImportResult(res.data);
      toast.success(`Import complete: ${res.data.matched} matched, ${res.data.unmatched} unmatched`);
      fetchImports();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Import failed');
    } finally { setImporting(false); }
  };

  const handleDrop = (e) => { e.preventDefault(); setDragOver(false); handleFileUpload(e.dataTransfer.files[0]); };

  const handleViewImport = async (importId) => {
    setSelectedImport(importId);
    setLoadingDetail(true);
    try {
      const res = await axios.get(`${API}/admin/royalties/imports/${importId}`);
      setImportDetail(res.data);
    } catch (err) { toast.error('Failed to load import details'); }
    finally { setLoadingDetail(false); }
  };

  const handleAssign = async (entryId) => {
    if (!assignArtistId) { toast.error('Select a user'); return; }
    try {
      await axios.put(`${API}/admin/royalties/entries/${entryId}/assign`, { artist_id: assignArtistId });
      toast.success('Entry assigned!');
      setAssigningEntry(null); setAssignArtistId('');
      if (selectedImport) handleViewImport(selectedImport);
      fetchImports();
    } catch (err) { toast.error(err.response?.data?.detail || 'Assignment failed'); }
  };

  const openTemplateEditor = (tpl = null) => {
    setEditingTemplate(tpl);
    setTplName(tpl?.name || '');
    setTplNotes(tpl?.notes || '');
    setTplMapping(tpl?.column_mapping || { artist: '', track: '', platform: '', country: '', streams: '', revenue: '', period: '' });
    setShowTemplateEditor(true);
  };

  const handleSaveTemplate = async () => {
    if (!tplName.trim()) { toast.error('Template name is required'); return; }
    if (!tplMapping.artist.trim()) { toast.error('Artist column header is required'); return; }
    setSavingTemplate(true);
    const cleaned = {};
    Object.entries(tplMapping).forEach(([k, v]) => { if (v.trim()) cleaned[k] = v.trim(); });
    try {
      if (editingTemplate) {
        await axios.put(`${API}/admin/distributor-templates/${editingTemplate.id}`, { name: tplName, column_mapping: cleaned, notes: tplNotes });
        toast.success('Template updated');
      } else {
        await axios.post(`${API}/admin/distributor-templates`, { name: tplName, column_mapping: cleaned, notes: tplNotes });
        toast.success('Template created');
      }
      setShowTemplateEditor(false);
      fetchTemplates();
    } catch (err) { toast.error('Failed to save template'); }
    finally { setSavingTemplate(false); }
  };

  const handleDeleteTemplate = async (id) => {
    try {
      await axios.delete(`${API}/admin/distributor-templates/${id}`);
      toast.success('Template deleted');
      fetchTemplates();
    } catch (err) { toast.error('Failed to delete template'); }
  };

  if (loading) return <AdminLayout><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" /></div></AdminLayout>;

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="admin-royalty-import">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Royalty <span className="text-[#E53935]">Import</span></h1>
          <p className="text-gray-400 mt-1">Upload distributor reports, manage templates, and reconcile earnings.</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-1 bg-[#141414] p-1 rounded-xl w-fit border border-white/10">
          {[
            { id: 'import', label: 'Import & Upload' },
            { id: 'templates', label: 'Distributor Templates' },
            { id: 'reconciliation', label: 'Reconciliation' },
            { id: 'schedules', label: 'Schedules' },
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveSection(tab.id)}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeSection === tab.id ? 'bg-[#E53935] text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
              data-testid={`admin-tab-${tab.id}`}>
              {tab.label}
            </button>
          ))}
        </div>

        {/* ===== IMPORT TAB ===== */}
        {activeSection === 'import' && (
          <div className="space-y-6">
            {/* Template Selector + Upload */}
            <div className="bg-[#141414] border border-white/10 rounded-xl p-6" data-testid="admin-import-section">
              <h3 className="text-base font-bold text-white flex items-center gap-2 mb-1">
                <FileArrowUp className="w-5 h-5 text-[#E53935]" /> Upload Distributor Report
              </h3>
              <p className="text-xs text-gray-500 mb-4">Select a template or let the system auto-detect columns.</p>

              {/* Template + Artist Selectors */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-5">
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-[10px] text-gray-500 mb-1">Column Template</label>
                  <select value={selectedTemplateId} onChange={(e) => setSelectedTemplateId(e.target.value)}
                    className="w-full bg-[#0A0A0A] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#E53935]"
                    data-testid="template-selector">
                    <option value="">Auto-detect columns</option>
                    {templates.map(t => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </div>
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-[10px] text-gray-500 mb-1">Assign to Artist <span className="text-gray-600">(for single-artist reports)</span></label>
                  <select value={selectedArtistId} onChange={(e) => setSelectedArtistId(e.target.value)}
                    className="w-full bg-[#0A0A0A] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#E53935]"
                    data-testid="artist-selector">
                    <option value="">Auto-detect from file</option>
                    {allUsers.map(u => (
                      <option key={u.id} value={u.id}>{u.artist_name || u.name} ({u.email})</option>
                    ))}
                  </select>
                </div>
                {(selectedTemplateId || selectedArtistId) && (
                  <div className="flex gap-2 mt-4 sm:mt-0">
                    {selectedTemplateId && <span className="text-xs text-[#E53935] bg-[#E53935]/10 px-2 py-1 rounded-md">Template active</span>}
                    {selectedArtistId && <span className="text-xs text-[#1DB954] bg-[#1DB954]/10 px-2 py-1 rounded-md">Artist selected</span>}
                  </div>
                )}
              </div>

              {/* Drag & Drop */}
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
                  dragOver ? 'border-[#E53935] bg-[#E53935]/5' : 'border-white/10 hover:border-[#E53935]/40 hover:bg-white/[0.02]'
                } ${importing ? 'pointer-events-none opacity-50' : ''}`}
                data-testid="admin-csv-dropzone"
              >
                <input type="file" ref={fileInputRef} accept=".csv,.xlsx,.xls,.pdf" className="hidden"
                  onChange={(e) => { handleFileUpload(e.target.files[0]); e.target.value = ''; }}
                  data-testid="admin-csv-file-input" />
                {importing ? (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-10 h-10 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" />
                    <p className="text-sm text-gray-400">Parsing file and matching users...</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 rounded-2xl bg-[#E53935]/10 flex items-center justify-center">
                      <Upload className="w-8 h-8 text-[#E53935]" />
                    </div>
                    <p className="text-sm font-medium text-white">Drop your file here or <span className="text-[#E53935] font-bold">browse</span></p>
                    <p className="text-xs text-gray-500">Supports CSV, Excel (.xlsx), and PDF files</p>
                  </div>
                )}
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <span className="text-[10px] px-2.5 py-1 rounded-md bg-[#1DB954]/10 text-[#1DB954] border border-[#1DB954]/20 font-bold">CSV</span>
                <span className="text-[10px] px-2.5 py-1 rounded-md bg-[#7C4DFF]/10 text-[#7C4DFF] border border-[#7C4DFF]/20 font-bold">XLSX</span>
                <span className="text-[10px] px-2.5 py-1 rounded-md bg-[#E53935]/10 text-[#E53935] border border-[#E53935]/20 font-bold">PDF</span>
                <span className="text-[10px] text-gray-600 self-center ml-2">|</span>
                {['Artist', 'Track', 'Platform', 'Streams', 'Revenue'].map(col => (
                  <span key={col} className="text-[10px] px-2 py-1 rounded-md bg-white/5 text-gray-400 border border-white/5">{col}</span>
                ))}
                <span className="text-[10px] text-gray-500 self-center ml-1">columns auto-detected</span>
              </div>
            </div>

            {/* Import Result */}
            {importResult && (
              <div className="bg-[#141414] border border-[#E53935]/20 rounded-xl p-6" data-testid="admin-import-result">
                <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-[#1DB954]" /> Import Complete
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                  {[
                    { v: importResult.total_rows, l: 'Total Rows', c: 'text-white', bg: 'bg-white/5' },
                    { v: importResult.matched, l: 'Matched', c: 'text-[#1DB954]', bg: 'bg-[#1DB954]/5' },
                    { v: importResult.unmatched, l: 'Unmatched', c: 'text-[#FF6B6B]', bg: 'bg-[#FF6B6B]/5' },
                    { v: `$${importResult.total_revenue?.toFixed(2)}`, l: 'Revenue', c: 'text-[#FFD700]', bg: 'bg-[#FFD700]/5' },
                  ].map((s, i) => (
                    <div key={i} className={`text-center p-3 ${s.bg} rounded-xl`}>
                      <p className={`text-2xl font-bold font-mono ${s.c}`}>{s.v}</p>
                      <p className="text-[10px] text-gray-500 mt-1">{s.l}</p>
                    </div>
                  ))}
                </div>
                {importResult.column_mapping && (
                  <div className="flex flex-wrap gap-2 pt-3 border-t border-white/5">
                    <span className="text-[10px] text-gray-500">Detected:</span>
                    {importResult.file_format && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#7C4DFF]/10 text-[#7C4DFF] font-bold">
                        Format: {importResult.file_format === 'retail_daily' ? 'Daily Platform Report' : importResult.file_format === 'retail_ranking' ? 'Platform Ranking' : 'Standard'}
                      </span>
                    )}
                    {Object.entries(importResult.column_mapping).map(([field, col]) => (
                      <span key={field} className="text-[10px] px-2 py-0.5 rounded-full bg-[#E53935]/10 text-[#E53935]">{field}: {col}</span>
                    ))}
                  </div>
                )}
                {importResult.unmatched > 0 && importResult.import_id && (
                  <Button onClick={() => handleViewImport(importResult.import_id)}
                    className="mt-4 bg-[#FF6B6B]/10 hover:bg-[#FF6B6B]/20 text-[#FF6B6B] font-bold text-xs gap-2" data-testid="admin-view-unmatched-btn">
                    <WarningCircle className="w-4 h-4" /> Review & Assign Unmatched
                  </Button>
                )}
              </div>
            )}

            {/* Import History */}
            <div className="bg-[#141414] border border-white/10 rounded-xl overflow-hidden" data-testid="admin-import-history">
              <div className="p-5 border-b border-white/10">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Clock className="w-4 h-4 text-[#FFD700]" /> Import History
                </h3>
              </div>
              {imports.length === 0 ? (
                <div className="p-10 text-center">
                  <FileArrowUp className="w-12 h-12 text-white/10 mx-auto mb-3" />
                  <p className="text-sm text-gray-500">No imports yet.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/5 bg-white/5">
                        <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">File</th>
                        <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Template</th>
                        <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Rows</th>
                        <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Matched</th>
                        <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Unmatched</th>
                        <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Revenue</th>
                        <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Date</th>
                        <th className="text-center py-3 px-4 text-xs text-gray-500 font-medium">Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {imports.map(imp => (
                        <tr key={imp.id} className="border-b border-white/5 hover:bg-white/5 transition-colors" data-testid={`admin-import-row-${imp.id}`}>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <FileCsv className="w-4 h-4 text-[#1DB954] flex-shrink-0" />
                              <span className="text-sm text-white truncate max-w-[180px]">{imp.filename}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-xs text-gray-400">{imp.template_used || 'Auto'}</td>
                          <td className="py-3 px-4 text-right text-sm font-mono text-gray-300">{imp.total_rows}</td>
                          <td className="py-3 px-4 text-right text-sm font-mono text-[#1DB954]">{imp.matched}</td>
                          <td className="py-3 px-4 text-right">
                            <span className={`text-sm font-mono ${imp.unmatched > 0 ? 'text-[#FF6B6B]' : 'text-gray-500'}`}>{imp.unmatched}</span>
                          </td>
                          <td className="py-3 px-4 text-right text-sm font-mono text-[#FFD700]">${imp.total_revenue?.toFixed(2)}</td>
                          <td className="py-3 px-4 text-xs text-gray-500">{imp.created_at ? new Date(imp.created_at).toLocaleDateString() : '-'}</td>
                          <td className="py-3 px-4 text-center">
                            <button onClick={() => handleViewImport(imp.id)} className="p-1.5 text-[#E53935] hover:bg-[#E53935]/10 rounded-lg transition-colors"
                              data-testid={`admin-view-import-${imp.id}`}><Eye className="w-4 h-4" /></button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ===== TEMPLATES TAB ===== */}
        {activeSection === 'templates' && (
          <div className="space-y-6" data-testid="templates-section">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Distributor Templates</h3>
                <p className="text-xs text-gray-500 mt-1">Save column mappings for each distributor so future imports are instant.</p>
              </div>
              <Button onClick={() => openTemplateEditor()} className="bg-[#E53935] hover:bg-[#E53935]/80 text-white font-bold text-xs gap-2" data-testid="create-template-btn">
                <Plus className="w-4 h-4" /> New Template
              </Button>
            </div>

            {templates.length === 0 ? (
              <div className="bg-[#141414] border border-white/10 rounded-xl p-10 text-center">
                <FileCsv className="w-12 h-12 text-white/10 mx-auto mb-3" />
                <p className="text-sm text-gray-500 mb-4">No templates yet. Create one for your distributors.</p>
                <Button onClick={() => openTemplateEditor()} className="bg-[#E53935]/10 hover:bg-[#E53935]/20 text-[#E53935] font-bold text-xs gap-2">
                  <Plus className="w-4 h-4" /> Create First Template
                </Button>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {templates.map(tpl => (
                  <div key={tpl.id} className="bg-[#141414] border border-white/10 rounded-xl p-5 hover:border-[#E53935]/30 transition-colors" data-testid={`template-card-${tpl.id}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="text-sm font-bold text-white">{tpl.name}</h4>
                        {tpl.notes && <p className="text-xs text-gray-500 mt-0.5">{tpl.notes}</p>}
                      </div>
                      <div className="flex gap-1">
                        <button onClick={() => openTemplateEditor(tpl)} className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg" data-testid={`edit-template-${tpl.id}`}>
                          <PencilSimple className="w-3.5 h-3.5" />
                        </button>
                        <button onClick={() => handleDeleteTemplate(tpl.id)} className="p-1.5 text-gray-400 hover:text-[#FF6B6B] hover:bg-[#FF6B6B]/10 rounded-lg" data-testid={`delete-template-${tpl.id}`}>
                          <Trash className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {Object.entries(tpl.column_mapping || {}).map(([field, header]) => (
                        <span key={field} className="text-[10px] px-2 py-0.5 rounded-full bg-[#E53935]/10 text-[#E53935]/80">
                          {field} = "{header}"
                        </span>
                      ))}
                    </div>
                    <p className="text-[10px] text-gray-600 mt-3">{tpl.created_at ? new Date(tpl.created_at).toLocaleDateString() : ''}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ===== RECONCILIATION TAB ===== */}
        {activeSection === 'reconciliation' && (
          <div className="space-y-6" data-testid="reconciliation-section">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Smart Reconciliation</h3>
                <p className="text-xs text-gray-500 mt-1">Auto-detect duplicate entries and revenue discrepancies across imports.</p>
              </div>
              <Button onClick={fetchReconciliation} disabled={loadingRecon}
                className="bg-[#E53935] hover:bg-[#E53935]/80 text-white font-bold text-xs gap-2" data-testid="refresh-recon-btn">
                {loadingRecon ? 'Analyzing...' : 'Refresh Analysis'}
              </Button>
            </div>

            {loadingRecon && !reconData ? (
              <div className="bg-[#141414] border border-white/10 rounded-xl p-16 flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" />
              </div>
            ) : reconData ? (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4" data-testid="recon-summary">
                  {[
                    { v: reconData.summary.total_imports, l: 'Total Imports', c: 'text-white' },
                    { v: reconData.summary.total_entries.toLocaleString(), l: 'Total Entries', c: 'text-gray-300' },
                    { v: reconData.summary.duplicate_groups, l: 'Duplicate Groups', c: reconData.summary.duplicate_groups > 0 ? 'text-[#FF6B6B]' : 'text-[#1DB954]' },
                    { v: reconData.summary.discrepancy_groups, l: 'Discrepancies', c: reconData.summary.discrepancy_groups > 0 ? 'text-[#FFD700]' : 'text-[#1DB954]' },
                  ].map((s, i) => (
                    <div key={i} className="bg-[#141414] border border-white/10 rounded-xl p-4 text-center">
                      <p className={`text-2xl font-bold font-mono ${s.c}`}>{s.v}</p>
                      <p className="text-[10px] text-gray-500 mt-1">{s.l}</p>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-[#141414] border border-white/10 rounded-xl p-4 text-center">
                    <p className="text-xl font-bold font-mono text-[#FF6B6B]">${reconData.summary.total_duplicate_revenue?.toFixed(2)}</p>
                    <p className="text-[10px] text-gray-500 mt-1">Potential Duplicate Revenue</p>
                  </div>
                  <div className="bg-[#141414] border border-white/10 rounded-xl p-4 text-center">
                    <p className="text-xl font-bold font-mono text-[#FFD700]">${reconData.summary.total_discrepancy_amount?.toFixed(2)}</p>
                    <p className="text-[10px] text-gray-500 mt-1">Revenue Discrepancy Total</p>
                  </div>
                </div>

                {/* Duplicates Table */}
                <div className="bg-[#141414] border border-white/10 rounded-xl overflow-hidden" data-testid="duplicates-section">
                  <div className="p-5 border-b border-white/10 flex items-center gap-2">
                    <CopySimple className="w-4 h-4 text-[#FF6B6B]" />
                    <h3 className="text-base font-bold text-white">Duplicate Entries</h3>
                    <span className="text-xs bg-[#FF6B6B]/10 text-[#FF6B6B] px-2 py-0.5 rounded-full ml-auto">{reconData.duplicates.length} groups</span>
                  </div>
                  {reconData.duplicates.length > 0 && (
                    <div className="p-4 border-b border-white/5 flex flex-wrap items-center gap-3 bg-[#FF6B6B]/[0.03]" data-testid="bulk-resolve-bar">
                      <select value={bulkResolveStrategy} onChange={e => setBulkResolveStrategy(e.target.value)}
                        className="bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white">
                        <option value="keep_latest">Keep Latest</option>
                        <option value="keep_highest">Keep Highest Revenue</option>
                        <option value="delete_all">Delete All Duplicates</option>
                      </select>
                      <Button size="sm" disabled={bulkProcessing}
                        onClick={() => {
                          const allIds = reconData.duplicates.flatMap(d => d.entry_ids || []);
                          if (allIds.length) bulkResolveDuplicates(allIds);
                          else toast.info('No entry IDs available in duplicate data');
                        }}
                        className="bg-[#FF6B6B] hover:bg-[#FF6B6B]/80 text-white text-xs font-bold gap-1" data-testid="resolve-all-btn">
                        {bulkProcessing ? 'Processing...' : 'Resolve All Duplicates'}
                      </Button>
                    </div>
                  )}
                  {reconData.duplicates.length === 0 ? (
                    <div className="p-8 text-center">
                      <CheckCircle className="w-10 h-10 text-[#1DB954]/20 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">No duplicate entries found. All clean!</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-white/5 bg-white/5">
                            <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Artist</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Track</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Platform</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Period</th>
                            <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Occurrences</th>
                            <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Revenue Each</th>
                            <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Excess</th>
                          </tr>
                        </thead>
                        <tbody>
                          {reconData.duplicates.map((d, i) => (
                            <tr key={i} className="border-b border-white/5 hover:bg-[#FF6B6B]/[0.03] transition-colors" data-testid={`dup-row-${i}`}>
                              <td className="py-3 px-4 text-sm text-white">{d.artist}</td>
                              <td className="py-3 px-4 text-xs text-gray-400">{d.track || '—'}</td>
                              <td className="py-3 px-4 text-xs text-gray-400">{d.platform || '—'}</td>
                              <td className="py-3 px-4 text-xs text-gray-400">{d.period || '—'}</td>
                              <td className="py-3 px-4 text-right text-sm font-mono text-[#FF6B6B]">{d.count}x</td>
                              <td className="py-3 px-4 text-right text-sm font-mono text-gray-300">${d.revenue_per_entry?.toFixed(4)}</td>
                              <td className="py-3 px-4 text-right text-sm font-mono text-[#FF6B6B] font-bold">${d.excess_revenue?.toFixed(4)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                {/* Discrepancies Table */}
                <div className="bg-[#141414] border border-white/10 rounded-xl overflow-hidden" data-testid="discrepancies-section">
                  <div className="p-5 border-b border-white/10 flex items-center gap-2">
                    <ArrowsLeftRight className="w-4 h-4 text-[#FFD700]" />
                    <h3 className="text-base font-bold text-white">Revenue Discrepancies</h3>
                    <span className="text-xs bg-[#FFD700]/10 text-[#FFD700] px-2 py-0.5 rounded-full ml-auto">{reconData.discrepancies.length} groups</span>
                  </div>
                  {reconData.discrepancies.length === 0 ? (
                    <div className="p-8 text-center">
                      <CheckCircle className="w-10 h-10 text-[#1DB954]/20 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">No discrepancies found. Revenue data is consistent!</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-white/5 bg-white/5">
                            <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Artist</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Track</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Platform</th>
                            <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Period</th>
                            <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Min Revenue</th>
                            <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Max Revenue</th>
                            <th className="text-right py-3 px-4 text-xs text-gray-500 font-medium">Difference</th>
                          </tr>
                        </thead>
                        <tbody>
                          {reconData.discrepancies.map((d, i) => (
                            <tr key={i} className="border-b border-white/5 hover:bg-[#FFD700]/[0.03] transition-colors" data-testid={`disc-row-${i}`}>
                              <td className="py-3 px-4 text-sm text-white">{d.artist}</td>
                              <td className="py-3 px-4 text-xs text-gray-400">{d.track || '—'}</td>
                              <td className="py-3 px-4 text-xs text-gray-400">{d.platform || '—'}</td>
                              <td className="py-3 px-4 text-xs text-gray-400">{d.period || '—'}</td>
                              <td className="py-3 px-4 text-right text-sm font-mono text-gray-300">${d.min_revenue?.toFixed(4)}</td>
                              <td className="py-3 px-4 text-right text-sm font-mono text-gray-300">${d.max_revenue?.toFixed(4)}</td>
                              <td className="py-3 px-4 text-right text-sm font-mono text-[#FFD700] font-bold">${d.discrepancy_amount?.toFixed(4)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                {/* Bulk Assign Unmatched */}
                {reconData.summary.unmatched_entries > 0 && (
                  <div className="bg-[#141414] border border-white/10 rounded-xl overflow-hidden" data-testid="bulk-assign-section">
                    <div className="p-5 border-b border-white/10 flex items-center gap-2">
                      <ArrowsLeftRight className="w-4 h-4 text-[#1DB954]" />
                      <h3 className="text-base font-bold text-white">Bulk Assign Unmatched</h3>
                      <span className="text-xs bg-[#1DB954]/10 text-[#1DB954] px-2 py-0.5 rounded-full ml-auto">{reconData.summary.unmatched_entries} unmatched</span>
                    </div>
                    <div className="p-5 flex flex-wrap items-center gap-3">
                      <select value={bulkAssignArtist} onChange={e => setBulkAssignArtist(e.target.value)}
                        className="bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-xs text-white min-w-[200px]" data-testid="bulk-assign-artist-select">
                        <option value="">Select Artist / Producer</option>
                        {allUsers.map(u => (
                          <option key={u.id} value={u.id}>{u.artist_name || u.name || u.email}</option>
                        ))}
                      </select>
                      <Button size="sm" disabled={bulkProcessing || !bulkAssignArtist}
                        onClick={async () => {
                          try {
                            const res = await axios.get(`${API}/admin/royalties/imports`);
                            const unmatched = [];
                            for (const imp of res.data.imports || []) {
                              const detail = await axios.get(`${API}/admin/royalties/imports/${imp.id}`);
                              for (const entry of detail.data.entries || []) {
                                if (entry.status === 'unmatched') unmatched.push(entry.id);
                              }
                            }
                            if (unmatched.length) { setSelectedUnmatched(unmatched); bulkAssignUnmatched(); }
                            else toast.info('No unmatched entries found');
                          } catch { toast.error('Failed to fetch unmatched entries'); setBulkProcessing(false); }
                        }}
                        className="bg-[#1DB954] hover:bg-[#1DB954]/80 text-white text-xs font-bold gap-1" data-testid="bulk-assign-btn">
                        {bulkProcessing ? 'Assigning...' : 'Assign All Unmatched'}
                      </Button>
                      <p className="text-xs text-gray-500">Assigns all unmatched entries to the selected user. Notifications will be sent automatically.</p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-[#141414] border border-white/10 rounded-xl p-10 text-center">
                <ShieldWarning className="w-12 h-12 text-white/10 mx-auto mb-3" />
                <p className="text-sm text-gray-500">Click "Refresh Analysis" to scan your imports.</p>
              </div>
            )}
          </div>
        )}

        {/* ===== SCHEDULES SECTION ===== */}
        {activeSection === 'schedules' && (
          <div className="space-y-6" data-testid="schedules-section">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Import Schedules</h3>
                <p className="text-xs text-gray-500 mt-1">Schedule recurring reminders to upload distributor reports.</p>
              </div>
              <div className="flex items-center gap-2">
                <Button onClick={checkDueSchedules} variant="outline" size="sm"
                  className="border-[#E53935]/30 text-[#E53935] hover:bg-[#E53935]/10 text-xs gap-1" data-testid="check-due-btn">
                  <Timer className="w-4 h-4" /> Check Due
                </Button>
                <Button onClick={() => setShowNewSchedule(true)} size="sm"
                  className="bg-[#E53935] hover:bg-[#E53935]/80 text-white text-xs gap-1" data-testid="new-schedule-btn">
                  <Plus className="w-4 h-4" /> New Schedule
                </Button>
              </div>
            </div>

            {/* Create Schedule Form */}
            {showNewSchedule && (
              <div className="bg-[#141414] border border-[#E53935]/20 rounded-xl p-5 space-y-4" data-testid="new-schedule-form">
                <h4 className="text-sm font-bold text-white">Create Schedule</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Schedule Name *</label>
                    <input value={schedName} onChange={e => setSchedName(e.target.value)}
                      placeholder="e.g. Weekly CD Baby Import"
                      className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-[#E53935]/50 focus:outline-none"
                      data-testid="sched-name-input" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Frequency *</label>
                    <select value={schedFrequency} onChange={e => setSchedFrequency(e.target.value)}
                      className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white" data-testid="sched-freq-select">
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Distributor Template</label>
                    <select value={schedTemplateId} onChange={e => setSchedTemplateId(e.target.value)}
                      className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white" data-testid="sched-template-select">
                      <option value="">None</option>
                      {templates.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Target Artist / Producer</label>
                    <select value={schedArtistId} onChange={e => setSchedArtistId(e.target.value)}
                      className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white" data-testid="sched-artist-select">
                      <option value="">All Artists</option>
                      {allUsers.map(u => <option key={u.id} value={u.id}>{u.artist_name || u.name || u.email}</option>)}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Notes</label>
                  <input value={schedNotes} onChange={e => setSchedNotes(e.target.value)} placeholder="Optional notes"
                    className="w-full bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-[#E53935]/50 focus:outline-none"
                    data-testid="sched-notes-input" />
                </div>
                <div className="flex items-center gap-3">
                  <Button onClick={createSchedule} disabled={savingSchedule}
                    className="bg-[#E53935] hover:bg-[#E53935]/80 text-white text-xs font-bold gap-1" data-testid="save-schedule-btn">
                    <FloppyDisk className="w-4 h-4" /> {savingSchedule ? 'Saving...' : 'Save Schedule'}
                  </Button>
                  <Button variant="ghost" onClick={() => setShowNewSchedule(false)} className="text-xs text-gray-400">Cancel</Button>
                </div>
              </div>
            )}

            {/* Schedules List */}
            {loadingSchedules ? (
              <div className="bg-[#141414] border border-white/10 rounded-xl p-16 flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" />
              </div>
            ) : schedules.length === 0 ? (
              <div className="bg-[#141414] border border-white/10 rounded-xl p-10 text-center">
                <CalendarBlank className="w-12 h-12 text-white/10 mx-auto mb-3" />
                <p className="text-sm text-gray-500">No schedules yet. Create one to get recurring import reminders.</p>
              </div>
            ) : (
              <div className="space-y-3" data-testid="schedules-list">
                {schedules.map(s => (
                  <div key={s.id} className={`bg-[#141414] border rounded-xl p-5 flex items-center gap-4 ${s.overdue ? 'border-[#FF6B6B]/40 bg-[#FF6B6B]/[0.03]' : 'border-white/10'}`}
                    data-testid={`schedule-${s.id}`}>
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${s.status === 'active' ? 'bg-[#1DB954]/10' : 'bg-gray-800'}`}>
                      {s.status === 'active'
                        ? <CalendarBlank className="w-5 h-5 text-[#1DB954]" />
                        : <Pause className="w-5 h-5 text-gray-500" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-bold text-white truncate">{s.name}</h4>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${s.status === 'active' ? 'bg-[#1DB954]/10 text-[#1DB954]' : 'bg-gray-800 text-gray-500'}`}>
                          {s.status}
                        </span>
                        {s.overdue && <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#FF6B6B]/10 text-[#FF6B6B] font-bold">OVERDUE</span>}
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {s.frequency} {s.artist_name ? `· ${s.artist_name}` : ''} {s.template_name ? `· ${s.template_name}` : ''}
                      </p>
                      <p className="text-[10px] text-gray-600 mt-0.5">
                        Next due: {s.next_due ? new Date(s.next_due).toLocaleDateString() : '—'} · Runs: {s.run_count}
                        {s.notes && <span className="ml-2 italic">"{s.notes}"</span>}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <button onClick={() => toggleSchedule(s.id)} title={s.status === 'active' ? 'Pause' : 'Resume'}
                        className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors" data-testid={`toggle-${s.id}`}>
                        {s.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      </button>
                      <button onClick={() => deleteSchedule(s.id)} title="Delete"
                        className="p-2 rounded-lg hover:bg-[#FF6B6B]/10 text-gray-400 hover:text-[#FF6B6B] transition-colors" data-testid={`delete-${s.id}`}>
                        <Trash className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ===== IMPORT DETAIL MODAL ===== */}
        {selectedImport && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => { setSelectedImport(null); setImportDetail(null); }} data-testid="admin-import-detail-modal">
            <div className="bg-[#0A0A0A] border border-white/10 rounded-2xl max-w-5xl w-full max-h-[85vh] overflow-hidden" onClick={e => e.stopPropagation()}>
              <div className="p-5 border-b border-white/10 flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">Import Details</h3>
                  {importDetail?.import && <p className="text-xs text-gray-500 mt-0.5">{importDetail.import.filename} — {importDetail.import.total_rows} rows</p>}
                </div>
                <button onClick={() => { setSelectedImport(null); setImportDetail(null); }}
                  className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg" data-testid="admin-close-import-detail">
                  <X className="w-5 h-5" />
                </button>
              </div>
              {loadingDetail ? (
                <div className="flex items-center justify-center py-16">
                  <div className="w-8 h-8 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : importDetail ? (
                <div className="overflow-auto max-h-[calc(85vh-80px)]">
                  <div className="grid grid-cols-4 gap-4 p-5 border-b border-white/5">
                    {[
                      { v: importDetail.import?.total_rows, l: 'Total', c: 'text-white' },
                      { v: importDetail.import?.matched, l: 'Matched', c: 'text-[#1DB954]' },
                      { v: importDetail.import?.unmatched, l: 'Unmatched', c: 'text-[#FF6B6B]' },
                      { v: `$${importDetail.import?.total_revenue?.toFixed(2)}`, l: 'Revenue', c: 'text-[#FFD700]' },
                    ].map((s, i) => (
                      <div key={i} className="text-center">
                        <p className={`text-lg font-bold font-mono ${s.c}`}>{s.v}</p>
                        <p className="text-[10px] text-gray-500">{s.l}</p>
                      </div>
                    ))}
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="sticky top-0">
                        <tr className="border-b border-white/5 bg-[#0A0A0A]">
                          {['Status', 'Artist (Raw)', 'Matched To', 'Track', 'Platform', 'Streams', 'Revenue', 'Action'].map(h => (
                            <th key={h} className={`py-3 px-4 text-xs text-gray-500 font-medium ${h === 'Streams' || h === 'Revenue' ? 'text-right' : h === 'Action' ? 'text-center' : 'text-left'}`}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {importDetail.entries?.map(entry => (
                          <tr key={entry.id} className={`border-b border-white/5 transition-colors ${entry.status === 'unmatched' ? 'bg-[#FF6B6B]/[0.03]' : 'hover:bg-white/5'}`}
                            data-testid={`admin-entry-row-${entry.id}`}>
                            <td className="py-3 px-4">
                              {entry.status === 'matched' ? (
                                <span className="inline-flex items-center gap-1 text-xs text-[#1DB954]"><CheckCircle className="w-3.5 h-3.5" weight="fill" /> Matched</span>
                              ) : (
                                <span className="inline-flex items-center gap-1 text-xs text-[#FF6B6B]"><WarningCircle className="w-3.5 h-3.5" weight="fill" /> Unmatched</span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-300">{entry.artist_name_raw}</td>
                            <td className="py-3 px-4 text-sm text-white">{entry.matched_artist_name || <span className="text-gray-500 italic">—</span>}</td>
                            <td className="py-3 px-4 text-xs text-gray-400 max-w-[140px] truncate">{entry.track || '—'}</td>
                            <td className="py-3 px-4 text-xs text-gray-400">{entry.platform || '—'}</td>
                            <td className="py-3 px-4 text-right text-sm font-mono text-gray-300">{entry.streams?.toLocaleString()}</td>
                            <td className="py-3 px-4 text-right text-sm font-mono text-[#FFD700]">${entry.revenue?.toFixed(4)}</td>
                            <td className="py-3 px-4 text-center">
                              {entry.status === 'unmatched' && (
                                assigningEntry === entry.id ? (
                                  <div className="flex items-center gap-2 justify-center">
                                    <select value={assignArtistId} onChange={(e) => setAssignArtistId(e.target.value)}
                                      className="bg-[#141414] border border-white/10 rounded-lg px-2 py-1.5 text-xs text-white focus:outline-none focus:border-[#E53935] max-w-[160px]"
                                      data-testid={`admin-assign-select-${entry.id}`}>
                                      <option value="">Select user</option>
                                      {allUsers.map(u => (
                                        <option key={u.id} value={u.id}>{u.artist_name || u.name} ({u.email})</option>
                                      ))}
                                    </select>
                                    <button onClick={() => handleAssign(entry.id)} className="p-1 text-[#1DB954] hover:bg-[#1DB954]/10 rounded" data-testid={`admin-confirm-assign-${entry.id}`}>
                                      <CheckCircle className="w-4 h-4" />
                                    </button>
                                    <button onClick={() => { setAssigningEntry(null); setAssignArtistId(''); }} className="p-1 text-gray-500 hover:bg-white/10 rounded">
                                      <X className="w-4 h-4" />
                                    </button>
                                  </div>
                                ) : (
                                  <button onClick={() => { setAssigningEntry(entry.id); setAssignArtistId(''); }}
                                    className="text-xs text-[#E53935] hover:text-[#E53935]/80 underline underline-offset-2 font-medium"
                                    data-testid={`admin-assign-btn-${entry.id}`}>Assign</button>
                                )
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}

        {/* ===== TEMPLATE EDITOR MODAL ===== */}
        {showTemplateEditor && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowTemplateEditor(false)} data-testid="template-editor-modal">
            <div className="bg-[#0A0A0A] border border-white/10 rounded-2xl max-w-lg w-full" onClick={e => e.stopPropagation()}>
              <div className="p-5 border-b border-white/10 flex items-center justify-between">
                <h3 className="text-base font-bold text-white">{editingTemplate ? 'Edit' : 'Create'} Template</h3>
                <button onClick={() => setShowTemplateEditor(false)} className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-5 space-y-4">
                <div>
                  <label className="block text-xs text-gray-400 mb-1.5">Distributor Name *</label>
                  <input value={tplName} onChange={(e) => setTplName(e.target.value)} placeholder="e.g., CD Baby, DistroKid, RouteNote"
                    className="w-full bg-[#141414] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:outline-none focus:border-[#E53935]"
                    data-testid="template-name-input" />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1.5">Notes (optional)</label>
                  <input value={tplNotes} onChange={(e) => setTplNotes(e.target.value)} placeholder="e.g., Monthly report format"
                    className="w-full bg-[#141414] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:outline-none focus:border-[#E53935]"
                    data-testid="template-notes-input" />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-3">Column Header Mappings</label>
                  <p className="text-[10px] text-gray-600 mb-3">Enter the exact header name from the distributor's CSV for each field.</p>
                  <div className="space-y-2">
                    {['artist', 'track', 'platform', 'country', 'streams', 'revenue', 'period'].map(field => (
                      <div key={field} className="flex items-center gap-3">
                        <span className="text-xs text-gray-400 w-20 text-right capitalize">{field}{field === 'artist' ? ' *' : ''}</span>
                        <input value={tplMapping[field] || ''} onChange={(e) => setTplMapping(p => ({ ...p, [field]: e.target.value }))}
                          placeholder={`CSV header for ${field}`}
                          className="flex-1 bg-[#141414] border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder:text-gray-600 focus:outline-none focus:border-[#E53935]"
                          data-testid={`template-field-${field}`} />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="p-5 border-t border-white/10 flex justify-end gap-3">
                <Button onClick={() => setShowTemplateEditor(false)} variant="outline" className="text-xs border-white/10 text-gray-400 hover:text-white">Cancel</Button>
                <Button onClick={handleSaveTemplate} disabled={savingTemplate}
                  className="bg-[#E53935] hover:bg-[#E53935]/80 text-white font-bold text-xs gap-2" data-testid="save-template-btn">
                  <FloppyDisk className="w-4 h-4" /> {savingTemplate ? 'Saving...' : editingTemplate ? 'Update' : 'Create'} Template
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminRoyaltyImportPage;
