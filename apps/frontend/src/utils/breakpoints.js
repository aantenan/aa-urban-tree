/**
 * Breakpoint constants for responsive design (match CSS media queries).
 * Use in JS for conditional rendering or in CSS with @media (min-width: ...).
 */
export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
};

import { useState, useEffect } from 'react';

/**
 * Hook-friendly: subscribe to window.matchMedia for a breakpoint.
 * Returns whether the viewport is at least that wide.
 * Note: requires window; use with care in SSR.
 */
export function useBreakpoint(minWidth) {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mq = window.matchMedia(`(min-width: ${minWidth}px)`);
    setMatches(mq.matches);
    const handler = () => setMatches(mq.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [minWidth]);
  return matches;
}
