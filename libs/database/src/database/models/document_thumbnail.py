"""Document thumbnail model for storing preview image paths."""
from peewee import CharField, ForeignKeyField, IntegerField

from database.models.base import BaseModel
from database.models.document import Document


class DocumentThumbnail(BaseModel):
    """Thumbnail for a document (e.g. JPG/PNG preview)."""

    document = ForeignKeyField(
        Document, backref="thumbnails", on_delete="CASCADE", index=True
    )
    thumbnail_path = CharField(max_length=1024, null=False)
    thumbnail_size = IntegerField()  # Bytes

    class Meta:
        table_name = "document_thumbnails"
