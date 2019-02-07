from django.utils.translation import ugettext as _
from django import forms

from envelope.forms import ContactForm
from braces.forms import UserKwargModelFormMixin
from crispy_forms.layout import Layout

from wattstrat.utils.forms import BootstrapFormHelper, WattstratSubmit
from wattstrat.simulation.models import Simulation

class WattstratContactForm(UserKwargModelFormMixin, ContactForm):
    simulation = forms.ModelChoiceField(Simulation.objects.all(), to_field_name='shortid',
                                        label=_("Simulation concerned"), required=False)

    def __init__(self, *args, **kwargs):
        super(WattstratContactForm, self).__init__(*args, **kwargs)
        if self.user.is_authenticated():
            self.fields['simulation'].queryset = Simulation.objects.filter(account__users=self.user)
        else:
            del self.fields['simulation']

        self.helper = BootstrapFormHelper(self)
        self.helper.layout = Layout(
            'sender', 'email', 'simulation', 'subject', 'message',
            WattstratSubmit('submit', _('Send')),
        )
