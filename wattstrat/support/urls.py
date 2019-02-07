from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^support/$', views.WattstratContactView.as_view(), name='support'),
    url(r'^support/', include('envelope.urls'))]
