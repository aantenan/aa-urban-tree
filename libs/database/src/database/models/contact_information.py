"""Contact information for an application: organization, address, county, primary/alternate contact."""
from peewee import CharField, ForeignKeyField, TextField

from database.models.application import Application
from database.models.base import BaseModel


class ContactInformation(BaseModel):
    """
    Contact information section: one-to-one with Application.
    Organization, mailing address, county, primary and alternate contact.
    """

    application = ForeignKeyField(Application, backref="contact_information", on_delete="CASCADE", unique=True)

    # Organization
    organization_name = CharField(max_length=255, null=True)

    # Mailing address
    address_line1 = CharField(max_length=255, null=True)
    address_line2 = CharField(max_length=255, null=True)
    city = CharField(max_length=128, null=True)
    state_code = CharField(max_length=2, null=True)
    zip_code = CharField(max_length=20, null=True)
    county = CharField(max_length=128, null=True)

    # Primary contact
    primary_contact_name = CharField(max_length=255, null=True)
    primary_contact_title = CharField(max_length=128, null=True)
    primary_contact_email = CharField(max_length=255, null=True)
    primary_contact_phone = CharField(max_length=32, null=True)

    # Alternate contact
    alternate_contact_name = CharField(max_length=255, null=True)
    alternate_contact_title = CharField(max_length=128, null=True)
    alternate_contact_email = CharField(max_length=255, null=True)
    alternate_contact_phone = CharField(max_length=32, null=True)

    class Meta:
        table_name = "contact_information"
