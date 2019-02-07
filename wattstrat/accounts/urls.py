from django.conf.urls import url

from . import views

#======================
# Authentication
#======================
urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^signup/$', views.SignUpView.as_view(), name='signup'),
    url(r'^email-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$$', views.EmailConfirmView.as_view(),
        name='email-confirm'),
    url(r'^password-change/$', views.PasswordChangeView.as_view(),
        name='password-change'),
    url(r'^password-reset/$', views.PasswordResetView.as_view(),
        name='password-reset'),
    url(r'^password-reset-done/$', views.PasswordResetDoneView.as_view(),
        name='password-reset-done'),
    url(r'^password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$$', views.PasswordResetConfirmView.as_view(),
        name='password-reset-confirm')]

#======================
# Accunt management
#======================
urlpatterns += [
    url(r'^userinfo/', views.UserInfos.as_view(), name="userinfo"),
    url(r'^account/$', views.AccountDetailView.as_view(), name='account'),
    url(r'^account/edit/$', views.AccountEditView.as_view(), name='account_edit'),
    url(r'^user/edit/$', views.UserEditView.as_view(), name='user_edit')]
