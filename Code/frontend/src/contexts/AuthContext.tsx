import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { fetchCurrentUser, logoutAccount, requestCsrfCookie } from "@/services/authService";

import type { User } from "@/types/auth";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  refreshUser: () => Promise<User | null>;
  signOut: () => Promise<void>;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = async () => {
    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch {
      setUser(null);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void requestCsrfCookie();
    void refreshUser();
  }, []);

  const signOut = async () => {
    // Clear local state first: the UI must reflect the logout even if the
    // server-side call fails (e.g., an already-invalid session).
    setUser(null);
    try {
      await logoutAccount();
    } catch {
      // Nothing to do — the local state is cleared either way.
    }
  };

  const value = useMemo(
    () => ({ user, isLoading, refreshUser, signOut, setUser }),
    [user, isLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
