from django.views import generic
from revproxy.views import ProxyView
from braces.views import LoginRequiredMixin
from django.conf import settings
from wattstrat.accounts.forms import SignupForm
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from wattstrat.utils.email import send_email_to_admin
from datetime import datetime



def handler400(request):
    messages.error(request, "Erreur 400 - Erreur de requête. Si cette erreur suvient à nouveau, merci de nous contacter.")
    return redirect('simulation:results:dashboard')

def handler401(request):
    messages.error(request, "Erreur 401 - Merci de vérifier que vous êtes toujours identifié. Si cette erreur suvient à nouveau, merci de nous contacter.")
    return redirect('simulation:results:dashboard')

def handler403(request):
    messages.error(request, "Erreur 403 - Merci de vérifier que vous êtes toujours identifié. Si cette erreur suvient à nouveau, merci de nous contacter.")
    return redirect('simulation:results:dashboard')

def handler404(request):
    messages.error(request, "Erreur 404 - Page non trouvée. Si cette erreur suvient à nouveau, merci de nous contacter.")
    return redirect('simulation:results:dashboard')


def handler500(request):
    messages.error(request, "Erreur 500 - Erreur interne. L'équipe WattStrat a été informée de cette erreur.")
    send_email_to_admin(subject="Erreur 500 - Erreur interne", body_template = "auth/emails/error_page.html", context={'time': datetime.now(), 'user': request.user, 'request': request})
    return redirect('simulation:results:dashboard')

def handler501(request):
    messages.error(request, "Erreur 501 - Fonctionnalité manquante. L'équipe WattStrat a été informée de cette erreur.")
    send_email_to_admin(subject="Erreur 501 - Fonctionnalité manquante", body_template = "auth/emails/error_page.html", context={'time': datetime.now(), 'user': request.user, 'request': request})
    return redirect('simulation:results:dashboard')

def handler502(request):
    messages.error(request, "Erreur 502 - Erreur de réponse. L'équipe WattStrat a été informée de cette erreur.")
    send_email_to_admin(subject="Erreur 502 - Erreur de réponse", body_template = "auth/emails/error_page.html", context={'time': datetime.now(), 'user': request.user, 'request': request})
    return redirect('simulation:results:dashboard')

def handler503(request):
    messages.error(request, "Erreur 503 - Service indisponible. L'équipe WattStrat a été informée de cette erreur.")
    send_email_to_admin(subject="Erreur 503 - Service indisponible", body_template = "auth/emails/error_page.html", context={'time': datetime.now(), 'user': request.user, 'request': request})
    return redirect('simulation:results:dashboard')



class HomePage(generic.TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(signup_form=SignupForm(), **kwargs)



class UserGuideByWikiView(LoginRequiredMixin,ProxyView):
    upstream = settings.WIKI_UPSTREAM
    add_remote_user=True
    # default path = ""
    def dispatch(self, request, *args, path="",**kwargs ):
        return super().dispatch(request, *args, path=path, **kwargs)




