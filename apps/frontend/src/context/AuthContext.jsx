import React, { createContext, useCallback, useContext, useState } from 'react';

const AuthContext = createContext(null);

const TOKEN_KEY = 'token';

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(null);

  const setToken = useCallback((newToken) => {
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken);
      setTokenState(newToken);
    } else {
      localStorage.removeItem(TOKEN_KEY);
      setTokenState(null);
      setUser(null);
    }
  }, []);

  const logout = useCallback(() => setToken(null), []);

  const value = {
    token,
    user,
    setToken,
    setUser,
    logout,
    isAuthenticated: !!token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
