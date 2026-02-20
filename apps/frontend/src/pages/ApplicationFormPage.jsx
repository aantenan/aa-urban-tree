import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiJson } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { Button } from '../components/ui';
import { ContactInformationSection } from '../components/ContactInformationSection';
import { ProjectInformationSection } from '../components/ProjectInformationSection';
import { FinancialInformationSection } from '../components/FinancialInformationSection';
import { DocumentUploadSection } from '../components/DocumentUploadSection';
import { SectionNav } from '../components/SectionNav';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function ApplicationFormPage() {
  const { id: applicationId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [application, setApplication] = useState(null);
  const [loadError, setLoadError] = useState('');
  const [startNewError, setStartNewError] = useState('');
  const [loadingApp, setLoadingApp] = useState(!!applicationId);
  const [boardStatus, setBoardStatus] = useState(null);
  const [markReadyError, setMarkReadyError] = useState('');
  const [markReadyLoading, setMarkReadyLoading] = useState(false);

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

  const loadBoardStatus = useCallback(() => {
    if (!applicationId) return;
    apiJson(`/api/v1/applications/${applicationId}/forestry-board-approval-status`)
      .then((res) => setBoardStatus(res?.data ?? res))
      .catch(() => setBoardStatus(null));
  }, [applicationId]);

  useEffect(() => {
    if (applicationId) loadBoardStatus();
  }, [applicationId, loadBoardStatus]);

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

  const handleMarkReadyForBoardReview = async () => {
    if (!applicationId) return;
    setMarkReadyError('');
    setMarkReadyLoading(true);
    try {
      await apiJson(`/api/v1/applications/${applicationId}/mark-ready-for-board-review`, { method: 'POST' });
      loadBoardStatus();
      setApplication((a) => a ? { ...a, readyForBoardReview: true } : a);
    } catch (err) {
      setMarkReadyError(getErrorMessage(err));
    } finally {
      setMarkReadyLoading(false);
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
          <SectionNav
            sections={[
              { id: 'contact', label: 'Contact Information', href: '#contact-information' },
              { id: 'project', label: 'Project Information', href: '#project-information' },
              { id: 'financial', label: 'Financial Information', href: '#financial-information' },
              { id: 'documents', label: 'Documents', href: '#documents' },
            ]}
            className="application-form__nav"
          />
          <ContactInformationSection applicationId={applicationId} />
          <ProjectInformationSection applicationId={applicationId} />
          <FinancialInformationSection applicationId={applicationId} />
          <DocumentUploadSection
            applicationId={applicationId}
            applicationStatus={application?.status}
          />
          {application?.status === 'draft' && (
            <section id="board-review" style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ccc', borderRadius: 4 }}>
              <h3>Forestry Board Review</h3>
              {boardStatus && (
                <p>
                  <strong>Status:</strong>{' '}
                  {boardStatus.status === 'pending' && 'Pending Board Approval'}
                  {boardStatus.status === 'approved' && 'Approved'}
                  {boardStatus.status === 'revision_requested' && 'Revision Requested'}
                  {boardStatus.status === 'not_submitted' && 'Not yet submitted for review'}
                  {!['pending', 'approved', 'revision_requested', 'not_submitted'].includes(boardStatus.status) && boardStatus.status}
                  {boardStatus.revisionComments && (
                    <span style={{ display: 'block', marginTop: '0.5rem' }}>
                      Board comments: {boardStatus.revisionComments}
                    </span>
                  )}
                </p>
              )}
              {(boardStatus?.status === 'not_submitted' || boardStatus?.status === 'revision_requested' || !boardStatus) && (
                <>
                  <Button
                    type="button"
                    variant="primary"
                    onClick={handleMarkReadyForBoardReview}
                    loading={markReadyLoading}
                  >
                    Mark ready for board review
                  </Button>
                  {markReadyError && (
                    <p role="alert" style={{ color: 'crimson', marginTop: '0.5rem' }}>{markReadyError}</p>
                  )}
                  <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
                    Notifies the Forestry Board for your county. They will review and either approve or request revisions.
                  </p>
                </>
              )}
            </section>
          )}
        </>
      ) : (
        <p>Start a new application to begin the contact and project information sections.</p>
      )}
    </div>
  );
}
