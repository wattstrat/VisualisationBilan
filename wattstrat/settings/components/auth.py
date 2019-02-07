#================
# Authentication
#================
from django.core.urlresolvers import reverse_lazy

AUTH_USER_MODEL = 'accounts.User'
LOGIN_REDIRECT_URL = reverse_lazy("simulation:results:dashboard")
LOGIN_URL = reverse_lazy("accounts:login")
