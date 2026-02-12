import React, { useState, useRef } from 'react';

/**
 * File upload with drag-and-drop and progress indicator.
 * Accept: e.g. ".pdf,.jpg,.jpeg,.png", maxSize in bytes.
 * onSelect(files), onProgress(percent), onError(message).
 */
export function FileUpload({
  accept = '.pdf,.jpg,.jpeg,.png',
  maxSize = 10 * 1024 * 1024,
  multiple = false,
  onSelect,
  onProgress,
  onError,
  disabled = false,
  label = 'Choose file or drag and drop',
  className = '',
}) {
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(null);
  const inputRef = useRef(null);

  const validate = (file) => {
    if (file.size > maxSize) {
      const mb = (maxSize / (1024 * 1024)).toFixed(0);
      return `File must be under ${mb}MB`;
    }
    return null;
  };

  const handleFiles = (files) => {
    if (!files?.length) return;
    const list = Array.from(files);
    const err = list.find((f) => validate(f));
    if (err) {
      onError?.(err);
      return;
    }
    setProgress(0);
    if (onProgress) {
      setTimeout(() => setProgress(100), 200);
      onProgress(100);
    } else {
      setProgress(100);
    }
    onSelect?.(list);
  };

  const handleChange = (e) => {
    handleFiles(e.target.files);
    e.target.value = '';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    if (disabled) return;
    handleFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(!disabled);
  };

  const handleDragLeave = () => setDragging(false);

  return (
    <div className={`file-upload ${className}`.trim()}>
      <div
        className={`file-upload__dropzone ${dragging ? 'file-upload__dropzone--active' : ''} ${disabled ? 'file-upload__dropzone--disabled' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        aria-label={label}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleChange}
          disabled={disabled}
          className="file-upload__input"
          aria-hidden="true"
        />
        <span className="file-upload__label">{label}</span>
        {progress != null && (
          <div className="file-upload__progress" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
            <div className="file-upload__progress-bar" style={{ width: `${progress}%` }} />
          </div>
        )}
      </div>
    </div>
  );
}
