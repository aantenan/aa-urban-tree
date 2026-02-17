"""Tests for Document and DocumentThumbnail models."""
import os

import pytest
from peewee import IntegrityError, SqliteDatabase

from database.connection import database_proxy, get_db
from database.models import Application, Document, DocumentThumbnail, User


@pytest.fixture
def in_memory_db() -> SqliteDatabase:
    """Use an in-memory SQLite database for tests."""
    db = SqliteDatabase(":memory:")
    database_proxy.initialize(db)
    db.create_tables([User, Application, Document, DocumentThumbnail])
    yield db
    database_proxy.initialize(None)
    db.close()


def test_document_create_and_thumbnail(in_memory_db: SqliteDatabase) -> None:
    """Document and DocumentThumbnail can be created with valid data."""
    u = User.create(email="doc@example.com", password_hash="x", account_status="active")
    app = Application.create(user=u, status="draft")
    doc = Document.create(
        application=app,
        file_name="plan.pdf",
        file_path="/uploads/abc/plan.pdf",
        file_size=1024,
        file_type="application/pdf",
        category="site_plan",
        uploader_user=u,
    )
    thumb = DocumentThumbnail.create(
        document=doc, thumbnail_path="/thumbs/thumb.jpg", thumbnail_size=256
    )
    assert doc.id is not None
    assert doc.upload_date is not None
    assert thumb.document_id == doc.id


def test_document_category_constraint(in_memory_db: SqliteDatabase) -> None:
    """Invalid category raises IntegrityError."""
    u = User.create(email="u@x.com", password_hash="x", account_status="active")
    app = Application.create(user=u, status="draft")
    with pytest.raises(IntegrityError):
        Document.create(
            application=app,
            file_name="x.pdf",
            file_path="/x",
            file_size=1,
            file_type="application/pdf",
            category="invalid_category",
            uploader_user=u,
        )


def test_document_unique_per_application_category(in_memory_db: SqliteDatabase) -> None:
    """Duplicate file_name within same application+category raises IntegrityError."""
    u = User.create(email="u@x.com", password_hash="x", account_status="active")
    app = Application.create(user=u, status="draft")
    Document.create(
        application=app,
        file_name="dup.pdf",
        file_path="/a",
        file_size=1,
        file_type="application/pdf",
        category="site_plan",
        uploader_user=u,
    )
    with pytest.raises(IntegrityError):
        Document.create(
            application=app,
            file_name="dup.pdf",
            file_path="/b",
            file_size=1,
            file_type="application/pdf",
            category="site_plan",
            uploader_user=u,
        )


def test_document_same_filename_different_category_allowed(
    in_memory_db: SqliteDatabase,
) -> None:
    """Same file_name in different category is allowed."""
    u = User.create(email="u@x.com", password_hash="x", account_status="active")
    app = Application.create(user=u, status="draft")
    Document.create(
        application=app,
        file_name="dup.pdf",
        file_path="/a",
        file_size=1,
        file_type="application/pdf",
        category="site_plan",
        uploader_user=u,
    )
    doc2 = Document.create(
        application=app,
        file_name="dup.pdf",
        file_path="/b",
        file_size=1,
        file_type="application/pdf",
        category="site_photos",
        uploader_user=u,
    )
    assert doc2.id is not None
