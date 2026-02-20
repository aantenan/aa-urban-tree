import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listBoardApplications } from '../services/boardApi';
import { getErrorMessage } from '../utils/errorHandler';
import { LoadingSpinner } from '../components/LoadingSpinner';

const STATUS_LABELS = {
  pending: 'Pending Board Approval',
  approved: 'Approved',
  revision_requested: 'Revision Requested',
};

export function BoardReviewQueuePage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    listBoardApplications()
      .then((data) => {
        if (cancelled) return;
        setApplications(data?.applications ?? []);
        setError('');
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
        if (err?.status === 403) {
          setError('You are not a forestry board member.');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="container">
      <div className="content-card">
        <h2 style={{ margin: 0 }}>Forestry Board Review Queue</h2>
        <p style={{ margin: '0.5rem 0 0' }}>
          Applications from your county awaiting review.
        </p>

        <section style={{ marginTop: '1.5rem' }} aria-label="Applications for review">
          {error && (
            <p role="alert" style={{ color: 'crimson' }}>{error}</p>
          )}
          {loading && <LoadingSpinner />}
          {!loading && !error && (
            <>
              {applications.length === 0 ? (
                <p>No applications pending review in your county.</p>
              ) : (
                <table className="board-queue-table" role="grid" aria-label="Applications">
                  <thead>
                    <tr>
                      <th scope="col">Applicant</th>
                      <th scope="col">Organization</th>
                      <th scope="col">Project</th>
                      <th scope="col">County</th>
                      <th scope="col">Status</th>
                      <th scope="col">Submitted for review</th>
                      <th scope="col">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {applications.map((app) => (
                      <tr key={app.applicationId}>
                        <td>{app.applicantName || '—'}</td>
                        <td>{app.organizationName || '—'}</td>
                        <td>{app.projectName || '—'}</td>
                        <td>{app.county || '—'}</td>
                        <td>
                          <span
                            className={`board-status board-status--${app.status}`}
                            aria-label={`Status: ${STATUS_LABELS[app.status] || app.status}`}
                          >
                            {STATUS_LABELS[app.status] || app.status}
                          </span>
                        </td>
                        <td>{app.submittedForReviewDate ? new Date(app.submittedForReviewDate).toLocaleDateString() : '—'}</td>
                        <td>
                          {(app.status === 'pending' || app.status === 'revision_requested') && (
                            <Link
                              to={`/board/review/${app.applicationId}`}
                              className="board-link"
                            >
                              Review
                            </Link>
                          )}
                          {app.status === 'approved' && <span aria-hidden="true">—</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}
