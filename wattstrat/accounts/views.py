import datetime

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.http.response import HttpResponse, HttpResponseServerError

from authtools import views as authviews
from braces.views import LoginRequiredMixin, MessageMixin, AnonymousRequiredMixin, FormValidMessageMixin

from wattstrat.accounts import forms
from wattstrat.accounts.models import Account, User
from wattstrat.simulation.models import Simulation
from wattstrat.utils.views import MenuMixin
from wattstrat.utils.email import send_email_to_admin


from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

if __debug__:
    import logging
    logger = logging.getLogger(__name__)

CUSTOM_SUBSCRIPTION = 'default'


class LoginView(AnonymousRequiredMixin,
                authviews.LoginView):
    template_name = "auth/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        redirect = super(LoginView, self).form_valid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me is True:
            ONE_MONTH = 30 * 24 * 60 * 60
            expiry = getattr(settings, "KEEP_LOGGED_DURATION", ONE_MONTH)
            self.request.session.set_expiry(expiry)
        return redirect


class LogoutView(authviews.LogoutView):
    url = reverse_lazy('home')


class SignUpView(AnonymousRequiredMixin,
                 FormValidMessageMixin,
                 generic.CreateView):
    form_class = forms.SignupForm
    model = User
    template_name = 'auth/signup.html'
    success_url = reverse_lazy('home')
    form_valid_message = "You're signed up, we just sent you a confirmation email. " \
                         "Please check your inbox to validate your email address"
    subject_template_name = 'auth/emails/signup_done_subject.txt'
    email_template_name = 'auth/emails/signup_done_email.html'

    def form_valid(self, form):
        r = super(SignUpView, self).form_valid(form)

        to_email = form.cleaned_data["email"]
        self.send_mail(to_email)
        send_email_to_admin(subject="Nouvelle inscription",
                                body_template="auth/emails/signup_done_subject.txt",
                                context={})
        return r

    def send_mail(self, to_email):
        form = PasswordResetForm(data={'email': to_email})
        form.full_clean()
        form.save(
            request=self.request,
            subject_template_name=self.subject_template_name,
            email_template_name=self.email_template_name
        )


class EmailConfirmView(authviews.PasswordResetConfirmView,
                       MessageMixin,
                       generic.View):
    success_message = _("Your account is verified, welcome to Wattstrat !")
    error_message = _("Sorry, we couldn't verify your account")

    def get(self, *args, **kwargs):
        if not self.validlink:
            self.messages.error(self.error_message)
            return redirect("home")
        else:
            self.user.email_verified = True
            self.user.save()
            # Simulate authentication for first login
            self.user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(self.request, self.user)
            self.messages.success(self.success_message)
            return redirect("simulation:results:dashboard")


class PasswordChangeView(authviews.PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = 'auth/password_change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         "Your password was changed, "
                         "hence you have been logged out. Please relogin")
        return super(PasswordChangeView, self).form_valid(form)


class PasswordResetView(authviews.PasswordResetView):
    form_class = forms.PasswordResetForm
    template_name = 'auth/password_reset.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    subject_template_name = 'auth/emails/password_reset_subject.txt'
    email_template_name = 'auth/emails/password_reset_email.html'


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


class PasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView):
    template_name = 'auth/password_reset_confirm.html'
    form_class = forms.SetPasswordForm


class AccountMixin(LoginRequiredMixin, MenuMixin):
    menus = ["account"]


class AccountDetailView(AccountMixin, generic.TemplateView):
    template_name = "accounts/account.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(account_display=forms.AccountForm(instance=self.request.user.account),
                                        user_display=forms.DisplayUserForm(instance=self.request.user),
                                        **kwargs)


class AccountEditView(AccountMixin, generic.UpdateView):
    model = Account
    form_class = forms.AccountForm
    template_name = "accounts/edit_account.html"

    def get_object(self, queryset=None):
        return self.request.user.account

    def get_context_data(self, **kwargs):
        return super().get_context_data(title=_("Edit your account"), **kwargs)


class UserEditView(AccountMixin, generic.UpdateView):
    model = User
    form_class = forms.UserForm
    template_name = "accounts/edit_account.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        return super().get_context_data(title=_("Edit your user"), **kwargs)




class UserInfos(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        infos = {}

        infos["user"] = self._getUserInfo()
        infos['account'] = self._getAccountInfo()

        return Response(infos)

    def _getUserInfo(self):
        return {'name': self.request.user.name,
                'email': self.request.user.email,
                }

    def _getAccountInfo(self):
        return {meta: getattr(self.request.user.account, meta) for meta in ["corporate_name", "department", "address", "phone", ]}
