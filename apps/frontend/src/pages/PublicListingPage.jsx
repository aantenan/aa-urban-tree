import React, { useEffect, useState } from 'react';
import { getProgramConfig } from '../services/publicApi';
import { ProgramInfoDisplay } from '../components/public/ProgramInfoDisplay';
import { ResourceDownloader } from '../components/public/ResourceDownloader';
import { LoadingSpinner } from '../components/LoadingSpinner';

/**
 * Public listing & discovery page. No authentication.
 * SEO: semantic markup, meta handled via index.html / helmet if added later.
 */
export function PublicListingPage() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getProgramConfig()
      .then((data) => {
        if (!cancelled) setConfig(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <p role="alert">Unable to load program information. Please try again later.</p>;

  return (
    <main id="public-listing" className="public-listing-page">
      <ProgramInfoDisplay config={config} />
      {config?.resources?.length > 0 && (
        <ResourceDownloader resources={config.resources} />
      )}
    </main>
  );
}
