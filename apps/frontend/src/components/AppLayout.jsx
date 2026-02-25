import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Shell layout inspired by [Maryland OneStop](https://onestop.md.gov/):
 * header with brand and nav (Log in / Register or Dashboard / Sign out), main content, footer.
 */
export function AppLayout() {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="app-header__inner container">
          <Link to="/" className="app-header__brand">
            <img
              src="/maryland-logo.svg"
              alt="Maryland"
              className="app-header__logo"
              width="92"
              height="92"
            />
          </Link>
          <nav className="app-header__nav" aria-label="Main">
            <Link
              to="/listing"
              className={`app-header__link ${location.pathname === '/listing' ? 'app-header__link--current' : ''}`}
            >
              Program &amp; Resources
            </Link>
            <Link
              to="/data"
              className={`app-header__link ${location.pathname === '/data' ? 'app-header__link--current' : ''}`}
            >
              Public data
            </Link>
            {isAuthenticated ? (
              <>
                <Link
                  to="/dashboard"
                  className={`app-header__link ${location.pathname.startsWith('/dashboard') ? 'app-header__link--current' : ''}`}
                >
                  Applications
                </Link>
                <Link
                  to="/complaints"
                  className={`app-header__link ${location.pathname.startsWith('/complaints') && !location.pathname.startsWith('/admin') ? 'app-header__link--current' : ''}`}
                >
                  Complaints
                </Link>
                <Link
                  to="/admin/complaints"
                  className={`app-header__link ${location.pathname.startsWith('/admin/complaints') ? 'app-header__link--current' : ''}`}
                >
                  Admin complaints
                </Link>
                <Link
                  to="/board/review"
                  className={`app-header__link ${location.pathname.startsWith('/board') ? 'app-header__link--current' : ''}`}
                >
                  Board Review
                </Link>
                <span className="app-header__user">{user?.email || 'User'}</span>
                <button
                  type="button"
                  onClick={() => logout()}
                  className="app-header__btn"
                >
                  Sign out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="app-header__link">Log in</Link>
                <Link to="/register" className="app-header__link app-header__link--cta">Register</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">
        <div className="app-footer__inner container">
          <nav className="app-footer__nav" aria-label="Footer">
            <a href="#privacy" className="app-footer__link">Privacy</a>
            <a href="#accessibility" className="app-footer__link">Accessibility</a>
          </nav>
          <p className="app-footer__copy">
            © {new Date().getFullYear()} Maryland OneStop
          </p>
        </div>
      </footer>
    </div>
  );
}
