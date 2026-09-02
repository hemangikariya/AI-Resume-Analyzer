import React, { createContext, useState, useEffect, useContext } from "react";
import api from "../services/api";

interface UserProfile {
  id: number;
  email: string;
  created_at: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
  setError: (err: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Sync token from localStorage on boot
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem("token");
      const storedUser = localStorage.getItem("user");

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        
        try {
          // Pre-validate stored JWT against backend profiles
          const res = await api.get("/auth/me");
          if (res.data.success) {
            setUser(res.data.data.user);
            localStorage.setItem("user", JSON.stringify(res.data.data.user));
          }
        } catch (err) {
          console.warn("Stored token is invalid or expired. Cleaning credentials...");
          logout();
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setError(null);
    try {
      const res = await api.post("/auth/login", { email, password });
      if (res.data.success) {
        const { user: userProfile, token: tokenData } = res.data.data;
        setToken(tokenData.access_token);
        setUser(userProfile);
        localStorage.setItem("token", tokenData.access_token);
        localStorage.setItem("user", JSON.stringify(userProfile));
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail?.error?.message || "Login failed. Check your credentials.";
      setError(msg);
      throw new Error(msg);
    }
  };

  const signup = async (email: string, password: string) => {
    setError(null);
    try {
      const res = await api.post("/auth/signup", { email, password });
      if (res.data.success) {
        const { user: userProfile, token: tokenData } = res.data.data;
        setToken(tokenData.access_token);
        setUser(userProfile);
        localStorage.setItem("token", tokenData.access_token);
        localStorage.setItem("user", JSON.stringify(userProfile));
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail?.error?.message || "Registration failed. Try a different email.";
      setError(msg);
      throw new Error(msg);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        signup,
        logout,
        error,
        setError
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
