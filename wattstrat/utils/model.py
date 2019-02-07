from django.utils.translation import ugettext as _
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible

SHORT_ID_LENGTH = 6


class ShortIdMixin(models.Model):
    shortid = models.CharField(_("Short alphanum identifier"), max_length=SHORT_ID_LENGTH,
                               db_index=True, blank=False, null=False)

    @classmethod
    def generate_shortid(cls, length=SHORT_ID_LENGTH):
        shortid = None
        while shortid == None or cls.objects.filter(shortid=shortid).exists() or shortid[0].isdigit():
            shortid = get_random_string(length=length)
        return shortid

    def save(self, *args, **kwargs):
        if self.pk == None or not self.shortid:
            self.shortid = self.generate_shortid()

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


@deconstructible
class FileUploadPath(object):
    """
    Callback object for the FileField's upload_to parameter.
    Distribute files into separate directories for each account.
    The instance object must define a "get_account" method that returns an Account instance.
    """

    def __init__(self, subdirectory=None):
        self.subdirectory = subdirectory

    def __call__(self, instance, filename):
        account = instance.get_account()
        if self.subdirectory:
            return '{0}/{1}/{2}'.format(account.id, self.subdirectory, filename)
        else:
            return '{0}/{1}'.format(account.id, filename)

    def __eq__(self, other):
        return self.subdirectory == other.subdirectory
