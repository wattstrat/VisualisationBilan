from django.utils.translation import ugettext as _
from django.db import models

from jsonfield import JSONField

from wattstrat.accounts.models import Account, User
from wattstrat.utils.model import ShortIdMixin


class Simulation(ShortIdMixin, models.Model):
    account = models.ForeignKey(Account, related_name="simulations")
    name = models.CharField(_("simulation name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    date = models.DateTimeField(_("creation date"), auto_now_add=True)

    # Where the data are saved

    """
        A list of "parameter" object, one for each milestone.

        For each parameter object, each parameter name is mapped to the list of parameters that concern this name.
        {
            'demand.residential.general': [...],
            'demand.residential.main_residential': [...],
        }
    """
    framing_parameters = JSONField(default=[], blank=True)
    territory_groups = JSONField(default=[], blank=True)

    # Scan or data
    simu_type = models.CharField(default="scan", blank=True, max_length=4)


    class Meta:
        ordering = ('-date', '-pk')

    def __str__(self):
        return self.name

    @property
    def groups_geocodes(self):
        return {group['id']: group['geocodes'] for group in self.territory_groups}

    def get_creator(self):
        return self.account.users.first()

    def get_creator_name(self):
        return self.get_creator().get_full_name()

    @property
    def creators(self):
        return [user.email for user in self.account.users.all()]
    
