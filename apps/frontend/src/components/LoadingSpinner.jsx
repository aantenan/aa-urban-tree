import React from 'react';

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '2rem',
  },
  spinner: {
    width: 40,
    height: 40,
    border: '3px solid #eee',
    borderTopColor: '#333',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  },
};

export function LoadingSpinner() {
  return (
    <div style={styles.container} aria-label="Loading">
      <div style={styles.spinner} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
