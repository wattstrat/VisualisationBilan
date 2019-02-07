import json

from django.conf import settings as djsettings
from django.core import urlresolvers

def simulation(request):
    context = {}
    if request.user.is_authenticated():
        account = request.user.account

        try:
            url_name = urlresolvers.resolve(request.path_info).view_name
        except urlresolvers.Resolver404:  # May happen with djangular url rewrite
            pass

    return context
