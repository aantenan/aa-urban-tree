"""Tests for DocumentManagementService with mock storage."""
from io import BytesIO
import pytest
from peewee import SqliteDatabase

from database.connection import database_proxy
from database.models import Application, Document, DocumentThumbnail, User
from services.document_management_service import DocumentManagementService
from utils.testing import MockMalwareScanner, MockStorageBackend, mock_malware_scanner, mock_storage_backend


@pytest.fixture
def db_and_services():
    """In-memory DB with User and Application, plus mock storage/scanner."""
    db = SqliteDatabase(":memory:")
    database_proxy.initialize(db)
    db.create_tables([User, Application, Document, DocumentThumbnail])
    yield db, mock_storage_backend(), mock_malware_scanner()
    database_proxy.initialize(None)
    db.close()


@pytest.fixture
def app_and_user(db_and_services):
    """Create user and draft application."""
    db, _, _ = db_and_services
    u = User.create(email="docuser@example.com", password_hash="x", account_status="active")
    app = Application.create(user=u, status="draft")
    return app, u, db_and_services


def test_upload_document_success(app_and_user):
    """Upload valid PDF succeeds and creates document record."""
    app, user, (db, storage, scanner) = app_and_user
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    content = b"%PDF-1.4 minimal content"
    result = svc.upload_document(
        str(app.id),
        str(user.id),
        file_obj=BytesIO(content),
        filename="plan.pdf",
        content_type="application/pdf",
        category="site_plan",
    )
    assert result["success"] is True
    assert "documentId" in result["data"]
    assert result["data"]["fileName"] == "plan.pdf"
    assert result["data"]["fileSize"] == len(content)
    doc = Document.get(Document.application_id == app.id)
    assert doc.file_name == "plan.pdf"
    assert doc.category == "site_plan"
    assert storage._store
    assert any("documents/" in k for k in storage._store)


def test_upload_blocked_after_submission(app_and_user):
    """Upload fails when application is submitted."""
    app, user, (db, storage, scanner) = app_and_user
    app.status = "submitted"
    app.save()
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    result = svc.upload_document(
        str(app.id),
        str(user.id),
        file_obj=BytesIO(b"%PDF-1.4 x"),
        filename="plan.pdf",
        content_type="application/pdf",
        category="site_plan",
    )
    assert result["success"] is False
    assert result["data"].get("code") == "not_draft"


def test_list_documents_grouped(app_and_user):
    """List returns documents grouped by category."""
    app, user, (db, storage, scanner) = app_and_user
    Document.create(
        application=app,
        file_name="plan.pdf",
        file_path="documents/a/plan.pdf",
        file_size=100,
        file_type="application/pdf",
        category="site_plan",
        uploader_user=user,
    )
    Document.create(
        application=app,
        file_name="photo.jpg",
        file_path="documents/a/photo.jpg",
        file_size=200,
        file_type="image/jpeg",
        category="site_photos",
        uploader_user=user,
    )
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    result = svc.list_documents(str(app.id), str(user.id))
    assert result["success"] is True
    docs = result["data"]["documents"]
    assert len(docs["sitePlan"]) == 1
    assert len(docs["sitePhotos"]) == 1
    assert docs["sitePlan"][0]["fileName"] == "plan.pdf"


def test_download_document(app_and_user):
    """Download returns file content from storage."""
    app, user, (db, storage, scanner) = app_and_user
    storage._store["documents/a/doc.pdf"] = b"pdf content"
    storage._meta["documents/a/doc.pdf"] = {"storage_key": "documents/a/doc.pdf", "size": 11}
    doc = Document.create(
        application=app,
        file_name="doc.pdf",
        file_path="documents/a/doc.pdf",
        file_size=11,
        file_type="application/pdf",
        category="site_plan",
        uploader_user=user,
    )
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    content, filename, content_type, err = svc.download_document(str(app.id), str(doc.id), str(user.id))
    assert err is None
    assert content == b"pdf content"
    assert filename == "doc.pdf"
    assert content_type == "application/pdf"


def test_delete_document(app_and_user):
    """Delete removes document and storage file."""
    app, user, (db, storage, scanner) = app_and_user
    storage._store["documents/a/doc.pdf"] = b"x"
    doc = Document.create(
        application=app,
        file_name="doc.pdf",
        file_path="documents/a/doc.pdf",
        file_size=1,
        file_type="application/pdf",
        category="site_plan",
        uploader_user=user,
    )
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    result = svc.delete_document(str(app.id), str(doc.id), str(user.id))
    assert result["success"] is True
    assert Document.select().where(Document.id == doc.id).count() == 0
    assert "documents/a/doc.pdf" not in storage._store


def test_delete_blocked_after_submission(app_and_user):
    """Delete fails when application is submitted."""
    app, user, (db, storage, scanner) = app_and_user
    app.status = "submitted"
    app.save()
    doc = Document.create(
        application=app,
        file_name="doc.pdf",
        file_path="documents/a/doc.pdf",
        file_size=1,
        file_type="application/pdf",
        category="site_plan",
        uploader_user=user,
    )
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    result = svc.delete_document(str(app.id), str(doc.id), str(user.id))
    assert result["success"] is False
    assert result["data"].get("code") == "not_draft"
    assert Document.select().where(Document.id == doc.id).count() == 1


def test_get_document_status(app_and_user):
    """Status returns sitePlanUploaded, sitePhotosUploaded, allRequiredDocumentsUploaded."""
    app, user, (db, storage, scanner) = app_and_user
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    result = svc.get_document_status(str(app.id), str(user.id))
    assert result["success"] is True
    assert result["data"]["sitePlanUploaded"] is False
    assert result["data"]["sitePhotosUploaded"] is False
    assert result["data"]["allRequiredDocumentsUploaded"] is False

    Document.create(
        application=app,
        file_name="plan.pdf",
        file_path="x",
        file_size=1,
        file_type="application/pdf",
        category="site_plan",
        uploader_user=user,
    )
    result = svc.get_document_status(str(app.id), str(user.id))
    assert result["data"]["sitePlanUploaded"] is True
    assert result["data"]["sitePhotosUploaded"] is False
    assert result["data"]["allRequiredDocumentsUploaded"] is False

    Document.create(
        application=app,
        file_name="photo.jpg",
        file_path="y",
        file_size=1,
        file_type="image/jpeg",
        category="site_photos",
        uploader_user=user,
    )
    result = svc.get_document_status(str(app.id), str(user.id))
    assert result["data"]["allRequiredDocumentsUploaded"] is True


def test_upload_invalid_file_rejected(app_and_user):
    """Upload with invalid extension is rejected."""
    app, user, (db, storage, scanner) = app_and_user
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    result = svc.upload_document(
        str(app.id),
        str(user.id),
        file_obj=BytesIO(b"x"),
        filename="virus.exe",
        content_type="application/octet-stream",
        category="site_plan",
    )
    assert result["success"] is False
    assert result["data"].get("code") == "validation_error"
    assert Document.select().where(Document.application_id == app.id).count() == 0


def test_upload_oversized_rejected(app_and_user):
    """Upload exceeding 10MB is rejected."""
    app, user, (db, storage, scanner) = app_and_user
    svc = DocumentManagementService(storage=storage, malware_scanner=scanner)
    large = b"x" * (11 * 1024 * 1024)
    result = svc.upload_document(
        str(app.id),
        str(user.id),
        file_obj=BytesIO(large),
        filename="large.pdf",
        content_type="application/pdf",
        category="site_plan",
    )
    assert result["success"] is False
    assert "size" in result["message"].lower() or "limit" in result["message"].lower()
