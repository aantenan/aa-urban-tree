import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiJson } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { Button } from '../components/ui';
import { ContactInformationSection } from '../components/ContactInformationSection';
import { ProjectInformationSection } from '../components/ProjectInformationSection';
import { FinancialInformationSection } from '../components/FinancialInformationSection';
import { DocumentUploadSection } from '../components/DocumentUploadSection';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function ApplicationFormPage() {
  const { id: applicationId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [application, setApplication] = useState(null);
  const [loadError, setLoadError] = useState('');
  const [startNewError, setStartNewError] = useState('');
  const [loadingApp, setLoadingApp] = useState(!!applicationId);

  React.useEffect(() => {
    if (!applicationId) {
      setApplication(null);
      setLoadingApp(false);
      setLoadError('');
      return;
    }
    setLoadingApp(true);
    setLoadError('');
    apiJson(`/api/v1/applications/${applicationId}`)
      .then((res) => {
        const data = res?.data ?? res;
        setApplication(data);
      })
      .catch((err) => {
        setLoadError(getErrorMessage(err));
      })
      .finally(() => {
        setLoadingApp(false);
      });
  }, [applicationId]);

  const handleStartNew = async () => {
    setStartNewError('');
    try {
      const res = await apiJson('/api/v1/applications', { method: 'POST' });
      const data = res?.data ?? res;
      if (data?.id) navigate(`/dashboard/application/${data.id}`, { replace: true });
    } catch (err) {
      setStartNewError(getErrorMessage(err));
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '2rem' }}>
      <header style={{ marginBottom: '1.5rem' }}>
        <h1>Grant Application</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          {application?.id && (
            <Button type="button" variant="secondary" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </Button>
          )}
          {!applicationId && (
            <Button type="button" variant="primary" onClick={handleStartNew}>
              Start new application
            </Button>
          )}
        </div>
      </header>

      {loadError && (
        <div role="alert" style={{ color: 'crimson', marginBottom: '1rem' }}>
          {loadError}
        </div>
      )}

      {startNewError && (
        <p role="alert" style={{ color: 'crimson', marginBottom: '1rem' }}>
          {startNewError}
        </p>
      )}

      {loadingApp && applicationId ? (
        <LoadingSpinner />
      ) : applicationId ? (
        <>
          <ContactInformationSection applicationId={applicationId} />
          <ProjectInformationSection applicationId={applicationId} />
          <FinancialInformationSection applicationId={applicationId} />
          <DocumentUploadSection
            applicationId={applicationId}
            applicationStatus={application?.status}
          />
        </>
      ) : (
        <p>Start a new application to begin the contact and project information sections.</p>
      )}
    </div>
  );
}
