import React, { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui';
import { apiJson } from '../services/api';

const WARN_BEFORE_MS = 5 * 60 * 1000; // 5 minutes before expiry
const CHECK_INTERVAL_MS = 60 * 1000;   // check every minute

/**
 * Session timeout warning: shows 5 minutes before expiry with extend or logout.
 * Uses JWT exp if available; otherwise no warning.
 */
export function SessionTimeoutWarning() {
  const { token, setToken, setUser, logout } = useAuth();
  const [show, setShow] = useState(false);
  const [extending, setExtending] = useState(false);

  const getExpiry = useCallback(() => {
    if (!token || token.length < 20) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload?.exp;
      return exp ? exp * 1000 : null;
    } catch {
      return null;
    }
  }, [token]);

  useEffect(() => {
    if (!token) {
      setShow(false);
      return;
    }
    const check = () => {
      const exp = getExpiry();
      if (!exp) return;
      const now = Date.now();
      if (exp - now <= WARN_BEFORE_MS && exp > now) setShow(true);
      else setShow(false);
    };
    check();
    const id = setInterval(check, CHECK_INTERVAL_MS);
    return () => clearInterval(id);
  }, [token, getExpiry]);

  const handleExtend = async () => {
    setExtending(true);
    try {
      const res = await apiJson('/api/v1/auth/refresh-token', {
        method: 'POST',
        body: JSON.stringify({ token }),
      });
      if (res?.token) {
        setToken(res.token);
        if (res?.user) setUser(res.user);
        setShow(false);
      }
    } catch {
      setShow(true);
    } finally {
      setExtending(false);
    }
  };

  const handleLogout = () => {
    logout();
    setShow(false);
    window.location.href = '/login';
  };

  if (!show) return null;
  return (
    <div
      className="session-timeout-warning"
      role="dialog"
      aria-labelledby="session-timeout-title"
      aria-describedby="session-timeout-desc"
      aria-modal="true"
    >
      <div className="session-timeout-warning__box">
        <h2 id="session-timeout-title" className="session-timeout-warning__title">
          Your session will time out soon
        </h2>
        <p id="session-timeout-desc" className="session-timeout-warning__desc">
          For security and protection of data, you will be logged out of your session in a few minutes.
          Click &ldquo;Log out&rdquo; to end your session, or &ldquo;Continue session&rdquo; to extend your session.
        </p>
        <div className="session-timeout-warning__actions">
          <Button type="button" variant="secondary" onClick={handleLogout} disabled={extending}>
            Log out
          </Button>
          <Button type="button" variant="primary" onClick={handleExtend} loading={extending}>
            Continue session
          </Button>
        </div>
      </div>
    </div>
  );
}
