import { useState, useCallback } from 'react';

/**
 * Form state: values, errors, touched, submit state.
 * validate(values) => errors object; optional validateOnChange/validateOnBlur.
 * Returns: values, errors, touched, setFieldValue, setFieldTouched, handleChange, handleBlur, handleSubmit, setErrors, isSubmitting, setSubmitting.
 */
export function useForm(initialValues = {}, options = {}) {
  const { validate, validateOnChange = true, validateOnBlur = true } = options;
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setSubmitting] = useState(false);

  const runValidation = useCallback(
    (nextValues) => {
      if (!validate) return {};
      const nextErrors = validate(nextValues);
      return typeof nextErrors === 'object' && nextErrors !== null ? nextErrors : {};
    },
    [validate]
  );

  const setFieldValue = useCallback(
    (name, value) => {
      setValues((prev) => {
        const next = { ...prev, [name]: value };
        if (validateOnChange) setErrors(runValidation(next));
        return next;
      });
    },
    [validateOnChange, runValidation]
  );

  const setFieldTouched = useCallback((name, isTouched = true) => {
    setTouched((prev) => ({ ...prev, [name]: isTouched }));
  }, []);

  const handleChange = useCallback(
    (e) => {
      const { name, value, type, checked } = e.target;
      const val = type === 'checkbox' ? checked : value;
      setFieldValue(name, val);
    },
    [setFieldValue]
  );

  const handleBlur = useCallback(
    (e) => {
      const { name } = e.target;
      setFieldTouched(name);
      if (validateOnBlur) {
        setErrors((prev) => ({ ...prev, ...runValidation(values) }));
      }
    },
    [setFieldTouched, validateOnBlur, runValidation, values]
  );

  const handleSubmit = useCallback(
    (onSubmit) => {
      return async (e) => {
        if (e?.preventDefault) e.preventDefault();
        const nextErrors = runValidation(values);
        setErrors(nextErrors);
        setTouched(Object.fromEntries(Object.keys(values).map((k) => [k, true])));
        const hasErrors = Object.values(nextErrors).some((v) => v != null && v !== '');
        if (hasErrors) return;
        setSubmitting(true);
        try {
          await onSubmit?.(values);
        } finally {
          setSubmitting(false);
        }
      };
    },
    [values, runValidation]
  );

  return {
    values,
    errors,
    touched,
    setFieldValue,
    setFieldTouched,
    setValues,
    setErrors,
    handleChange,
    handleBlur,
    handleSubmit,
    isSubmitting,
    setSubmitting,
  };
}
