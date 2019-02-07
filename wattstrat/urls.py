from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
import wattstrat.accounts.urls
import wattstrat.simulation.urls
import wattstrat.support.urls
import wattstrat.map.urls
from . import views
from django.conf import settings
from django.conf.urls import include

from world import urls as worldURLs


if settings.DEBUG:
    import debug_toolbar
    from django.contrib.staticfiles import views as staticviews


urlpatterns = [
    url(r'^$', views.HomePage.as_view(), name='home'),
    #url(r'^usecase/$', TemplateView.as_view(template_name="usecase.html"), name='usecase'),
    #url(r'^formation/$', TemplateView.as_view(template_name="formation.html"), name='formation'),
    #url(r'^clients/$', TemplateView.as_view(template_name="clients.html"), name='clients'),
    #url(r'^platform/$', TemplateView.as_view(template_name="platform.html"), name='platform'),
    url(r'^tos/$', TemplateView.as_view(template_name="terms_of_service.html"), name='tos'),
    url(r'^', include(wattstrat.accounts.urls, namespace='accounts')),
    url(r'^simulation/', include(wattstrat.simulation.urls, namespace='simulation')),
    url(r'^', include(wattstrat.support.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^guide/?$', views.UserGuideByWikiView.as_view(), name='guide'),
    url(r'^guide/(?P<path>.+)$',
        views.UserGuideByWikiView.as_view(), name='guidePath'),

    # world APP
    url(r'^world/', include(worldURLs, namespace="world")),
    #===========================
    # Map tiles vector
    #===========================

    url(r'^map/', include(wattstrat.map.urls, namespace='map')),
]

urlpatterns += [url(r'^maintenance-mode/', include('maintenance_mode.urls'))]

if settings.DEBUG:
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        # User-documents results
        #        url(r'^filesdownload/(?P<path>[-0-9a-f]*/.*)$', staticviews.serve, {
        #            'document_root': settings.FILERESULTS_ROOT,
        #            'show_indexes': True,
        #        }),
    ]
    # User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
