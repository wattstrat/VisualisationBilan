from django.conf.urls import url
from django.contrib.gis import admin

from .views import tile_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tiles/(?P<layer>[-.a-zA-Z]+)/(?P<zoom>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+).mvt', tile_view),
]
