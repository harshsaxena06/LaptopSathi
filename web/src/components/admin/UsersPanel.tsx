import React, { useEffect, useState } from 'react';
import { adminApi, AdminUser } from '@/api/adminApi';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { ApiError } from '@/types/auth';

export function UsersPanel() {
  const { user: me } = useAuth();
  const { showToast } = useToast();
  const [users, setUsers] = useState<AdminUser[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);

  async function loadUsers() {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.listUsers();
      setUsers(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load users.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUsers();
  }, []);

  async function toggleRole(u: AdminUser) {
    const nextRole = u.role === 'admin' ? 'user' : 'admin';
    setBusyId(u.id);
    try {
      const updated = await adminApi.updateUser(u.id, { role: nextRole });
      setUsers((prev) => prev?.map((x) => (x.id === u.id ? updated : x)) ?? null);
      showToast(`${updated.email} is now ${updated.role === 'admin' ? 'an admin' : 'a regular user'}.`, 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Could not update role.', 'error');
    } finally {
      setBusyId(null);
    }
  }

  async function toggleActive(u: AdminUser) {
    setBusyId(u.id);
    try {
      const updated = await adminApi.updateUser(u.id, { is_active: !u.is_active });
      setUsers((prev) => prev?.map((x) => (x.id === u.id ? updated : x)) ?? null);
      showToast(`${updated.email} ${updated.is_active ? 'reactivated' : 'deactivated'}.`, 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Could not update account status.', 'error');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="card">
      <h3 style={{ marginBottom: 4 }}>Users</h3>
      <p style={{ fontSize: 12.5, color: 'var(--text-2)', marginBottom: 16 }}>
        Promote, demote, or deactivate accounts directly — changes take effect immediately.
      </p>
      {loading && <p style={{ color: 'var(--text-2)', fontSize: 13 }}>Loading…</p>}
      {error && <p className="field-error">{error}</p>}
      {users && (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Verified</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => {
                const isSelf = u.id === me?.id;
                const busy = busyId === u.id;
                return (
                  <tr key={u.id}>
                    <td>{u.full_name ? `${u.full_name} · ` : ''}{u.email}</td>
                    <td>
                      {u.role === 'admin' ? (
                        <span className="role-badge">Admin</span>
                      ) : (
                        <span style={{ color: 'var(--text-2)', fontSize: 12.5 }}>User</span>
                      )}
                    </td>
                    <td>
                      <span style={{ color: u.is_active ? 'var(--green)' : 'var(--red)', fontWeight: 600, fontSize: 12 }}>
                        {u.is_active ? 'Active' : 'Deactivated'}
                      </span>
                    </td>
                    <td>{u.is_verified ? 'Yes' : 'No'}</td>
                    <td style={{ color: 'var(--text-2)', whiteSpace: 'nowrap' }}>
                      {new Date(`${u.created_at}Z`).toLocaleDateString()}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        <button
                          type="button"
                          className="btn btn-ghost"
                          style={{ width: 'auto', padding: '6px 10px', fontSize: 11.5 }}
                          disabled={isSelf || busy}
                          title={isSelf ? "You can't change your own role." : undefined}
                          onClick={() => toggleRole(u)}
                        >
                          {u.role === 'admin' ? 'Make user' : 'Make admin'}
                        </button>
                        <button
                          type="button"
                          className="btn btn-ghost"
                          style={{ width: 'auto', padding: '6px 10px', fontSize: 11.5 }}
                          disabled={isSelf || busy}
                          title={isSelf ? "You can't deactivate your own account." : undefined}
                          onClick={() => toggleActive(u)}
                        >
                          {u.is_active ? 'Deactivate' : 'Reactivate'}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
