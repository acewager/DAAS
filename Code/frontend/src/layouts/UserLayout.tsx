import { Outlet, Link } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

// Minimal placeholder for the User Layout described in
// 08_Frontend_Architecture.md Section 11 (Sidebar + Header + Content).
// Sidebar navigation is built out alongside Authentication (Sprint 1).
export default function UserLayout() {
  const { user, signOut } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950">
      <header className="border-b border-border bg-white/80 px-4 py-3 backdrop-blur dark:bg-slate-900/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div>
            <span className="block font-semibold text-lg">Desktop Cloud Platform</span>
            {user && <span className="text-sm text-slate-500">Signed in as {user.username}</span>}
          </div>
          <div className="flex items-center gap-3 text-sm">
            <Link to="/" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">Dashboard</Link>
            <Link to="/profile" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">Profile</Link>
            <Link to="/templates" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">Templates</Link>
            <Link to="/instances" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">Instances</Link>
            <Link to="/instances/new" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">New instance</Link>
            <Link to="/software-requests" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">Requests</Link>
            {user && (user.role === "ADMIN" || user.role === "SUPER_ADMIN") && (
              <>
                <Link to="/admin" className="font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400">Admin</Link>
                <Link to="/admin/users" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">Users</Link>
                <Link to="/admin/instances" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">All instances</Link>
                <Link to="/admin/events" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">Events</Link>
                <Link to="/admin/requests" className="text-slate-600 hover:text-slate-900 dark:text-slate-300">Approvals</Link>
              </>
            )}
            {user ? (
              <button className="rounded-lg border border-border px-3 py-1.5" onClick={() => void signOut()} type="button">
                Logout
              </button>
            ) : (
              <Link to="/login" className="rounded-lg border border-border px-3 py-1.5">Login</Link>
            )}
          </div>
        </div>
      </header>
      <main className="mx-auto flex w-full max-w-6xl flex-1 p-4">
        <Outlet />
      </main>
    </div>
  );
}
