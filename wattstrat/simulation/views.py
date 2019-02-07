from copy import deepcopy
import json
from dateutil import parser as datetimeparser
import datetime

import itertools
from datetime import date, datetime
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.views import generic, View
from django.conf import settings
from django.contrib import messages
from django.http.response import Http404, HttpResponse
from django.utils.dateparse import parse_datetime

from braces.views import LoginRequiredMixin, UserFormKwargsMixin
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework import status

from pymongo import MongoClient

from Utils.JSONencoder import jsonEncoder
from collections import OrderedDict
from Utils.Latinise import Latinise
import re
import geojson
from Utils.GeoJSON import GeoJSON
from Utils.Variables import ResultVariables, ParameterVariables, Geo, NotLoaded, GeoInfos
from wattstrat.simulation.models import Simulation

from wattstrat.simulation.forms import RemovalForm, TerritoryAssessmentForm

from wattstrat.simulation.results import SimulationResultWorkspace, SimulationResultDownloader

from wattstrat.simulation.serializers import SimulationSerializer
from wattstrat.simulation.SimulationResultsContainer import ZipContainer

from wattstrat.simulation.FilterParamByUser import FilterParamByUser, GraphFilterParam, DOWNLOAD_DATA_YEAR

from Utils.compatibilities import flatten
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .messages import SUPPRESSION_SUCCESS, SUPPRESSION_ERROR, SUPPRESSION_DENIED, REQUEST_ERROR

"""
TODO:
 + Remove all csrf_exempt by using 
    https://djangocn.readthedocs.io/zh/stable-1.11.x/ref/csrf.html#setting-the-token-on-the-ajax-request
"""
if __debug__:
    import logging
    logger = logging.getLogger(__name__)

# import pprint
# pp = pprint.PrettyPrinter(indent=4)

ONE_YEAR_DURATION = 180  # computation duration of one year of simulation
AVERAGE_WEATHER_YEAR = '0000'

download_list_scan = []
download_list_ges = []
download_list_dynamic = []
download_list_compare = []

with open('babel/dot/result_tags.json') as myfile:
    d = json.load(myfile)
    for key in d.keys():
        if 'GES' in key:
            download_list_ges.append(d[key][0])
        if 'Bilan' in key:
            download_list_scan.append(d[key][0])
        if 'Réseau' in key[0:6]:
            download_list_scan.append(d[key][0])

download_list_scan += download_list_ges
download_list_dynamic = download_list_scan
download_list_compare = download_list_scan

download_list_ges.sort()
download_list_scan.sort()
download_list_dynamic.sort()
download_list_compare.sort()

BasicDownloadBySimuType = {
    None: {
        'geocodes': lambda simu: ['FR99999'] + flatten([group['geocodes'] for group in simu.territory_groups]),
        'parameters': []
    },
    'scan': {
        'geocodes': lambda simu: flatten([group['geocodes'] for group in simu.territory_groups]),
        'parameters': download_list_scan
    },
    'ges': {
        'geocodes': lambda simu: flatten([group['geocodes'] for group in simu.territory_groups]),
        'parameters': download_list_ges
    },
    'dynamic': {
        'geocodes': lambda simu: ['FR99999'] + [group['id'] for group in simu.territory_groups] + flatten([group['geocodes'] for group in simu.territory_groups]),
        'parameters': download_list_dynamic
    },
    'compare': {
        'geocodes': lambda simu: ['FR99999'] + [group['id'] for group in simu.territory_groups] + flatten([group['geocodes'] for group in simu.territory_groups]),
        'parameters': download_list_compare
    }
}


#===========================
# BaseViews and Mixins
#===========================


class SimulationMenuMixin(object):
    menu_builder = None
    default_section = None

    def get_context_data(self, **context):
        section = self.kwargs.get('section', self.default_section)
        context.update(
            self.menu_builder.get_menu_context_for_section(
                section, expand=True))
        return super().get_context_data(**context)


class StaticSimulationByPathMixin(object):
    YEAR = DOWNLOAD_DATA_YEAR

    PATH_TO_STATIC_CONFIG = {
        '/simulation/data/': {"shortid": 'bilan %d' % YEAR, "simu_type": "data"}
    }

    def get_object(self):
        try:
            shortid = self.kwargs.get('shortid')
            if shortid is not None:
                if shortid[0:5] != 'bilan':
                    return super().get_object()
            else:
                config = self.PATH_TO_STATIC_CONFIG[self.request.path]
                self.kwargs.update(config)
            self.simulation = self.object = self._create_simulation_object()
            return self.simulation
        except KeyError:
            return super().get_object()

    def _create_simulation_object(self):
        YEAR = self.YEAR
        BILAN_PARAM = {
            'territory_groups': [
                {'geocodes': ['FR99999'],
                 'id': 'group_1',
                 'name': 'Territoire'}
            ],
            'date': datetime(YEAR, 1, 1, 0, 0, 0, 0, tzinfo=None),
            'territory_groups': [],
            'description': 'Bilan of year %d' % YEAR,
            'simu_type': 'data',
            'name': 'bilan%d' % YEAR,
            'shortid': 'bilan%d' % YEAR,
        }
        simu = Simulation(**BILAN_PARAM)
        simu.framing_parameters = {
            'subcategory': None,
            'category': None,
            'territory_groups': [{
                'geocodes': ['FR99999'],
                'id': 'group_1',
                'name': 'Territoire'
            }],
            'simu_type': 'data',
            'climate_scenario': 'climate_normal',
            'ecogrowth': 2,
            'demography': 'insee_ref',
            'period': {
                'end': '%d-12-31T23:00:00.000Z' % YEAR,
                'start': '%d-01-01T00:00:00.000Z' % YEAR, }
        }
        simu.account_id = self.request.user.account_id

        return simu


class BaseSimulationMixin(object):
    model = Simulation
    context_object_name = 'simulation'
    slug_url_kwarg = 'shortid'
    slug_field = 'shortid'

    def dispatch(self, request, *args, **kwargs):
        simulation = self.get_object()
        if not (simulation.account_id == self.request.user.account_id):
            raise PermissionError()

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        if hasattr(self, 'simulation'):
            return self.simulation
        else:
            self.simulation = self.object = super().get_object()
            return self.simulation


class BaseSimulationView(LoginRequiredMixin,
                         StaticSimulationByPathMixin,
                         BaseSimulationMixin,
                         generic.DetailView):
    pass


class SimulationPermission(BasePermission):

    def has_object_permission(self, request, view, simulation):
        return (simulation.account_id == request.user.account_id)


class SimulationAPIMixin(object):
    queryset = Simulation.objects.all()
    lookup_field = 'shortid'
    permission_classes = (IsAuthenticated, SimulationPermission)
    renderer_classes = [JSONRenderer]

    def update_def_with_territorialize_def(self, section, definition):
        # By default, do not calculate data
        pass

    def get_section_and_simulation_and_definition(self):
        simulation = self.get_object()
        section = self.kwargs['section']
        definition = simulation_parameters_definitions.get(section)
        self.update_def_with_territorialize_def(section, definition)
        if definition is None:
            raise Http404('Invalid parameters section : {}'.format(section))
        return section, simulation, definition

#===========================
# Territory assessment Configuration/Launching
#===========================


class TerritoryScanView(LoginRequiredMixin,
                        UserFormKwargsMixin, generic.CreateView):
    template_name = "simulation/scan.html"
    form_class = TerritoryAssessmentForm

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        simulation = self.object = form.save()

        geocodes = self.request.POST.get('geocodes', '').split(',')
        simu_type = "scan"
        year = self.request.POST.get('weather')
        if year == 'average':
            year = AVERAGE_WEATHER_YEAR
        territory_group = {
            'id': 'group_1',
            'name': _('Cartography'),
            'geocodes': geocodes,
        }

        simulation.framing_parameters = {
            'weather_type': {'type': 'faithful', 'years': [year]},
            'subcategory': None,
            'category': None,
            'territory_groups': [territory_group],
            'simu_type': simu_type,
            'climate_scenario': 'climate_normal',
            'ecogrowth': 2,
            'demography': 'insee_ref',
            'period': {
                'start': '{}-01-01T00:00:00.000Z'.format(year),
                'end': '{}-12-31T23:00:00.000Z'.format(year)
            }
        }
        simulation.simu_type = simu_type
        simulation.territory_groups = [territory_group]
        simulation.save()
        return redirect('simulation:results:dashboard')



#===========================
# Simulation results
#===========================




class SimulationResultsDashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "simulation/results/dashboard.html"

    def get_context_data(self, **context):
        simulations = Simulation.objects.all().filter(
            Q(account__users=self.request.user)
        )
        serializer = SimulationSerializer(simulations, many=True)
        return super().get_context_data(
            simulations=json.dumps(serializer.data),
            removal_form=RemovalForm(),
            ** context)

    def post(self, request, *args, **kwargs):
        print(request.POST)
        if 'action' in request.POST and 'removal' in request.POST['action']:
            form = RemovalForm(request.POST)
            if form.is_valid():
                context = form.cleaned_data.copy()
                simulation = context['simulation']
                if simulation is None:
                    messages.error(request, REQUEST_ERROR)
                if simulation.account.id == request.user.account.id:
                    if __debug__:
                        logger.info("Suppression of simulation {} by {}: SUCCESS".format(
                            simulation.shortid, request.user))
                        simulation.delete()
                        messages.success(request, SUPPRESSION_SUCCESS)
                else:
                    if __debug__:
                        logger.info("Suppression of simulation {} by {}: DENIED".format(
                            simulation.shortid, request.user))
                    messages.error(request, SUPPRESSION_DENIED)
            else:
                messages.error(request, SUPPRESSION_ERROR)
        return redirect('simulation:results:dashboard')


class SimulationResultsExploreView(BaseSimulationView):
    template_name = "simulation/results/explore.html"

    def get_context_data(self, **context):
        simulations = Simulation.objects.all().filter(
            Q(account__users=self.request.user)
        )
        serializer = SimulationSerializer(simulations, many=True)
        cSimuSerializer = SimulationSerializer(self.simulation)
        return super().get_context_data(
            simulations=json.dumps(serializer.data),
            current_simulation=json.dumps(cSimuSerializer.data),
            simuName=self.simulation.name,
            simuShortID=self.simulation.shortid,
            simulationType='results',
            ** context)



class BilanResultsDownloadsView(BaseSimulationView):
    template_name = "simulation/results/explore.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['simuid'] = 'bilan2015'
        context['simulationType'] = 'data'
        context['dataYear'] = DOWNLOAD_DATA_YEAR
        return context


class ResultAPIMixin(object):
    queryset = Simulation.objects.all()
    lookup_field = 'shortid'
    permission_classes = (IsAuthenticated, SimulationPermission)
    renderer_classes = [JSONRenderer]

    def get_section_and_simulation_and_definition(self):
        simulation = self.get_object()
        section = self.kwargs['section']
        definition = result_parameters_definitions.get(section)
        if definition is None:
            raise Http404('Invalid parameters section : {}'.format(section))
        return section, simulation, definition


class ResultsParametersAPIView(StaticSimulationByPathMixin, ResultAPIMixin, RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        simulation = self.get_object()

        # Initial start date
        start_date = simulation.framing_parameters['period']['start']
        end_date = simulation.framing_parameters['period']['end']
        simu_type = simulation.simu_type
        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'territory_groups': simulation.territory_groups,
            'simu_type': simu_type
        })


class AllSimuParameters(StaticSimulationByPathMixin, ResultAPIMixin, RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        _, simulation, _ = self.get_section_and_simulation_and_definition()
        dates = simulation.framing_parameters['period']
        return Response({'start': dates['start'].replace(
            tzinfo=None), 'end': dates['end'].replace(tzinfo=None)})


# TODO : Filtre, Users, Simus
class ResultsChartsAPIView(ResultAPIMixin, BaseSimulationView):
    permission_classes = (IsAuthenticated, SimulationPermission)
    renderer_classes = [JSONRenderer]

    MAXGRAPH = 20

    def post(self, request, *args, **kwargs):
        body = request.body.decode('utf-8')
        data = json.loads(body)
        simulations = Simulation.objects.all().filter(
            Q(account__users=self.request.user)
        )
        graph = data['workspace']
        FilterParams = GraphFilterParam(simulations)
        Workspace = SimulationResultWorkspace(
            None, graph, filterParams=FilterParams, httpRequest=request)
        response = {}

        nbGraph = 0
        for results in Workspace:
            for result in results:
                if nbGraph > self.MAXGRAPH:
                    response['more'] = {'more': True}
                    return Response(response)
                divid = 'graph-%d' % (nbGraph)
                result['divid'] = divid
                # TODO Change!
                result['simuType'] = 'None'
                # TODO GraphType!!!!
                # Just one index TODO
                result['indexParam'] = 0
                response[divid] = result
                nbGraph += 1

        return HttpResponse(json.dumps(response, default=jsonEncoder),
                            content_type='application/json')


class ZIPRenderer(BaseRenderer):
    media_type = 'application/zip'
    format = 'zip'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

@method_decorator(csrf_exempt, name='dispatch') # Django 1.9!
class ResultsChartsDownloadView(BaseSimulationView):
    queryset = Simulation.objects.all()
    lookup_field = 'shortid'
    permission_classes = (IsAuthenticated, SimulationPermission)
    renderer_classes = [ZIPRenderer]

    def post(self, request, *args, **kwargs):
        body = request.body.decode('utf-8')
        data = json.loads(body)
        simulations = Simulation.objects.all().filter(
            Q(account__users=self.request.user)
        )

        graph = data['workspace']
        FilterParams = GraphFilterParam(simulations)
        Workspace = SimulationResultWorkspace(
            None, graph, filterParams=FilterParams, httpRequest=request)

        simulation = self.get_object()
        simuID = simulation.shortid
        simu_type = None

        zipname = "results-%s.zip" % simuID
        responseZip = ZipContainer(zipname=zipname)
        filenames = {}
        for results in Workspace:
            filename = results['filename']
            if filename in filenames:
                nbSet = filenames.get(filename, 1)
                filenames[filename] = nbSet + 1
                filename = '%d-%s' % (nbSet, filename)
            else:
                filenames[filename] = 1

            responseZip.write(results['data'], filename=filename)

        response = HttpResponse(content_type='application/zip')
        response[
            'Content-Disposition'] = 'attachment; filename="{}"'.format(zipname)

        response.write(responseZip.read())
        return response

# Default free download of some variables fo some geocodes

@method_decorator(csrf_exempt, name='dispatch') # Django 1.9!
class ResultsBasicsDownloadView(BaseSimulationView):
    queryset = Simulation.objects.all()
    lookup_field = 'shortid'
    permission_classes = (IsAuthenticated, SimulationPermission)
    renderer_classes = [ZIPRenderer]

    def get(self, request, *args, **kwargs):
        simulation = self.get_object()
        simuID = simulation.shortid

        simu_type = simulation.simu_type
        start_date = parse_datetime(simulation.framing_parameters[
            'period']['start']).date()
        end_date = parse_datetime(simulation.framing_parameters[
            'period']['end']).date()
        precision = 'm'
        filetype = kwargs['filetype']
        conf = BasicDownloadBySimuType.get(
            simu_type, BasicDownloadBySimuType[None])
        parameters = conf['parameters']
        geocodes = conf['geocodes'](simulation)
        nbSet = 0
        zipname = "results-%s.zip" % simuID
        responseZip = ZipContainer(zipname=zipname)
        lastZip = None
        # TODO : WARNING
        # multiple year not linearize => multiple file with same name in the Zip
        # => confusing for user because extract zip will override csv
        # HERE: we linearize because monthly precision.
        results = SimulationResultDownloader(simulation=simulation,
                                             parameters=parameters,
                                             start_date=start_date,
                                             end_date=end_date,
                                             geocodes=geocodes,
                                             precision=precision,
                                             fileType=filetype,
                                             ZipIt=True)
        for result in results:
            filename = 'set-%d' % (nbSet)
            lastZip = result
            responseZip.write(result, filename=filename)
            nbSet += 1

        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(zipname)

        if nbSet == 1:
            response.write(lastZip)
        else:
            response.write(responseZip.read())

        return response

#===========================
# Dynamic geoJson
#===========================


class DynamicGeoJsonMixin(GeoJSON):

    def dispatch(self, request, *args, **kwargs):
        if DynamicGeoJsonMixin.geojson_features is None:
            self.load_geojson_features()

        return super().dispatch(request, *args, **kwargs)


class DynamicGeoJsonView(DynamicGeoJsonMixin, generic.View):

    def get(self, request):
        geocodes = request.GET.get('geocodes')
        geocodes = json.loads(geocodes) if geocodes else []
        geojson_data = self.get_geojson(geocodes)
        return HttpResponse(geojson.dumps(geojson_data),
                            content_type='application/json')


class SimulationGeoJsonView(DynamicGeoJsonMixin, BaseSimulationView):

    def get(self, request, shortid, group_id):
        simulation = self.get_object()
        geojson_data = self.get_geojson(
            simulation.groups_geocodes.get(
                group_id, []))
        return HttpResponse(geojson.dumps(geojson_data),
                            content_type='application/json')


#===========================
# Async Type-ahead
#===========================
@method_decorator(csrf_exempt, name='dispatch') # Django 1.9!
class FilterAPIViewMixin(generic.View):
    permission_classes = (IsAuthenticated, SimulationPermission)
    renderer_classes = [JSONRenderer]

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        typed = data.get("typed", "")
        exclude = data.get("exclude")
        if exclude is None:
            exclude = []
        else:
            exclude = list(map(lambda x: x.lower(), exclude))
        res = self._filter(typed, exclude)
        return HttpResponse(json.dumps(res),
                            content_type='application/json')

@method_decorator(csrf_exempt, name='dispatch') # Django 1.9!
class SimulationFilterAPIViewMixin(BaseSimulationView):
    permission_classes = (IsAuthenticated, SimulationPermission)
    renderer_classes = [JSONRenderer]


    def post(self, request, shortid):
        data = json.loads(request.body.decode('utf-8'))
        typed = data.get("typed", "")
        exclude = data.get("exclude")
        if exclude is None:
            exclude = []
        else:
            exclude = list(map(lambda x: x.lower(), exclude))
        self._simulation = self.get_object()
        self._mainSimu = shortid
        res = self._filter(typed, exclude)

        return HttpResponse(json.dumps(res),
                            content_type='application/json')


class DefaultFilterAPIMixin(object):
    MAX = 10

    def _filter(self, typed, exclude=[]):
        ret = {}
        gene = self._generator(typed)
        try:
            while (self.MAX == 0) or (len(ret) < self.MAX):
                data = next(gene)
                if data[self._key].lower() not in exclude:
                    ret[data[self._key]] = data
        except StopIteration:
            pass
        return [self._filterOut(d) for d in self._sort(ret)]

    def _sort(self, ret):
        return list(ret.values())

    def _filterOut(self, data):
        return data


class ResultVariablesFilterAPIMixin(DefaultFilterAPIMixin):

    def _filterOut(self, data):
        return ResultVariables.filterV(data)




class GeocodesFilterAPIMixin(DefaultFilterAPIMixin):

    def _filterOut(self, data):
        return Geo.filterV(data)


class DefaultGeocodeGeneratorAPIMixin(Geo):

    def __init__(self):
        super().__init__()
        self._key = "geocode"

    def _generator(self, typed):
        try:
            if not self._load():
                print("Failed loading Geocodes")
                return iter([])
        except NotLoaded:
            return iter([])

        matchRE = re.compile(Latinise.transform(typed), flags=re.IGNORECASE)
        geneexactlabel = (s for s in iter(
            self) if matchRE.match(s["labelmatch"]))
        genelabel = (s for s in iter(self) if typed in s["labelmatch"])
        genepostal = (s for s in iter(self) if typed in s["postal"])
        genegeocode = (s for s in iter(self) if typed in s["geocode"].lower())
        gene = itertools.chain(geneexactlabel, genelabel,
                               genepostal, genegeocode)
        return gene

    def _sort(self, ret):
        return sorted(ret.values(), key=lambda city: (city.get("order", 99), city.get("labelmatch", "")))


class DefaultResultVariablesGeneratorAPIMixin(ResultVariables):

    def __init__(self):
        super().__init__()
        self._key = "varname"
        self._re = None

    def _computeRE(self, typed):
        self._re = list(map(lambda x: re.compile(Latinise.transform(x),
                                                 flags=re.IGNORECASE),
                            filter(bool, typed.split(" "))))

    def _generator(self, typed):
        try:
            if not self._load():
                return iter([])
        except NotLoaded:
            return iter([])
        self._computeRE(typed)

        genevarname = (s for s in self.variables.values() if all(
            map(lambda regexp: bool(regexp.search(s["varname"])), self._re)))
        genelabel = (s for s in self.variables.values() if all(
            map(lambda regexp: bool(regexp.search(s["l_label"])), self._re)))
        genetags = (s for s in self.variables.values() if all(map(
            lambda regexp: any([bool(regexp.search(tag)) for tag in s["l_tags"]]), self._re)))
        geneunit = (s for s in self.variables.values() if all(
            map(lambda regexp: bool(regexp.search(s["unit"])), self._re)))
        gene = itertools.chain(genevarname, genelabel, genetags, geneunit)
        return gene


class AllResultVariablesGeneratorAPIMixin(ResultVariables):

    def __init__(self):
        super().__init__()
        self._key = "varname"

    def _generator(self, typed):
        try:
            if not self._load():
                return iter([])
        except NotLoaded:
            return iter([])
        gene = (s for s in self.variables.values())
        return gene



class DefaultGeocodesFilterAPIMixin(DefaultGeocodeGeneratorAPIMixin, GeocodesFilterAPIMixin, FilterAPIViewMixin):
    pass


class DefaultResultVariablesFilterAPIMixin(DefaultResultVariablesGeneratorAPIMixin, ResultVariablesFilterAPIMixin, FilterAPIViewMixin):
    pass


class DefaultGeocodesFilterAPIView(DefaultGeocodesFilterAPIMixin):
    pass


class DefaultResultVariablesFilterAPIView(DefaultResultVariablesFilterAPIMixin):
    pass


class UserGeocodesFilterAPIMixin(DefaultGeocodeGeneratorAPIMixin, GeocodesFilterAPIMixin):

    def _generator(self, typed):
        filterParam = FilterParamByUser(
            self._simulation, request=None, args=None, kwargs=None)
        if self._groups is None or len(self._groups) == 0:
            self._groups = [T for T in self._simulation.territory_groups]

        gene = super()._generator(typed)
        return (p for p in filterParam.geocodeFilterIterator(gene))


class BySimulationGeocodesFilterAPIView(UserGeocodesFilterAPIMixin, SimulationFilterAPIViewMixin):
    pass


class UserAllGeocodesFilterAPIMixin(DefaultGeocodeGeneratorAPIMixin, GeocodesFilterAPIMixin):
    MAX = 0
    _FLATTEN_TYPE = [1, 2]

    def _generator(self, typed):
        filterParam = FilterParamByUser(
            self._simulation, request=None, args=None, kwargs=None)
        if self._groups is None or len(self._groups) == 0:
            self._groups = [T for T in self._simulation.territory_groups]
        self._load()
        if filterParam._simuType not in ["ges", "scan"]:
            yield from self._noFilterAllGenerator()
            raise StopIteration()
        gene = super()._generator("")
        for p in filterParam.geocodeFilterIterator(gene):
            if 'sub' in p:
                ret = dict(p)
                if self.isGroups(ret["geocode"]):
                    ret['includes'] = [self.getVar(g) for g in ret['sub']]
                    ret['includes'].append({'labelinfo': "Tout le groupe", "geocode": ret[
                                           "geocode"], "sub": ret["sub"], "label": ret["label"], '_type': 3, "order": 0})
            else:
                ret = p
            yield ret
        raise StopIteration()

    def _noFilterAllGenerator(self):
        yield {'order': 10, 'label': 'France', 'geocode': 'FR99999', '_type': 0, '_flatten': True,
               'includes': [{'labelinfo': "Tous les départements et communes", "geocode": 'FR99999', "label": "France", "order": 0}],
               'sub': [{'label': "Tous les départements et communes"}]}
        for k, v in self._groups.items():
            ret = dict(v)
            ret['includes'] = [self.getVar(g) for g in ret['sub']]
            ret['includes'].append({'labelinfo': "Tout le groupe", "geocode": ret["geocode"],
                                    "label": ret["label"], 'sub': ret['sub'], '_type': 3, "order": 0})
            yield ret


class BySimulationGeocodesInfosAPIView(UserAllGeocodesFilterAPIMixin, SimulationFilterAPIViewMixin):

    def _filter(self, typed, exclude=[]):
        ret = {}
        gene = self._generator(typed)
        try:
            while (self.MAX == 0) or (len(ret) < self.MAX):
                data = next(gene)
                if data[self._key].lower() not in exclude:
                    ret[data[self._key]] = data
        except StopIteration:
            pass
        return [self._filterOut(d) for d in self._sort(ret)]

    def _filterOut(self, data):
        ret = deepcopy(data)
        if "includes" in ret:
            ret["includes"] = sorted(ret["includes"], key=lambda x: (
                x.get("order", 99), x.get("labelinfo", x.get("label", ""))))
        return GeoInfos.filterV(ret)


class UserResultVariablesFilterAPIMixin(DefaultResultVariablesGeneratorAPIMixin, ResultVariablesFilterAPIMixin):

    def _generator(self, typed):
        filterParam = FilterParamByUser(
            self._simulation, request=None, args=None, kwargs=None)
        gene = super()._generator(typed)

        return (p for p in filterParam.parameterFilterIterator(gene))


class BySimulationResultVariablesFilterAPIView(UserResultVariablesFilterAPIMixin, SimulationFilterAPIViewMixin):
    pass


class UserAllResultVariablesFilterAPIMixin(AllResultVariablesGeneratorAPIMixin, ResultVariablesFilterAPIMixin):
    MAX = 0

    def _generator(self, typed):
        filterParam = FilterParamByUser(
            self._simulation, request=None, args=None, kwargs=None)
        gene = super()._generator("")

        return (p for p in filterParam.parameterFilterIterator(gene))


class BySimulationAllResultVariablesFilterAPIView(UserAllResultVariablesFilterAPIMixin, SimulationFilterAPIViewMixin):
    pass

#    url(r'^parameterstag/$', views.ConfigurationParametersTagsAPIView.as_view(), name="parameterstag"),



class SimulationResultVariablesAPIView(generic.View):
    pass
