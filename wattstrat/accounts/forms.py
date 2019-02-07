from django.utils.translation import ugettext as _
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import forms as authforms, get_user_model
from django.core.urlresolvers import reverse, reverse_lazy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field
from authtools import forms as authtoolsforms

from wattstrat.accounts.models import Account
from wattstrat.utils.forms import WattstratSubmit, SimpleCrispyMixin

User = get_user_model()


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["username"].widget.input_type = "email"  # ugly hack

        self.helper.layout = Layout(
            Field('username', placeholder="Enter Email", autofocus=""),
            Field('password', placeholder="Enter Password"),
            HTML('<a href="{}">Mot de passe oublié ?</a>'.format(
                reverse("accounts:password-reset"))),
            Field('remember_me'),
            Submit('sign_in', 'Log in',
                   css_class="btn btn-lg btn-primary btn-block"),
        )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if not user.email_verified:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='unverified_email',
            )


class SignupForm(authtoolsforms.UserCreationForm):
    accept_tos = forms.BooleanField(required=True, error_messages={
        "required": _("You must accept the terms of service to sign up.")
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['accept_tos'].label = _("Accept the <a href='%(tos_url)s' target='_blank'>terms of service</a>"
                                            ) % {'tos_url': reverse_lazy('tos')}

        self.helper = FormHelper()
        self.helper.form_action = 'accounts:signup'
        self.fields["email"].widget.input_type = "email"  # ugly hack

        self.helper.layout = Layout(
            Field('email', placeholder="Enter Email", autofocus=""),
            Field('name', placeholder="Enter user name"),
            Field('password1', placeholder="Enter Password"),
            Field('password2', placeholder="Re-enter Password"),
            Field('accept_tos'),
            Submit('sign_up', 'Accéder à la plateforme', css_class="btn-success"),
        )


class PasswordChangeForm(authforms.PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('old_password', placeholder="Enter old password",
                  autofocus=""),
            Field('new_password1', placeholder="Enter new password"),
            Field('new_password2', placeholder="Enter new password (again)"),
            WattstratSubmit('pass_change', 'Change Password'),
        )


class PasswordResetForm(authtoolsforms.FriendlyPasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('email', placeholder="Enter email",
                  autofocus=""),
            WattstratSubmit('pass_reset', 'Reset Password'),
        )


class SetPasswordForm(authforms.SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('new_password1', placeholder="Enter new password",
                  autofocus=""),
            Field('new_password2', placeholder="Enter new password (again)"),
            WattstratSubmit('pass_change', 'Change Password'),
        )


class AccountForm(SimpleCrispyMixin, forms.ModelForm):

    class Meta:
        model = Account
        fields = ['corporate_name', 'department', 'address', 'phone', 'logo']


class UserForm(SimpleCrispyMixin, forms.ModelForm):

    class Meta:
        model = User
        fields = ['name']


class DisplayUserForm(SimpleCrispyMixin, forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email']
