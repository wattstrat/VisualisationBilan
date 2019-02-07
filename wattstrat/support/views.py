from django.utils.translation import ugettext_lazy as _

from envelope.views import ContactView
from braces.views import FormMessagesMixin, UserFormKwargsMixin
from wattstrat.support.forms import WattstratContactForm

class WattstratContactView(FormMessagesMixin, UserFormKwargsMixin, ContactView):
    template_name = "support/contact.html"
    form_valid_message = _(u"Thank you for your message.")
    form_invalid_message = _(u"There was an error in the contact form.")
    form_class = WattstratContactForm

    def get_initial(self):
        """
        Automatically fills form fields for authenticated users.
        """
        initial = super(WattstratContactView, self).get_initial().copy()
        user = self.request.user
        if user.is_authenticated():
            initial['sender'] = user.get_full_name()

        initial['simulation'] = self.request.GET.get('simulation', None)
        return initial
