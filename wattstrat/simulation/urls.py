from django.conf.urls import url, include

from . import views

#===========================
# Territory assessment
#===========================

assessment_patterns = [
    url(r'^scan/$', views.TerritoryScanView.as_view(), name="scan"),
    url(r'^data/$', views.BilanResultsDownloadsView.as_view(), name="data")]


#===========================
# Bilan results
#===========================
results_patterns = [
    # list of all bilans
    url(r'^$', views.SimulationResultsDashboardView.as_view(), name='dashboard'),
    # link to show a bilan
    url(r'^(?P<shortid>\w+)/$',
        views.SimulationResultsExploreView.as_view(), name='explore'),
    # download a bilan
    url(r'^(?P<shortid>\w+)/downloads/(?P<filetype>\w+)$',
        views.ResultsChartsDownloadView.as_view(), name='download'),
    # basic download of bilan
    url(r'^(?P<shortid>\w+)/basicsdownload/(?P<filetype>\w+)$',
        views.ResultsBasicsDownloadView.as_view(), name='basicsdownload'),

    # Angular URL
    url(r'^(?P<shortid>\w+)/parameters/$',
        views.ResultsParametersAPIView.as_view(), name="parameters"),
    url(r'^(?P<shortid>\w+)/chart/$',
        views.ResultsChartsAPIView.as_view(), name="chart")
]


urlpatterns = [
    #===========================
    # Typeahead async
    #===========================
    url(r'^resultvariablesfilter/$',
        views.DefaultResultVariablesFilterAPIView.as_view(), name="resultvariablesfilter"),
    url(r'^geocodesfilter/$', views.DefaultGeocodesFilterAPIView.as_view(),
        name="gecodesfilter"),

    # Specific typeahead with filter for simu
    url(r'^(?P<shortid>\w+)/geocodesfilter/',
        views.BySimulationGeocodesFilterAPIView.as_view(), name="simugeocodesfilter"),
    url(r'^(?P<shortid>\w+)/resultstag/',
        views.BySimulationResultVariablesFilterAPIView.as_view(), name="simuresultvariablesfilter"),

    #===========================
    # Territory assessment
    #===========================
    url(r'^', include(assessment_patterns)),

    #===========================
    # Simulation results
    #===========================
    url(r'^', include(results_patterns, namespace="results")),

    #===========================
    # Dynamic geoJson
    #===========================
    url(r'^(?P<shortid>\w+)/map/(?P<group_id>[_\w]+).geojson/$',
        views.SimulationGeoJsonView.as_view(), name='geojson'),
    url(r'^dynamic-geojson/$', views.DynamicGeoJsonView.as_view(),
        name='dynamic_geojson'),
    url(r'^(?P<shortid>\w+)/map/(?P<group_id>[_\w]+).geojson/$',
        views.SimulationGeoJsonView.as_view(), name='simulation_geojson'),

    #===========================
    # Infos
    #===========================

    url(r'^(?P<shortid>\w+)/allresultstag/', views.BySimulationAllResultVariablesFilterAPIView.as_view(),
        name="simuallresultvariablesfilter"),
    url(r'^(?P<shortid>\w+)/geocodesinfos/',
        views.BySimulationGeocodesInfosAPIView.as_view(), name="geocodesinfos")
    ]

