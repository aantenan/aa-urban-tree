# Frontend Component Framework

Reusable patterns for forms, modals, loading, accessibility, and print.

## Base components

- **Button** (`components/ui/Button.jsx`): `variant` (primary|secondary), `loading`, `disabled`, `type`. Use `aria-label` when the label is only an icon.
- **Input** (`components/ui/Input.jsx`): `label`, `error`, `hint`, `required`. Inline error and `aria-invalid`/`aria-describedby` for screen readers.
- **Form** (`components/ui/Form.jsx`): Wraps children with `onSubmit`, `loading`; use with `useForm` for validation.
- **Modal** (`components/ui/Modal.jsx`): `open`, `onClose`, `title`. Escape and overlay click close; `role="dialog"`, `aria-modal="true"`.
- **ConfirmationDialog** (`components/ui/ConfirmationDialog.jsx`): Confirm/cancel actions; `confirmLabel`, `cancelLabel`, `variant`, `loading`.

## Form management

- **useForm** (`hooks/useForm.js`): `initialValues`, `validate(values) => errors`, `validateOnChange`/`validateOnBlur`. Returns `values`, `errors`, `touched`, `handleChange`, `handleBlur`, `handleSubmit(onSubmit)`, `isSubmitting`, `setErrors`, etc.
- **useAutoSave** (`hooks/useAutoSave.js`): Debounced save: pass `values`, `onSave`, `{ delay, enabled }`. Calls `onSave(latestValues)` after inactivity.

## Loading and errors

- **LoadingSpinner** (`components/LoadingSpinner.jsx`): Centered spinner with `aria-label="Loading"`.
- **ErrorBoundary** (`components/ErrorBoundary.jsx`): Catches child errors; optional `fallback`, `message`, `showRetry`, `onRetry`, `onError`.

## File upload and date

- **FileUpload** (`components/FileUpload.jsx`): Drag-and-drop, `accept`, `maxSize`, `onSelect(files)`, `onProgress`, `onError`. Progress bar and keyboard accessible.
- **DatePicker** (`components/DatePicker.jsx`): Native `type="date"` with `label`, `value`/`onChange`, `min`/`max`, `error`, `hint`.

## Navigation

- **Breadcrumb** (`components/Breadcrumb.jsx`): `items = [{ label, path? }]`. Current page without `path`; `aria-label="Breadcrumb"`.
- **SectionNav** (`components/SectionNav.jsx`): `sections = [{ id, label, href?, completed? }]`, `currentId`. Completion status indicators.

## Accessibility

- **utils/accessibility.js**: `getFocusableElements(container)`, `focusFirst`/`focusLast`, `trapFocus(container)`, `announce(message, 'polite'|'assertive')`.
- **utils/breakpoints.js**: `BREAKPOINTS` (sm/md/lg/xl), `useBreakpoint(minWidth)` for responsive logic.
- Use `sr-only` class for screen-reader-only text. Buttons and inputs use `aria-*` as needed.

## Print / PDF

- **utils/print.js**: `printReceipt(selector)` to print a section (e.g. `.print-area`); `getPrintStyles()` for `@media print` CSS. Users can "Print to PDF" from the browser.

## Usage example

```jsx
import { Form, Button, Input } from './components/ui';
import { useForm } from './hooks/useForm';

function MyForm() {
  const { values, errors, handleChange, handleBlur, handleSubmit, isSubmitting } = useForm(
    { email: '' },
    { validate: (v) => ({ email: !v.email ? 'Required' : null }) }
  );
  return (
    <Form onSubmit={handleSubmit(async (vals) => { /* submit */ })}>
      <Input name="email" label="Email" value={values.email} error={errors.email}
        onChange={handleChange} onBlur={handleBlur} />
      <Button type="submit" loading={isSubmitting}>Submit</Button>
    </Form>
  );
}
```
