
from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from authtools.models import AbstractNamedUser
from djchoices.choices import DjangoChoices, ChoiceItem
from jsonfield import JSONField

from wattstrat.utils.model import FileUploadPath


class Account(models.Model):
    #======================
    # Contact
    #======================
    corporate_name = models.CharField(_("corporate name"), max_length=100, blank=True)
    department = models.CharField(_("department"), max_length=100, blank=True)
    address = models.CharField(_("address"), max_length=200, blank=True)
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    logo = models.ImageField(_("logo"), upload_to=FileUploadPath('logo'), null=True, blank=True)
    communes = JSONField(default={}, blank=True)

    class Meta:
        verbose_name = _("account")

    def __str__(self):
        if self.corporate_name:
            return self.corporate_name
        else:
            return _('account of %(user)s') % {'user': self.users.first()}

    def get_absolute_url(self):
        return reverse('accounts:account')

    def get_account(self):
        """ Used by FileUploadPath """
        return self


class User(AbstractNamedUser):
    account = models.ForeignKey(Account, verbose_name=_("account"), related_name='users')
    email_verified = models.BooleanField("Email verified", default=False)

    def get_absolute_url(self):
        return reverse('accounts:account')

    def save(self, *args, **kwargs):
        # Create an empty account on user creation
        if not self.pk and not self.account_id:
            self.account = Account.objects.create()
        super(User, self).save(*args, **kwargs)

    @property
    def username(self):
        return self.email
