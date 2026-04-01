import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  Disc, 
  Plus, 
  MagnifyingGlass,
  DotsThree,
  Clock,
  CheckCircle,
  Warning
} from '@phosphor-icons/react';

const ReleasesPage = () => {
  const [releases, setReleases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchReleases();
  }, []);

  const fetchReleases = async () => {
    try {
      const response = await axios.get(`${API}/releases`);
      setReleases(response.data);
    } catch (error) {
      console.error('Failed to fetch releases:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredReleases = releases.filter(release => {
    const matchesFilter = filter === 'all' || release.status === filter;
    const matchesSearch = release.title.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'distributed':
        return <CheckCircle className="w-4 h-4 text-[#22C55E]" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-[#FFCC00]" />;
      case 'draft':
        return <Warning className="w-4 h-4 text-[#71717A]" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'distributed':
        return 'bg-[#22C55E]/10 text-[#22C55E]';
      case 'processing':
        return 'bg-[#FFCC00]/10 text-[#FFCC00]';
      case 'draft':
        return 'bg-[#71717A]/10 text-[#71717A]';
      default:
        return 'bg-[#71717A]/10 text-[#71717A]';
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-[#FF3B30] border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="releases-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Releases</h1>
            <p className="text-[#A1A1AA] mt-1">Manage your music catalog</p>
          </div>
          <Link to="/releases/new">
            <Button className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white" data-testid="create-release-btn">
              <Plus className="w-4 h-4 mr-2" /> New Release
            </Button>
          </Link>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <MagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#71717A]" />
            <Input
              placeholder="Search releases..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 bg-[#141414] border-white/10 text-white placeholder:text-[#71717A]"
              data-testid="search-releases-input"
            />
          </div>
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="w-full sm:w-40 bg-[#141414] border-white/10 text-white" data-testid="filter-select">
              <SelectValue placeholder="Filter" />
            </SelectTrigger>
            <SelectContent className="bg-[#141414] border-white/10">
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="distributed">Distributed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Releases List */}
        {filteredReleases.length === 0 ? (
          <div className="bg-[#141414] border border-white/10 rounded-md p-12 text-center">
            <Disc className="w-16 h-16 text-[#71717A] mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No releases found</h3>
            <p className="text-[#A1A1AA] mb-6">
              {releases.length === 0 
                ? "Create your first release to start distributing your music"
                : "No releases match your search criteria"
              }
            </p>
            {releases.length === 0 && (
              <Link to="/releases/new">
                <Button className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white">
                  <Plus className="w-4 h-4 mr-2" /> Create Release
                </Button>
              </Link>
            )}
          </div>
        ) : (
          <div className="bg-[#141414] border border-white/10 rounded-md overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-wider text-[#A1A1AA]">Release</th>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-wider text-[#A1A1AA] hidden md:table-cell">Type</th>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-wider text-[#A1A1AA] hidden lg:table-cell">UPC</th>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-wider text-[#A1A1AA]">Status</th>
                  <th className="px-6 py-4 text-left text-xs uppercase tracking-wider text-[#A1A1AA] hidden sm:table-cell">Tracks</th>
                  <th className="px-6 py-4"></th>
                </tr>
              </thead>
              <tbody>
                {filteredReleases.map((release) => (
                  <tr 
                    key={release.id}
                    className="border-b border-white/5 hover:bg-white/2 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <Link to={`/releases/${release.id}`} className="flex items-center gap-3 hover:text-[#FF3B30] transition-colors">
                        <div className="w-10 h-10 bg-[#1E1E1E] rounded flex items-center justify-center flex-shrink-0">
                          {release.cover_art_url ? (
                            <img src={`${API.replace('/api', '')}/api/files/${release.cover_art_url}`} alt="" className="w-full h-full object-cover rounded" />
                          ) : (
                            <Disc className="w-5 h-5 text-[#A1A1AA]" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium">{release.title}</p>
                          <p className="text-xs text-[#71717A]">{release.genre}</p>
                        </div>
                      </Link>
                    </td>
                    <td className="px-6 py-4 hidden md:table-cell">
                      <span className="capitalize text-sm text-[#A1A1AA]">{release.release_type}</span>
                    </td>
                    <td className="px-6 py-4 hidden lg:table-cell">
                      <span className="font-mono text-xs text-[#71717A]">{release.upc}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs capitalize ${getStatusColor(release.status)}`}>
                        {getStatusIcon(release.status)}
                        {release.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 hidden sm:table-cell">
                      <span className="text-sm text-[#A1A1AA]">{release.track_count}</span>
                    </td>
                    <td className="px-6 py-4">
                      <Link to={`/releases/${release.id}`}>
                        <Button variant="ghost" size="sm" className="text-[#A1A1AA] hover:text-white">
                          <DotsThree className="w-5 h-5" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default ReleasesPage;
