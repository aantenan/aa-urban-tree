import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiJson } from '../services/api';
import { getProgramConfig } from '../services/publicApi';
import { ProgramInfoDisplay } from '../components/public/ProgramInfoDisplay';
import { ResourceDownloader } from '../components/public/ResourceDownloader';
import { Button } from '../components/ui';
import { LoadingSpinner } from '../components/LoadingSpinner';

/** Check if deadline has passed (ISO date string). */
function isDeadlinePassed(deadline) {
  if (!deadline) return false;
  try {
    return new Date(deadline) < new Date();
  } catch {
    return false;
  }
}

/** Check if application period is open. */
function isApplicationOpen(openDate, deadline) {
  const now = new Date();
  if (openDate) {
    try {
      if (new Date(openDate) > now) return false;
    } catch {
      return false;
    }
  }
  return !isDeadlinePassed(deadline);
}

/** Format ISO date for display. */
function formatDate(iso) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString(undefined, { dateStyle: 'long' });
  } catch {
    return iso;
  }
}

export function PublicListingPage() {
  const { isAuthenticated } = useAuth();
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [draftApplications, setDraftApplications] = useState([]);

  useEffect(() => {
    document.title = 'Program & Resources | Urban Tree Grant Program';
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) metaDesc.setAttribute('content', 'Find program information, eligibility, deadlines, and resources for the Urban Tree Grant Program.');
  }, []);

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

  useEffect(() => {
    if (!isAuthenticated) return;
    let cancelled = false;
    apiJson('/api/v1/applications')
      .then((res) => {
        if (cancelled) return;
        const data = res?.data ?? res;
        const apps = Array.isArray(data) ? data : [];
        setDraftApplications(apps.filter((a) => a?.status === 'draft'));
      })
      .catch(() => {
        if (!cancelled) setDraftApplications([]);
      });
    return () => { cancelled = true; };
  }, [isAuthenticated]);

  if (loading) {
    return (
      <div className="container">
        <div className="content-card">
          <LoadingSpinner />
        </div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="container">
        <div className="content-card">
          <p role="alert" className="listing-page__error">
            Unable to load program information. Please try again later.
          </p>
        </div>
      </div>
    );
  }

  const grantCycle = config?.grantCycle || {};
  const eligibility = config?.eligibility || {};
  const program = config?.program || {};
  const applicationDeadline = grantCycle.applicationDeadline || config?.grant_cycle?.application_deadline;
  const applicationOpen = grantCycle.applicationOpen || config?.grant_cycle?.application_open;
  const canStartApplication = isApplicationOpen(applicationOpen, applicationDeadline);
  const deadlinePassed = isDeadlinePassed(applicationDeadline);
  const firstDraft = draftApplications[0];

  return (
    <main id="public-listing" className="public-listing-page">
      <div className="container">
        <div className="listing-page__hero content-card">
          <h1 className="listing-page__title">Program &amp; Resources</h1>
          <p className="listing-page__lead">
            Find program information, eligibility, deadlines, and resources for the Urban Tree Grant Program in one place.
          </p>
          <div className="listing-page__actions">
            {canStartApplication ? (
              <Link to="/dashboard/application">
                <Button type="button" variant="primary">Start Application</Button>
              </Link>
            ) : (
              <Button type="button" variant="primary" disabled aria-disabled="true">
                Start Application
              </Button>
            )}
            {deadlinePassed && (
              <span className="listing-page__deadline-notice" aria-live="polite">
                Application deadline has passed.
              </span>
            )}
            {isAuthenticated && firstDraft && (
              <Link
                to={`/dashboard/application/${firstDraft.id}`}
                className="listing-page__return-link"
              >
                Return to Saved Application
              </Link>
            )}
          </div>
        </div>

        <ProgramInfoDisplay
          config={{
            ...config,
            title: config.title || program.name,
            description: config.description || program.purpose,
            eligibility: eligibility?.summary || config?.eligibility,
            deadline_info: config.deadlineInfo || config.deadline_info,
            contact_email: program.contactEmail || config.contact_email,
            contact_phone: program.contactPhone || config.contact_phone,
          }}
        />

        {Object.keys(grantCycle).length > 0 && (
          <section className="content-card grant-cycle-section" aria-labelledby="grant-cycle-heading">
            <h2 id="grant-cycle-heading">Grant Cycle</h2>
            <dl className="grant-cycle__list">
              {grantCycle.year && (
                <>
                  <dt>Year</dt>
                  <dd>{grantCycle.year}</dd>
                </>
              )}
              {grantCycle.applicationOpen && (
                <>
                  <dt>Application open</dt>
                  <dd>{formatDate(grantCycle.applicationOpen)}</dd>
                </>
              )}
              {grantCycle.applicationDeadline && (
                <>
                  <dt>Application deadline</dt>
                  <dd>{formatDate(grantCycle.applicationDeadline)}</dd>
                </>
              )}
              {grantCycle.awardNotificationDate && (
                <>
                  <dt>Award notification</dt>
                  <dd>{formatDate(grantCycle.awardNotificationDate)}</dd>
                </>
              )}
            </dl>
          </section>
        )}

        {(eligibility.applicantTypes?.length > 0 ||
          eligibility.projectTypes?.length > 0 ||
          eligibility.fundingLimits ||
          eligibility.costMatchRequirement != null ||
          eligibility.ineligibleActivities?.length > 0) && (
          <section className="content-card eligibility-section" aria-labelledby="eligibility-structured-heading">
            <h2 id="eligibility-structured-heading">Eligibility Details</h2>
            {eligibility.applicantTypes?.length > 0 && (
              <div className="eligibility-section__block">
                <h3>Eligible applicant types</h3>
                <ul>
                  {eligibility.applicantTypes.map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </div>
            )}
            {eligibility.projectTypes?.length > 0 && (
              <div className="eligibility-section__block">
                <h3>Project types</h3>
                <ul>
                  {eligibility.projectTypes.map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </div>
            )}
            {eligibility.fundingLimits && (
              <div className="eligibility-section__block">
                <h3>Funding limits</h3>
                <p>
                  ${(eligibility.fundingLimits.minimum ?? 0).toLocaleString()} – ${(eligibility.fundingLimits.maximum ?? 0).toLocaleString()}
                </p>
              </div>
            )}
            {eligibility.costMatchRequirement != null && (
              <div className="eligibility-section__block">
                <h3>Cost-match requirement</h3>
                <p>{eligibility.costMatchRequirement}%</p>
              </div>
            )}
            {eligibility.ineligibleActivities?.length > 0 && (
              <div className="eligibility-section__block">
                <h3>Ineligible activities</h3>
                <ul>
                  {eligibility.ineligibleActivities.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {config?.resources?.length > 0 && (
          <ResourceDownloader resources={config.resources} />
        )}
      </div>
    </main>
  );
}
