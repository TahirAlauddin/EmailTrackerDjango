from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models.fields import CharField, EmailField, IntegerField


class Recipient(models.Model):
    """
    Model to store information about email recipients.

    A recipient is a unique combination of recipient_id and email_campaign_id.
    This model stores details such as recipient's first name, last name, company name and email address,
    as well as the information such as recipient's opened the email or clicked on the link.
    """
    email_address = EmailField(max_length=255)
    first_name = CharField(max_length=255, blank=True, null=True)
    last_name = CharField(max_length=255,  blank=True, null=True)
    company_name = CharField(max_length=255, blank=True, null=True)
    recipient_id = IntegerField()
    email_campaign_id = IntegerField()
    opened = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    from_user = models.ForeignKey('AppUser', on_delete=models.CASCADE)

    def __str__(self):
        return self.email_address
    
    class Meta:
        """Make sure there is only one row with same recipient_id and email_campaign_id"""
        constraints = [
            models.UniqueConstraint(
                fields=['recipient_id', 'email_campaign_id', 'from_user'],
                name='unique_recipient_per_campaign'
            )
        ]


class AppUser(models.Model):
    first_name = models.CharField(verbose_name=_('first name'), max_length=254, null=True)
    last_name = models.CharField(verbose_name=_('last name'), max_length=254, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("date joined"))
    license = models.CharField(max_length=12, verbose_name=_("License Key"))
    email_address = models.EmailField(
        _('Email'),
        max_length=150,
        unique=True,
        error_messages={
            'unique': _("A user with that Email already exists."),
        },
    )

    def __str__(self):
        return self.email_address

    class Meta:
        ordering = ("-id",)
        verbose_name = _("App User")
        verbose_name_plural = _("App Users")
        db_table = "core_appuser"

