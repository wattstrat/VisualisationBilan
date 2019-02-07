from django.conf.urls import url, include

from . import views

#===========================
# MAP with OL
#===========================
urlpatterns = [
    url(r'^bati/(?P<zoom>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+).mvt$',
        views.BatiTilesView.as_view(), name='batiments')]
