import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { Switch } from '../components/ui/switch';
import { Calendar } from '../components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '../components/ui/popover';
import { format } from 'date-fns';
import { 
  Disc, 
  CalendarBlank,
  Sparkle,
  ArrowRight
} from '@phosphor-icons/react';
import { toast } from 'sonner';

const GENRES = [
  'Pop', 'Rock', 'Hip-Hop', 'R&B', 'Electronic', 'Jazz', 'Classical', 
  'Country', 'Folk', 'Reggae', 'Latin', 'Metal', 'Punk', 'Blues',
  'Soul', 'Funk', 'Indie', 'Alternative', 'Dance', 'Ambient'
];

const CreateReleasePage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    release_type: 'single',
    genre: '',
    subgenre: '',
    release_date: new Date(),
    description: '',
    explicit: false,
    language: 'en'
  });

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleAISuggestDescription = async () => {
    if (!formData.title || !formData.genre) {
      toast.error('Please enter a title and genre first');
      return;
    }
    
    setAiLoading(true);
    try {
      const response = await axios.post(`${API}/ai/generate-description`, {
        title: formData.title,
        artist_name: 'Artist', // Will be filled from backend
        genre: formData.genre,
        mood: null
      });
      setFormData({ ...formData, description: response.data.description });
      toast.success('AI description generated!');
    } catch (error) {
      toast.error('Failed to generate description');
    } finally {
      setAiLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.genre) {
      toast.error('Please fill in all required fields');
      return;
    }
    
    setLoading(true);
    try {
      const payload = {
        ...formData,
        release_date: format(formData.release_date, 'yyyy-MM-dd')
      };
      
      const response = await axios.post(`${API}/releases`, payload);
      toast.success('Release created successfully!');
      navigate(`/releases/${response.data.id}`);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to create release';
      toast.error(typeof errorMsg === 'string' ? errorMsg : 'Failed to create release');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto" data-testid="create-release-page">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Create New Release</h1>
          <p className="text-[#A1A1AA] mt-1">Fill in the details for your new release</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Info */}
          <div className="bg-[#141414] border border-white/10 rounded-md p-6">
            <h2 className="text-lg font-medium mb-6 flex items-center gap-2">
              <Disc className="w-5 h-5 text-[#FF3B30]" />
              Basic Information
            </h2>
            
            <div className="space-y-5">
              <div>
                <Label htmlFor="title" className="text-white mb-2 block">
                  Release Title <span className="text-[#FF3B30]">*</span>
                </Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  placeholder="Enter release title"
                  className="bg-[#0A0A0A] border-white/10 text-white placeholder:text-[#71717A]"
                  required
                  data-testid="release-title-input"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Label className="text-white mb-2 block">
                    Release Type <span className="text-[#FF3B30]">*</span>
                  </Label>
                  <Select 
                    value={formData.release_type} 
                    onValueChange={(v) => handleChange('release_type', v)}
                  >
                    <SelectTrigger className="bg-[#0A0A0A] border-white/10 text-white" data-testid="release-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#141414] border-white/10">
                      <SelectItem value="single">Single ($20)</SelectItem>
                      <SelectItem value="ep">EP ($35)</SelectItem>
                      <SelectItem value="album">Album ($50)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-white mb-2 block">
                    Primary Genre <span className="text-[#FF3B30]">*</span>
                  </Label>
                  <Select 
                    value={formData.genre} 
                    onValueChange={(v) => handleChange('genre', v)}
                  >
                    <SelectTrigger className="bg-[#0A0A0A] border-white/10 text-white" data-testid="genre-select">
                      <SelectValue placeholder="Select genre" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#141414] border-white/10 max-h-60">
                      {GENRES.map((genre) => (
                        <SelectItem key={genre} value={genre}>{genre}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="subgenre" className="text-white mb-2 block">
                    Subgenre
                  </Label>
                  <Input
                    id="subgenre"
                    value={formData.subgenre}
                    onChange={(e) => handleChange('subgenre', e.target.value)}
                    placeholder="e.g., Synthwave"
                    className="bg-[#0A0A0A] border-white/10 text-white placeholder:text-[#71717A]"
                    data-testid="subgenre-input"
                  />
                </div>

                <div>
                  <Label className="text-white mb-2 block">
                    Release Date <span className="text-[#FF3B30]">*</span>
                  </Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full justify-start text-left bg-[#0A0A0A] border-white/10 text-white hover:bg-[#141414]"
                        data-testid="release-date-btn"
                      >
                        <CalendarBlank className="mr-2 h-4 w-4" />
                        {format(formData.release_date, 'PPP')}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0 bg-[#141414] border-white/10">
                      <Calendar
                        mode="single"
                        selected={formData.release_date}
                        onSelect={(date) => date && handleChange('release_date', date)}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label htmlFor="description" className="text-white">Description</Label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleAISuggestDescription}
                    disabled={aiLoading}
                    className="text-[#FFCC00] hover:text-[#FFCC00] hover:bg-[#FFCC00]/10"
                    data-testid="ai-description-btn"
                  >
                    {aiLoading ? (
                      <div className="w-4 h-4 border-2 border-[#FFCC00] border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <>
                        <Sparkle className="w-4 h-4 mr-1" />
                        AI Suggest
                      </>
                    )}
                  </Button>
                </div>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="Describe your release..."
                  rows={4}
                  className="bg-[#0A0A0A] border-white/10 text-white placeholder:text-[#71717A]"
                  data-testid="description-textarea"
                />
              </div>

              <div className="flex items-center justify-between p-4 bg-[#0A0A0A] rounded-md">
                <div>
                  <p className="font-medium">Explicit Content</p>
                  <p className="text-sm text-[#71717A]">Mark if contains explicit lyrics</p>
                </div>
                <Switch
                  checked={formData.explicit}
                  onCheckedChange={(checked) => handleChange('explicit', checked)}
                  data-testid="explicit-switch"
                />
              </div>
            </div>
          </div>

          {/* Pricing Info */}
          <div className="bg-[#141414] border border-white/10 rounded-md p-6">
            <h2 className="text-lg font-medium mb-4">Pricing</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-[#A1A1AA]">Release fee ({formData.release_type})</span>
                <span className="font-mono">
                  ${formData.release_type === 'single' ? '20.00' : formData.release_type === 'ep' ? '35.00' : '50.00'}
                </span>
              </div>
              <div className="flex justify-between text-[#22C55E]">
                <span>Your royalties</span>
                <span className="font-mono">100%</span>
              </div>
              <p className="text-xs text-[#71717A] pt-2 border-t border-white/10">
                Or use free tier with 15% revenue share
              </p>
            </div>
          </div>

          {/* Submit */}
          <div className="flex items-center justify-end gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/releases')}
              className="border-white/10 hover:bg-white/5 text-white"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white"
              data-testid="create-release-submit-btn"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  Create Release <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
};

export default CreateReleasePage;
