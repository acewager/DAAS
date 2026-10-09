import { Route, Routes } from "react-router-dom";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { AuthProvider } from "@/contexts/AuthContext";
import UserLayout from "@/layouts/UserLayout";
import DashboardPage from "@/pages/DashboardPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ProfilePage from "@/pages/ProfilePage";
import PasswordResetPage from "@/pages/PasswordResetPage";
import TemplatesPage from "@/pages/TemplatesPage";
import NewInstancePage from "@/pages/NewInstancePage";
import InstancesPage from "@/pages/InstancesPage";
import SoftwareRequestsPage from "@/pages/SoftwareRequestsPage";
import AdminRequestsPage from "@/pages/AdminRequestsPage";
import AdminDashboardPage from "@/pages/AdminDashboardPage";
import AdminUsersPage from "@/pages/AdminUsersPage";
import AdminInstancesPage from "@/pages/AdminInstancesPage";
import AdminEventsPage from "@/pages/AdminEventsPage";

/**
 * Route table per 08_Frontend_Architecture.md Section 6.
 *
 * Authentication routes and a protected dashboard are implemented in Sprint 1.
 * Remaining feature routes are added one vertical slice at a time.
 */
export default function AppRoutes() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/reset-password" element={<PasswordResetPage />} />
        <Route path="/reset-password/confirm" element={<PasswordResetPage />} />
        <Route
          element={
            <ProtectedRoute>
              <UserLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/instances" element={<InstancesPage />} />
          <Route path="/instances/new" element={<NewInstancePage />} />
          <Route path="/software-requests" element={<SoftwareRequestsPage />} />
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route path="/admin/requests" element={<AdminRequestsPage />} />
          <Route path="/admin/users" element={<AdminUsersPage />} />
          <Route path="/admin/instances" element={<AdminInstancesPage />} />
          <Route path="/admin/events" element={<AdminEventsPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
