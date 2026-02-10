import React, { createContext, useContext, useState } from 'react';

const ApplicationContext = createContext(null);

export function ApplicationProvider({ children }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);

  const value = {
    applications,
    setApplications,
    loading,
    setLoading,
  };

  return (
    <ApplicationContext.Provider value={value}>
      {children}
    </ApplicationContext.Provider>
  );
}

export function useApplications() {
  const ctx = useContext(ApplicationContext);
  if (!ctx) throw new Error('useApplications must be used within ApplicationProvider');
  return ctx;
}
