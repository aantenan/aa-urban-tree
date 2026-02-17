"""Document management service: upload, list, download, delete with ownership verification."""
import uuid
from io import BytesIO
from typing import Any, BinaryIO
from uuid import UUID

from database.models import Application, Document, DocumentThumbnail
from documents.categories import (
    DOCUMENT_CATEGORY_SITE_PHOTOS,
    DOCUMENT_CATEGORY_SITE_PLAN,
    normalize_category,
)
from documents.validation import validate_document_upload_and_scan
from utils.responses import error_response, success_response


class DocumentManagementService:
    """Document upload, retrieval, download, delete. Constructor injection for storage and scanner."""

    def __init__(
        self,
        storage=None,
        malware_scanner=None,
    ) -> None:
        self.storage = storage
        self.malware_scanner = malware_scanner

    def _get_app_or_error(self, application_id: str, user_id: str) -> tuple[Application | None, dict | None]:
        """Return (app, None) if found and owned, else (None, error_response)."""
        try:
            aid = UUID(application_id)
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return None, error_response("Invalid id", data={"code": "invalid_id"})
        try:
            app = Application.get((Application.id == aid) & (Application.user_id == uid))
            return app, None
        except Application.DoesNotExist:
            return None, error_response("Application not found", data={"code": "not_found"})

    def _build_storage_key(self, application_id: str, document_id: str, filename: str) -> str:
        """Build unique storage key for document."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        return f"documents/{application_id}/{document_id}.{ext}"

    def _build_thumbnail_key(self, application_id: str, document_id: str) -> str:
        """Build storage key for thumbnail."""
        return f"documents/{application_id}/{document_id}/thumb.png"

    def upload_document(
        self,
        application_id: str,
        user_id: str,
        *,
        file_obj: BinaryIO,
        filename: str,
        content_type: str,
        category: str,
    ) -> dict[str, Any]:
        """
        Upload document: validate, scan, store, create DB record. Optionally generate thumbnail for images.
        """
        app, err = self._get_app_or_error(application_id, user_id)
        if err is not None:
            return err
        if app.status != "draft":
            return error_response(
                "Documents cannot be modified after application submission",
                data={"code": "not_draft"},
            )
        if not self.storage:
            return error_response("Storage not configured", data={"code": "storage_error"})

        size = 0
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        data = file_obj.read()
        size = len(data)

        ok, msg = validate_document_upload_and_scan(
            filename=filename,
            content_type=content_type,
            size=size,
            category=category,
            file_obj=BytesIO(data),
            scanner=self.malware_scanner,
        )
        if not ok:
            return error_response(msg, data={"code": "validation_error"})

        category_normalized = normalize_category(category) or category
        doc_id = uuid.uuid4()
        storage_key = self._build_storage_key(application_id, str(doc_id), filename)

        try:
            meta = self.storage.upload(
                BytesIO(data),
                key=storage_key,
                content_type=content_type,
                original_filename=filename,
            )
        except Exception as e:
            return error_response(f"Upload failed: {e}", data={"code": "upload_error"})

        try:
            user_uuid = UUID(user_id)
            doc = Document.create(
                id=doc_id,
                application_id=app.id,
                file_name=filename,
                file_path=storage_key,
                file_size=meta.size if hasattr(meta, "size") else size,
                file_type=content_type,
                category=category_normalized,
                uploader_user=user_uuid,
            )
        except Exception as e:
            try:
                self.storage.delete(storage_key)
            except Exception:
                pass
            return error_response(f"Failed to save document record: {e}", data={"code": "db_error"})

        thumb_url: str | None = None
        if content_type in ("image/jpeg", "image/png"):
            thumb_key, thumb_size = self._generate_and_store_thumbnail(
                application_id, str(doc_id), BytesIO(data), content_type
            )
            if thumb_key:
                DocumentThumbnail.create(
                    document_id=doc.id,
                    thumbnail_path=thumb_key,
                    thumbnail_size=thumb_size,
                )
                thumb_url = self.storage.get_url(thumb_key) if self.storage else None

        upload_date = doc.upload_date.isoformat() + "Z" if hasattr(doc.upload_date, "isoformat") else str(doc.upload_date)
        return success_response(
            data={
                "documentId": str(doc.id),
                "fileName": filename,
                "fileSize": meta.size if hasattr(meta, "size") else size,
                "uploadDate": upload_date,
                "thumbnailUrl": thumb_url,
            },
            message="Document uploaded",
        )

    def list_documents(self, application_id: str, user_id: str) -> dict[str, Any]:
        """List documents grouped by category (camelCase keys for API)."""
        app, err = self._get_app_or_error(application_id, user_id)
        if err is not None:
            return err
        docs = Document.select().where(Document.application_id == app.id).order_by(Document.upload_date)
        grouped: dict[str, list[dict]] = {
            "sitePlan": [],
            "sitePhotos": [],
            "supportingDocuments": [],
        }
        for doc in docs:
            has_thumb = DocumentThumbnail.select().where(DocumentThumbnail.document_id == doc.id).exists()
            upload_date = doc.upload_date.isoformat() + "Z" if hasattr(doc.upload_date, "isoformat") else str(doc.upload_date)
            item = {
                "documentId": str(doc.id),
                "fileName": doc.file_name,
                "fileSize": doc.file_size,
                "uploadDate": upload_date,
                "hasThumbnail": has_thumb,
            }
            if doc.category == DOCUMENT_CATEGORY_SITE_PLAN:
                grouped["sitePlan"].append(item)
            elif doc.category == DOCUMENT_CATEGORY_SITE_PHOTOS:
                grouped["sitePhotos"].append(item)
            else:
                grouped["supportingDocuments"].append(item)
        return success_response(data={"documents": grouped})

    def download_thumbnail(
        self, application_id: str, document_id: str, user_id: str
    ) -> tuple[bytes | None, dict | None]:
        """Download thumbnail for document. Returns (content, error_response)."""
        app, err = self._get_app_or_error(application_id, user_id)
        if err is not None:
            return None, err
        try:
            doc_id = UUID(document_id)
        except (ValueError, TypeError):
            return None, error_response("Invalid document id", data={"code": "invalid_id"})
        try:
            doc = Document.get((Document.id == doc_id) & (Document.application_id == app.id))
        except Document.DoesNotExist:
            return None, error_response("Document not found", data={"code": "not_found"})
        thumb = DocumentThumbnail.select().where(DocumentThumbnail.document_id == doc.id).first()
        if not thumb:
            return None, error_response("Thumbnail not found", data={"code": "not_found"})
        if not self.storage:
            return None, error_response("Storage not configured", data={"code": "storage_error"})
        try:
            content = self.storage.download(thumb.thumbnail_path)
            return content, None
        except FileNotFoundError:
            return None, error_response("Thumbnail file not found", data={"code": "not_found"})
        except Exception as e:
            return None, error_response(f"Download failed: {e}", data={"code": "download_error"})

    def download_document(
        self, application_id: str, document_id: str, user_id: str
    ) -> tuple[bytes | None, str | None, str | None, dict | None]:
        """
        Download document file. Returns (content, filename, content_type, error_response).
        """
        app, err = self._get_app_or_error(application_id, user_id)
        if err is not None:
            return None, None, None, err
        try:
            doc_id = UUID(document_id)
        except (ValueError, TypeError):
            return None, None, None, error_response("Invalid document id", data={"code": "invalid_id"})
        try:
            doc = Document.get((Document.id == doc_id) & (Document.application_id == app.id))
        except Document.DoesNotExist:
            return None, None, None, error_response("Document not found", data={"code": "not_found"})
        if not self.storage:
            return None, None, None, error_response("Storage not configured", data={"code": "storage_error"})
        try:
            content = self.storage.download(doc.file_path)
            return content, doc.file_name, doc.file_type, None
        except FileNotFoundError:
            return None, None, None, error_response("File not found", data={"code": "not_found"})
        except Exception as e:
            return None, None, None, error_response(f"Download failed: {e}", data={"code": "download_error"})

    def delete_document(self, application_id: str, document_id: str, user_id: str) -> dict[str, Any]:
        """Delete document. Blocked after application submission."""
        app, err = self._get_app_or_error(application_id, user_id)
        if err is not None:
            return err
        if app.status != "draft":
            return error_response(
                "Documents cannot be modified after application submission",
                data={"code": "not_draft"},
            )
        try:
            doc_id = UUID(document_id)
        except (ValueError, TypeError):
            return error_response("Invalid document id", data={"code": "invalid_id"})
        try:
            doc = Document.get((Document.id == doc_id) & (Document.application_id == app.id))
        except Document.DoesNotExist:
            return error_response("Document not found", data={"code": "not_found"})
        thumb = DocumentThumbnail.select().where(DocumentThumbnail.document_id == doc.id)
        for t in thumb:
            if self.storage:
                try:
                    self.storage.delete(t.thumbnail_path)
                except Exception:
                    pass
            t.delete_instance()
        if self.storage:
            try:
                self.storage.delete(doc.file_path)
            except Exception:
                pass
        doc.delete_instance()
        return success_response(message="Document deleted")

    def get_document_status(self, application_id: str, user_id: str) -> dict[str, Any]:
        """Return completion status: sitePlanUploaded, sitePhotosUploaded, allRequiredDocumentsUploaded."""
        app, err = self._get_app_or_error(application_id, user_id)
        if err is not None:
            return err
        site_plan = Document.select().where(
            (Document.application_id == app.id) & (Document.category == DOCUMENT_CATEGORY_SITE_PLAN)
        ).exists()
        site_photos = Document.select().where(
            (Document.application_id == app.id) & (Document.category == DOCUMENT_CATEGORY_SITE_PHOTOS)
        ).exists()
        return success_response(data={
            "sitePlanUploaded": site_plan,
            "sitePhotosUploaded": site_photos,
            "allRequiredDocumentsUploaded": site_plan and site_photos,
        })

    def _generate_and_store_thumbnail(
        self, application_id: str, document_id: str, file_obj: BinaryIO, content_type: str
    ) -> tuple[str | None, int]:
        """Generate thumbnail for image and store. Returns (thumbnail_key, size) or (None, 0)."""
        from documents.thumbnail import generate_thumbnail

        thumb_key = self._build_thumbnail_key(application_id, document_id)
        thumb_data, thumb_size = generate_thumbnail(
            file_obj=file_obj,
            content_type=content_type,
            max_size=(200, 200),
        )
        if thumb_data and thumb_size and self.storage:
            try:
                self.storage.upload(
                    BytesIO(thumb_data),
                    key=thumb_key,
                    content_type="image/png",
                    original_filename="thumb.png",
                )
                return thumb_key, thumb_size
            except Exception:
                return None, 0
        return None, 0
