"""Project information for an application: name, site, ownership, type, scope, timeline, description."""
from peewee import CharField, DateField, FloatField, ForeignKeyField, IntegerField, TextField

from database.models.application import Application
from database.models.base import BaseModel


class ProjectInformation(BaseModel):
    """
    Project information section: one-to-one with Application.
    Project name, site address, ownership, type, acreage, tree count, timeline, description.
    """

    application = ForeignKeyField(Application, backref="project_information", on_delete="CASCADE", unique=True)

    project_name = CharField(max_length=255, null=True)
    site_address_line1 = CharField(max_length=255, null=True)
    site_address_line2 = CharField(max_length=255, null=True)
    site_city = CharField(max_length=128, null=True)
    site_state_code = CharField(max_length=2, null=True)
    site_zip_code = CharField(max_length=20, null=True)
    site_ownership = CharField(max_length=64, null=True)  # code from site_ownership_options
    project_type = CharField(max_length=64, null=True)   # code from project_type_options
    acreage = FloatField(null=True)
    tree_count = IntegerField(null=True)
    start_date = DateField(null=True)
    completion_date = DateField(null=True)
    description = TextField(null=True)

    class Meta:
        table_name = "project_information"
