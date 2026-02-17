import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  deleteDocument,
  downloadDocument,
  getDocumentStatus,
  getThumbnailUrl,
  listDocuments,
  uploadDocument,
} from '../services/documentApi';
import { getErrorMessage } from '../utils/errorHandler';
import { Button, ConfirmationDialog, Modal } from './ui';
import { FileUpload } from './FileUpload';
import { LoadingSpinner } from './LoadingSpinner';

const CATEGORIES = [
  { key: 'site_plan', label: 'Site Plan', required: true },
  { key: 'site_photos', label: 'Site Photos', required: true },
  { key: 'supporting_documents', label: 'Supporting Documents', required: false },
];

const formatSize = (bytes) => {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${bytes} B`;
};

const formatDate = (iso) => {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { dateStyle: 'medium' });
  } catch {
    return iso;
  }
};

export function DocumentUploadSection({ applicationId, applicationStatus = 'draft' }) {
  const [documents, setDocuments] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(!!applicationId);
  const [loadError, setLoadError] = useState('');
  const [uploading, setUploading] = useState({});
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadError, setUploadError] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [previewDoc, setPreviewDoc] = useState(null);
  const [previewBlobUrl, setPreviewBlobUrl] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [thumbUrls, setThumbUrls] = useState({});
  const previewBlobRef = useRef(null);

  const isDraft = applicationStatus === 'draft';

  const loadData = useCallback(() => {
    if (!applicationId) return;
    setLoading(true);
    setLoadError('');
    Promise.all([
      listDocuments(applicationId),
      getDocumentStatus(applicationId),
    ])
      .then(([docs, st]) => {
        setDocuments(docs);
        setStatus(st);
      })
      .catch((err) => setLoadError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [applicationId]);

  useEffect(() => {
    if (!applicationId) {
      setDocuments(null);
      setStatus(null);
      setLoading(false);
      setThumbUrls({});
      return;
    }
    loadData();
  }, [applicationId, loadData]);

  useEffect(() => {
    if (!documents?.documents || !applicationId) return;
    const all = [
      ...(documents.documents.sitePlan || []),
      ...(documents.documents.sitePhotos || []),
      ...(documents.documents.supportingDocuments || []),
    ].filter((d) => d.hasThumbnail);
    all.forEach((doc) => {
      getThumbnailUrl(applicationId, doc.documentId).then((url) => {
        if (url) setThumbUrls((prev) => ({ ...prev, [doc.documentId]: url }));
      });
    });
  }, [documents, applicationId]);

  useEffect(() => {
    if (!previewDoc || !applicationId || !previewDoc.hasThumbnail) {
      if (previewBlobRef.current) {
        URL.revokeObjectURL(previewBlobRef.current);
        previewBlobRef.current = null;
      }
      setPreviewBlobUrl(null);
      return;
    }
    getThumbnailUrl(applicationId, previewDoc.documentId).then((url) => {
      if (previewBlobRef.current) URL.revokeObjectURL(previewBlobRef.current);
      previewBlobRef.current = url;
      setPreviewBlobUrl(url);
    });
    return () => {
      if (previewBlobRef.current) {
        URL.revokeObjectURL(previewBlobRef.current);
        previewBlobRef.current = null;
      }
    };
  }, [previewDoc?.documentId, applicationId]);

  const handleUpload = (category, files) => {
    if (!files?.length || !applicationId || !isDraft) return;
    setUploadError('');
    const file = files[0];
    setUploading((prev) => ({ ...prev, [category]: true }));
    setUploadProgress((prev) => ({ ...prev, [category]: 0 }));
    uploadDocument(applicationId, file, category, (p) => {
      setUploadProgress((prev) => ({ ...prev, [category]: p }));
    })
      .then(() => {
        loadData();
      })
      .catch((err) => {
        setUploadError(getErrorMessage(err));
      })
      .finally(() => {
        setUploading((prev) => ({ ...prev, [category]: false }));
        setUploadProgress((prev) => ({ ...prev, [category]: null }));
      });
  };

  const handleDelete = (doc) => {
    setDeleteConfirm({
      documentId: doc.documentId,
      fileName: doc.fileName,
    });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm || !applicationId) return;
    setDeleteLoading(true);
    try {
      await deleteDocument(applicationId, deleteConfirm.documentId);
      loadData();
      setDeleteConfirm(null);
    } catch (err) {
      setUploadError(getErrorMessage(err));
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleDownload = async (doc) => {
    if (!applicationId) return;
    try {
      const { url, fileName } = await downloadDocument(
        applicationId,
        doc.documentId,
        doc.fileName
      );
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setUploadError(getErrorMessage(err));
    }
  };

  const getCategoryDocs = (key) => {
    const map = {
      site_plan: 'sitePlan',
      site_photos: 'sitePhotos',
      supporting_documents: 'supportingDocuments',
    };
    return (documents?.documents?.[map[key]] ?? []) || [];
  };

  if (loading && applicationId) {
    return (
      <section className="form-section documents-section" aria-labelledby="documents-heading">
        <h2 id="documents-heading">Documents</h2>
        <LoadingSpinner />
      </section>
    );
  }

  return (
    <section
      id="documents"
      className="form-section documents-section"
      aria-labelledby="documents-heading"
      aria-describedby="documents-status"
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          flexWrap: 'wrap',
          marginBottom: '1rem',
        }}
      >
        <h2 id="documents-heading" style={{ margin: 0 }}>
          Documents
        </h2>
        <span
          id="documents-status"
          className="form-section__completion"
          aria-live="polite"
          role="status"
          style={{
            padding: '0.25rem 0.5rem',
            borderRadius: 4,
            fontSize: '0.875rem',
            background: status?.allRequiredDocumentsUploaded ? '#e8f5e9' : '#fff3e0',
            color: status?.allRequiredDocumentsUploaded ? '#1b5e20' : '#e65100',
          }}
        >
          {status?.allRequiredDocumentsUploaded
            ? 'Required documents complete'
            : 'Site Plan and Site Photos required'}
        </span>
        {!isDraft && (
          <span className="documents-section__locked" aria-live="polite">
            Documents cannot be modified after submission.
          </span>
        )}
      </div>

      {loadError && (
        <p role="alert" className="form-section__error">
          {loadError}
          <Button type="button" variant="secondary" onClick={loadData} style={{ marginLeft: '0.5rem' }}>
            Retry
          </Button>
        </p>
      )}
      {uploadError && (
        <p role="alert" className="form-section__error">
          {uploadError}
        </p>
      )}

      <p className="documents-section__hint">
        Accepted formats: PDF, JPG, PNG. Maximum 10 MB per file.
      </p>

      <div className="documents-section__grid">
        {CATEGORIES.map((cat) => (
          <div
            key={cat.key}
            className="documents-section__category"
            aria-labelledby={`documents-${cat.key}-heading`}
          >
            <h3 id={`documents-${cat.key}-heading`} className="documents-section__subheading">
              {cat.label}
              {cat.required && (
                <span className="documents-section__required" aria-hidden="true">
                  {' '}
                  (required)
                </span>
              )}
              {status && (
                <span
                  className={`documents-section__badge ${
                    (cat.key === 'site_plan' && status.sitePlanUploaded) ||
                    (cat.key === 'site_photos' && status.sitePhotosUploaded)
                      ? 'documents-section__badge--ok'
                      : ''
                  }`}
                  aria-hidden="true"
                >
                  {(cat.key === 'site_plan' && status.sitePlanUploaded) ||
                  (cat.key === 'site_photos' && status.sitePhotosUploaded)
                    ? '✓'
                    : ''}
                </span>
              )}
            </h3>

            {isDraft && (
              <>
                <FileUpload
                  accept=".pdf,.jpg,.jpeg,.png"
                  maxSize={10 * 1024 * 1024}
                  multiple={false}
                  disabled={uploading[cat.key]}
                  label={uploading[cat.key] ? 'Uploading…' : 'Choose file or drag and drop'}
                  onSelect={(files) => handleUpload(cat.key, files)}
                  onError={(msg) => setUploadError(msg)}
                />
                {uploading[cat.key] && uploadProgress[cat.key] != null && (
                  <div
                    className="file-upload__progress documents-section__upload-progress"
                    role="progressbar"
                    aria-valuenow={uploadProgress[cat.key]}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className="file-upload__progress-bar"
                      style={{ width: `${uploadProgress[cat.key]}%` }}
                    />
                  </div>
                )}
              </>
            )}

            <ul className="documents-section__list" aria-label={`${cat.label} documents`}>
              {getCategoryDocs(cat.key).map((doc) => (
                <li key={doc.documentId} className="documents-section__item">
                  <div className="documents-section__item-inner">
                    {doc.hasThumbnail && thumbUrls[doc.documentId] ? (
                      <button
                        type="button"
                        className="documents-section__thumb"
                        onClick={() => setPreviewDoc(doc)}
                        aria-label={`Preview ${doc.fileName}`}
                      >
                        <img
                          src={thumbUrls[doc.documentId]}
                          alt=""
                          width={48}
                          height={48}
                          className="documents-section__thumb-img"
                        />
                      </button>
                    ) : (
                      <span className="documents-section__thumb-placeholder" aria-hidden="true">
                        📄
                      </span>
                    )}
                    <div className="documents-section__item-info">
                      <span className="documents-section__item-name">{doc.fileName}</span>
                      <span className="documents-section__item-meta">
                        {formatSize(doc.fileSize)} · {formatDate(doc.uploadDate)}
                      </span>
                    </div>
                    <div className="documents-section__item-actions">
                      <Button
                        type="button"
                        variant="secondary"
                        className="documents-section__btn-small"
                        onClick={() => handleDownload(doc)}
                      >
                        Download
                      </Button>
                      {isDraft && (
                        <Button
                          type="button"
                          variant="secondary"
                          className="documents-section__btn-small"
                          onClick={() => handleDelete(doc)}
                          aria-label={`Delete ${doc.fileName}`}
                        >
                          Delete
                        </Button>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
            {getCategoryDocs(cat.key).length === 0 && (
              <p className="documents-section__empty" aria-live="polite">
                No documents uploaded yet.
              </p>
            )}
          </div>
        ))}
      </div>

      <ConfirmationDialog
        open={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        onConfirm={confirmDelete}
        title="Delete document"
        message={deleteConfirm ? `Delete "${deleteConfirm.fileName}"?` : ''}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="primary"
        loading={deleteLoading}
      />

      <Modal
        open={!!previewDoc}
        onClose={() => setPreviewDoc(null)}
        title={previewDoc?.fileName}
        aria-describedby="preview-image-desc"
      >
        {(previewDoc?.hasThumbnail && previewBlobUrl) ? (
          <img
            id="preview-image-desc"
            src={previewBlobUrl}
            alt={previewDoc.fileName}
            className="documents-section__preview-img"
            style={{ maxWidth: '100%', maxHeight: '70vh' }}
          />
        ) : previewDoc && (
          <p id="preview-image-desc">Preview not available for this file type.</p>
        )}
      </Modal>
    </section>
  );
}
