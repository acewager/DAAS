import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchAdminUsers, updateAdminUser } from "@/services/adminService";
import type { AdminUser } from "@/services/adminService";
import { useAuth } from "@/contexts/AuthContext";

/**
 * User management (VS-050, Sprint 8) — the user list with role/activation
 * management. Role changes require a super admin; admins can toggle
 * activation; nobody can change their own account.
 */
export default function AdminUsersPage() {
  const queryClient = useQueryClient();
  const { user: me } = useAuth();
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["admin-users", search],
    queryFn: () => fetchAdminUsers({ search: search || undefined }),
  });

  const update = useMutation({
    mutationFn: ({ id, changes }: { id: string; changes: { role?: string; is_active?: boolean } }) => updateAdminUser(id, changes),
    onSuccess: () => {
      setError("");
      void queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
    onError: () => setError("Unable to update the user."),
  });

  const canChangeRoles = me?.role === "SUPER_ADMIN";

  return (
    <div className="w-full max-w-3xl space-y-4">
      <h1 className="text-2xl font-semibold">Users</h1>
      <input
        className="w-full rounded border p-2 text-sm"
        placeholder="Search by username or email…"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
      {isLoading && <p className="text-sm text-slate-500">Loading users…</p>}
      <div className="space-y-2">
        {data?.users.map((user: AdminUser) => (
          <article className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border bg-white p-4 dark:bg-slate-900" key={user.id}>
            <div>
              <strong>{user.username}</strong>
              {user.id === me?.id && <span className="ml-1 text-xs text-slate-400">(you)</span>}
              <p className="text-sm text-slate-500">{user.email} · {user.instance_count} instance(s)</p>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <select
                className="rounded border p-1.5 text-xs"
                value={user.role}
                disabled={!canChangeRoles || user.id === me?.id}
                onChange={(event) => update.mutate({ id: user.id, changes: { role: event.target.value } })}
              >
                <option value="USER">USER</option>
                <option value="ADMIN">ADMIN</option>
                <option value="SUPER_ADMIN">SUPER_ADMIN</option>
              </select>
              <button
                className={`rounded px-3 py-1.5 text-xs disabled:opacity-40 ${user.is_active ? "bg-success/10 text-success" : "bg-danger/10 text-danger"}`}
                disabled={user.id === me?.id || update.isPending}
                onClick={() => update.mutate({ id: user.id, changes: { is_active: !user.is_active } })}
                type="button"
              >
                {user.is_active ? "Active" : "Inactive"}
              </button>
            </div>
          </article>
        ))}
        {data && data.users.length === 0 && <p className="text-sm text-slate-500">No users match.</p>}
      </div>
      {data && data.pagination.pages > 1 && (
        <div className="flex items-center justify-between text-sm text-slate-500">
          <span>Page {data.pagination.page} of {data.pagination.pages} ({data.pagination.total} users)</span>
        </div>
      )}
    </div>
  );
}
