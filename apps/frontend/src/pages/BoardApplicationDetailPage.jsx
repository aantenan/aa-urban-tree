import React, { useCallback, useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getBoardApplication, approveApplication, requestRevision, listBoardDocuments, getBoardDocumentDownloadPath } from '../services/boardApi';
import { apiFetch } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Button, Input } from '../components/ui';
import { Modal } from '../components/ui/Modal';

const STATUS_LABELS = {
  pending: 'Pending Board Approval',
  approved: 'Approved',
  revision_requested: 'Revision Requested',
};

export function BoardApplicationDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [documents, setDocuments] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [showApproveDialog, setShowApproveDialog] = useState(false);
  const [showRevisionDialog, setShowRevisionDialog] = useState(false);
  const [approveForm, setApproveForm] = useState({ boardMemberName: '', boardMemberTitle: '', approvalDate: '' });
  const [revisionComments, setRevisionComments] = useState('');
  const [actionError, setActionError] = useState('');

  const loadData = useCallback(() => {
    if (!id) return;
    setLoading(true);
    setError('');
    Promise.all([
      getBoardApplication(id),
      listBoardDocuments(id).catch(() => null),
    ])
      .then(([appData, docsRes]) => {
        setData(appData);
        setDocuments(docsRes?.documents ?? docsRes);
        const today = new Date().toISOString().split('T')[0];
        setApproveForm((f) => ({ ...f, approvalDate: today }));
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleApprove = () => {
    if (!approveForm.boardMemberName?.trim()) {
      setActionError('Please type your full name to confirm your signature.');
      return;
    }
    setActionLoading(true);
    setActionError('');
    approveApplication(id, {
      boardMemberName: approveForm.boardMemberName.trim(),
      boardMemberTitle: approveForm.boardMemberTitle?.trim() || undefined,
      approvalDate: approveForm.approvalDate,
    })
      .then(() => {
        setShowApproveDialog(false);
        loadData();
      })
      .catch((err) => setActionError(getErrorMessage(err)))
      .finally(() => setActionLoading(false));
  };

  const handleRequestRevision = () => {
    if (!revisionComments?.trim()) {
      setActionError('Please enter comments for the applicant.');
      return;
    }
    setActionLoading(true);
    setActionError('');
    requestRevision(id, { comments: revisionComments.trim() })
      .then(() => {
        setShowRevisionDialog(false);
        setRevisionComments('');
        loadData();
      })
      .catch((err) => setActionError(getErrorMessage(err)))
      .finally(() => setActionLoading(false));
  };

  const canAct = data?.status === 'pending' || data?.status === 'revision_requested';

  return (
    <div className="container">
      <div className="content-card">
        <nav aria-label="Breadcrumb" className="breadcrumb">
          <Link to="/board/review">Board Review</Link>
          <span aria-hidden="true"> / </span>
          <span>Application {id?.slice(0, 8)}…</span>
        </nav>

        {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
        {loading && <LoadingSpinner />}

        {!loading && data && (
          <>
            <div className="board-detail-header">
              <h2 style={{ margin: 0 }}>{data.projectName || 'Application'}</h2>
              <span className={`board-status board-status--${data.status}`}>
                {STATUS_LABELS[data.status] || data.status}
              </span>
            </div>
            <p>
              <strong>Applicant:</strong> {data.applicantName}
              {' · '}
              <strong>Organization:</strong> {data.organizationName}
              {' · '}
              <strong>County:</strong> {data.county}
            </p>

            {data.revisionHistory?.length > 0 && (
              <section className="board-revision-history" aria-label="Revision history">
                <h3>Revision History</h3>
                <ul>
                  {data.revisionHistory.map((rev, i) => (
                    <li key={i}>
                      <strong>{rev.requestDate ? new Date(rev.requestDate).toLocaleDateString() : '—'}</strong>
                      <p>{rev.comments}</p>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {data.sections && (
              <section className="board-sections" aria-label="Application sections">
                <h3>Application Details</h3>
                {data.sections.contactInformation && (
                  <div className="board-section">
                    <h4>Contact Information</h4>
                    <dl>
                      {Object.entries(data.sections.contactInformation).map(([k, v]) => (
                        v != null && v !== '' && (
                          <React.Fragment key={k}>
                            <dt>{k.replace(/_/g, ' ')}</dt>
                            <dd>{String(v)}</dd>
                          </React.Fragment>
                        )
                      ))}
                    </dl>
                  </div>
                )}
                {data.sections.projectInformation && (
                  <div className="board-section">
                    <h4>Project Information</h4>
                    <dl>
                      {Object.entries(data.sections.projectInformation).map(([k, v]) => (
                        v != null && v !== '' && (
                          <React.Fragment key={k}>
                            <dt>{k.replace(/_/g, ' ')}</dt>
                            <dd>{String(v)}</dd>
                          </React.Fragment>
                        )
                      ))}
                    </dl>
                  </div>
                )}
                {data.sections.financialInformation && (
                  <div className="board-section">
                    <h4>Financial Information</h4>
                    <dl>
                      {Object.entries(data.sections.financialInformation).map(([k, v]) => (
                        v != null && v !== '' && (
                          <React.Fragment key={k}>
                            <dt>{k.replace(/_/g, ' ')}</dt>
                            <dd>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</dd>
                          </React.Fragment>
                        )
                      ))}
                    </dl>
                  </div>
                )}
              </section>
            )}

            {documents && (documents.sitePlan?.length > 0 || documents.sitePhotos?.length > 0 || documents.supportingDocuments?.length > 0) && (
              <section className="board-documents" aria-label="Uploaded documents">
                <h3>Documents</h3>
                <ul>
                  {[].concat(
                    documents.sitePlan || [],
                    documents.sitePhotos || [],
                    documents.supportingDocuments || [],
                  ).map((doc) => {
                    const docId = doc.documentId || doc.id;
                    const path = getBoardDocumentDownloadPath(id, docId);
                    const filename = doc.fileName || doc.file_name || 'document';
                    return (
                      <li key={docId}>
                        <button
                          type="button"
                          className="board-link"
                          style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer', font: 'inherit', color: 'var(--link)' }}
                          onClick={() => {
                            apiFetch(path)
                              .then((r) => r.blob())
                              .then((b) => {
                                const u = URL.createObjectURL(b);
                                const a = document.createElement('a');
                                a.href = u;
                                a.download = filename;
                                a.click();
                                URL.revokeObjectURL(u);
                              })
                              .catch(() => {});
                          }}
                        >
                          {filename}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </section>
            )}

            {canAct && data.status !== 'approved' && (
              <section className="board-actions" aria-label="Approval actions">
                <h3>Actions</h3>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  <Button
                    type="button"
                    variant="primary"
                    onClick={() => { setShowApproveDialog(true); setActionError(''); }}
                  >
                    Approve
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => { setShowRevisionDialog(true); setActionError(''); setRevisionComments(''); }}
                  >
                    Request Revision
                  </Button>
                </div>
              </section>
            )}
          </>
        )}
      </div>

      <Modal
        open={showApproveDialog}
        title="Approve Application"
        onClose={() => !actionLoading && setShowApproveDialog(false)}
      >
        <p>By approving, you confirm with your electronic signature (typed name) that you have reviewed this application.</p>
        {actionError && <p role="alert" style={{ color: 'crimson' }}>{actionError}</p>}
        <label className="board-signature-label" style={{ display: 'block', marginTop: '1rem' }}>
          Type your full name (electronic signature) <span className="required">*</span>
          <Input
            type="text"
            value={approveForm.boardMemberName}
            onChange={(e) => setApproveForm((f) => ({ ...f, boardMemberName: e.target.value }))}
            placeholder="Your full name"
            autoComplete="name"
            aria-required="true"
            style={{ display: 'block', marginTop: '0.25rem' }}
          />
        </label>
        <label className="board-signature-label" style={{ display: 'block', marginTop: '1rem' }}>
          Title
          <Input
            type="text"
            value={approveForm.boardMemberTitle}
            onChange={(e) => setApproveForm((f) => ({ ...f, boardMemberTitle: e.target.value }))}
            placeholder="e.g. Forestry Board Chair"
            style={{ display: 'block', marginTop: '0.25rem' }}
          />
        </label>
        <label className="board-signature-label" style={{ display: 'block', marginTop: '1rem' }}>
          Approval date
          <Input
            type="date"
            value={approveForm.approvalDate}
            onChange={(e) => setApproveForm((f) => ({ ...f, approvalDate: e.target.value }))}
            aria-label="Approval date"
            style={{ display: 'block', marginTop: '0.25rem' }}
          />
        </label>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
          <Button type="button" variant="secondary" onClick={() => !actionLoading && setShowApproveDialog(false)} disabled={actionLoading}>
            Cancel
          </Button>
          <Button type="button" variant="primary" onClick={handleApprove} loading={actionLoading}>
            Confirm Approval
          </Button>
        </div>
      </Modal>

      <Modal
        open={showRevisionDialog}
        title="Request Revision"
        onClose={() => !actionLoading && setShowRevisionDialog(false)}
      >
        <p>The applicant will receive an email with your comments and can edit and resubmit for review.</p>
        {actionError && <p role="alert" style={{ color: 'crimson' }}>{actionError}</p>}
        <label className="board-signature-label" style={{ display: 'block', marginTop: '1rem' }}>
          Comments for applicant <span className="required">*</span>
          <textarea
            value={revisionComments}
            onChange={(e) => setRevisionComments(e.target.value)}
            placeholder="Describe the changes needed..."
            rows={5}
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            aria-required="true"
          />
        </label>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
          <Button type="button" variant="secondary" onClick={() => !actionLoading && setShowRevisionDialog(false)} disabled={actionLoading}>
            Cancel
          </Button>
          <Button type="button" variant="primary" onClick={handleRequestRevision} loading={actionLoading}>
            Submit Revision Request
          </Button>
        </div>
      </Modal>
    </div>
  );
}
