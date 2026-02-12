import { useEffect, useRef, useCallback } from 'react';

/**
 * Debounced auto-save: call onSave(values) after delay ms of no changes.
 * onSave is called with latest values; optional onError.
 */
export function useAutoSave(values, onSave, options = {}) {
  const { delay = 2000, enabled = true } = options;
  const timeoutRef = useRef(null);
  const lastSavedRef = useRef(null);
  const onSaveRef = useRef(onSave);
  onSaveRef.current = onSave;

  const flush = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    const current = typeof values === 'object' && values !== null ? { ...values } : values;
    if (lastSavedRef.current === null || JSON.stringify(current) !== JSON.stringify(lastSavedRef.current)) {
      lastSavedRef.current = current;
      onSaveRef.current?.(current);
    }
  }, [values]);

  useEffect(() => {
    if (!enabled) return;
    timeoutRef.current = setTimeout(flush, delay);
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [values, delay, enabled, flush]);

  return { flush };
}
