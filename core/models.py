from django.db import models
from django.db.models.fields import CharField, EmailField, IntegerField


class Recipient(models.Model):
    """
    Model to store information about email recipients.

    A recipient is a unique combination of recipient_id, recipient_list_id, and email_campaign_id.
    This model stores details such as recipient's first name, last name, company name and email address,
    as well as the information such as recipient's opened the email or clicked on the link.
    """
    email_address = EmailField(max_length=255)
    first_name = CharField(max_length=255, blank=True, null=True)
    last_name = CharField(max_length=255,  blank=True, null=True)
    company_name = CharField(max_length=255, blank=True, null=True)
    recipient_id = IntegerField()
    recipient_list_id = IntegerField()
    email_campaign_id = IntegerField()
    opened = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)

    def __str__(self):
        return self.email_address
    
    class Meta:
        """Make sure there is only one row with same recipient_id, recipient_list_id and
        email_campaign_id"""
        constraints = [
            models.UniqueConstraint(
                fields=['recipient_id', 'recipient_list_id', 'email_campaign_id'],
                name='unique_recipient_per_campaign'
            )
        ]

