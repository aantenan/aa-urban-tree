"""Document model for file metadata storage and category-based organization."""
from datetime import datetime

from peewee import CharField, Check, DateTimeField, ForeignKeyField, IntegerField

from database.models.application import Application
from database.models.base import BaseModel
from database.models.user import User


# Valid document categories (stored as snake_case in DB)
DOCUMENT_CATEGORY_SITE_PLAN = "site_plan"
DOCUMENT_CATEGORY_SITE_PHOTOS = "site_photos"
DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS = "supporting_documents"

DOCUMENT_CATEGORIES = (
    DOCUMENT_CATEGORY_SITE_PLAN,
    DOCUMENT_CATEGORY_SITE_PHOTOS,
    DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS,
)


class Document(BaseModel):
    """
    Document metadata: application association, filename, path, size, type,
    category, upload details. File content stored externally; paths in DB.
    Categories: Site Plan, Site Photos, Supporting Documents.
    """

    application = ForeignKeyField(
        Application, backref="documents", on_delete="CASCADE", index=True
    )
    file_name = CharField(max_length=512)  # Original filename
    file_path = CharField(max_length=1024, null=False)  # System-generated path
    file_size = IntegerField()  # Bytes
    file_type = CharField(max_length=64)  # e.g. application/pdf, image/jpeg
    category = CharField(max_length=64, index=True)  # site_plan | site_photos | supporting_documents
    upload_date = DateTimeField(default=datetime.utcnow)  # Auto-set on creation
    uploader_user = ForeignKeyField(
        User, backref="uploaded_documents", on_delete="SET NULL", null=True
    )

    class Meta:
        table_name = "documents"
        indexes = (
            (("application_id", "category"), False),
            (("application_id", "category", "file_name"), True),  # Unique per app+category
        )
        constraints = [
            Check(
                "category IN ('site_plan', 'site_photos', 'supporting_documents')",
                name="documents_category_check",
            ),
        ]
