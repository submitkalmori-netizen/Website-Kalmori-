import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import AdminLayout from '../components/AdminLayout';
import { Users, MagnifyingGlass, CaretLeft, CaretRight, PencilSimple, X } from '@phosphor-icons/react';
import { Button } from '../components/ui/button';

const AdminUsersPage = () => {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [editUser, setEditUser] = useState(null);
  const [editForm, setEditForm] = useState({ role: '', plan: '', status: '' });
  const [saving, setSaving] = useState(false);

  const fetchUsers = async (p = 1, q = '') => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: p, limit: 15 });
      if (q) params.append('search', q);
      const res = await axios.get(`${API}/admin/users?${params}`);
      setUsers(res.data.users);
      setTotal(res.data.total);
      setPages(res.data.pages);
      setPage(p);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchUsers(1, search); }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchUsers(1, search);
  };

  const openEdit = (user) => {
    setEditUser(user);
    setEditForm({ role: user.role, plan: user.plan, status: user.status || 'active' });
  };

  const handleSave = async () => {
    if (!editUser) return;
    setSaving(true);
    try {
      await axios.put(`${API}/admin/users/${editUser.id}`, editForm);
      setEditUser(null);
      fetchUsers(page, search);
    } catch (err) { console.error(err); alert(err.response?.data?.detail || 'Update failed'); }
    finally { setSaving(false); }
  };

  const planColor = (p) => {
    if (p === 'pro') return 'bg-[#E040FB]/10 text-[#E040FB]';
    if (p === 'rise') return 'bg-[#FFD700]/10 text-[#FFD700]';
    return 'bg-gray-600/20 text-gray-400';
  };

  const roleColor = (r) => {
    if (r === 'admin') return 'text-[#E53935]';
    return 'text-gray-400';
  };

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="admin-users">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">User <span className="text-[#E53935]">Management</span></h1>
            <p className="text-gray-400 mt-1">Manage platform users and permissions</p>
          </div>
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <div className="relative">
              <MagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                placeholder="Search users..." className="pl-9 pr-4 py-2 text-sm rounded-lg w-64"
                data-testid="user-search-input" />
            </div>
            <Button type="submit" className="bg-[#E53935] hover:bg-[#d32f2f] text-white text-sm" data-testid="user-search-btn">Search</Button>
          </form>
        </div>

        <div className="card-kalmori overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12"><div className="w-6 h-6 border-2 border-[#E53935] border-t-transparent rounded-full animate-spin" /></div>
          ) : users.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-3 text-gray-600" />
              <p>No users found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="users-table">
                <thead>
                  <tr className="border-b border-white/10 bg-white/5">
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">User</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Email</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Role</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Plan</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Releases</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Joined</th>
                    <th className="text-left py-3 px-4 text-xs text-gray-500 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#7C4DFF] to-[#E040FB] flex items-center justify-center text-xs font-bold text-white">
                            {u.name?.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <p className="text-sm font-medium">{u.artist_name || u.name}</p>
                            <p className="text-xs text-gray-500">{u.name}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-400">{u.email}</td>
                      <td className="py-3 px-4 text-sm capitalize"><span className={roleColor(u.role)}>{u.role}</span></td>
                      <td className="py-3 px-4"><span className={`text-xs px-2 py-1 rounded-full capitalize ${planColor(u.plan)}`}>{u.plan}</span></td>
                      <td className="py-3 px-4 text-sm font-mono text-gray-400">{u.release_count}</td>
                      <td className="py-3 px-4 text-xs text-gray-500">{new Date(u.created_at).toLocaleDateString()}</td>
                      <td className="py-3 px-4">
                        <button onClick={() => openEdit(u)} className="text-xs text-[#7C4DFF] hover:underline flex items-center gap-1" data-testid={`edit-user-${u.id}`}>
                          <PencilSimple className="w-4 h-4" /> Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {pages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-white/10">
              <p className="text-xs text-gray-500">{total} total users</p>
              <div className="flex items-center gap-2">
                <button onClick={() => fetchUsers(page - 1, search)} disabled={page <= 1} className="p-1 text-gray-400 hover:text-white disabled:opacity-30"><CaretLeft className="w-5 h-5" /></button>
                <span className="text-sm text-gray-400">Page {page} of {pages}</span>
                <button onClick={() => fetchUsers(page + 1, search)} disabled={page >= pages} className="p-1 text-gray-400 hover:text-white disabled:opacity-30"><CaretRight className="w-5 h-5" /></button>
              </div>
            </div>
          )}
        </div>

        {/* Edit User Modal */}
        {editUser && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4" data-testid="edit-user-modal">
            <div className="absolute inset-0 bg-black/70" onClick={() => setEditUser(null)} />
            <div className="relative bg-[#111] border border-white/10 rounded-2xl w-full max-w-md p-6 space-y-5">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold">Edit User</h2>
                <button onClick={() => setEditUser(null)} className="p-1 text-gray-400 hover:text-white"><X className="w-5 h-5" /></button>
              </div>
              <div className="text-sm text-gray-400 bg-white/5 p-3 rounded-lg">
                <p className="font-medium text-white">{editUser.artist_name || editUser.name}</p>
                <p>{editUser.email}</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Role</label>
                  <select value={editForm.role} onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                    className="w-full p-2 rounded-lg text-sm" data-testid="edit-role-select">
                    <option value="artist">Artist</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Plan</label>
                  <select value={editForm.plan} onChange={(e) => setEditForm({ ...editForm, plan: e.target.value })}
                    className="w-full p-2 rounded-lg text-sm" data-testid="edit-plan-select">
                    <option value="free">Free</option>
                    <option value="rise">Rise</option>
                    <option value="pro">Pro</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Status</label>
                  <select value={editForm.status} onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                    className="w-full p-2 rounded-lg text-sm" data-testid="edit-status-select">
                    <option value="active">Active</option>
                    <option value="suspended">Suspended</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <Button onClick={() => setEditUser(null)} variant="outline" className="flex-1 border-white/10 text-gray-400">Cancel</Button>
                <Button onClick={handleSave} disabled={saving} className="flex-1 bg-[#E53935] hover:bg-[#d32f2f] text-white" data-testid="save-user-btn">
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminUsersPage;
