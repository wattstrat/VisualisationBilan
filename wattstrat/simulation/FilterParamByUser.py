import re
from Utils.Variables import Geo
import datetime

DOWNLOAD_DATA_YEAR = 2015

# import pprint
# pp = pprint.PrettyPrinter(indent=4)


class FilterIterator(object):

    def __init__(self, iterator):
        if hasattr(iterator, '__next__'):
            self._iterator = iterator
        else:
            self._iterator = iter(iterator)

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            elm = self._filter(next(self._iterator))
            if elm is not None:
                return elm

    def _filter(self, elm):
        return elm


class REFilterIterator(FilterIterator):

    def __init__(self, variables, RE):
        super().__init__(variables)
        self._re = RE

    def _filter(self, elm):
        if bool(self._re.search(elm)):
            return elm


class StopEvaluation(Exception):

    def __init__(self, retValue):
        self._ret = retValue


class FunFilterIterator(FilterIterator):

    def __init__(self, variables, *filters, fun=None):
        super().__init__(variables)
        self._filters = filters
        self._fun = fun

    def _filter(self, elm):
        if self._fun is None:
            return elm
        prev = []
        ret = True
        try:
            for filt in self._filters:
                ret = self._fun(filt._filter(elm), ret, prev)
            prev.append(ret)
        except StopEvaluation as e:
            ret = e._ret

        if ret:
            return elm
        else:
            None
    # Default basic function for filter with

    @staticmethod
    def Unionfilter(elmFiltered, oldRet, prev):
        ret = elmFiltered is None
        if ret:
            raise StopEvaluation(True)
        return False

    @staticmethod
    def Intersectfilter(self, elmFiltered, oldRet, prev):
        if elmFiltered is None:
            raise StopEvaluation(False)
        return True

    @staticmethod
    def DiffSymfilter(self, elmFiltered, oldRet, prev):
        ret = (elmFiltered is not None) ^ oldRet
        return ret


class ChoicesFilterIterator(FilterIterator):

    def __init__(self, variables, allowedVariables):
        super().__init__(variables)
        self._allowed = allowedVariables

    def _filter(self, elm):
        if elm in self._allowed:
            return elm


class GeocodesFilterIterator(ChoicesFilterIterator):

    def _filter(self, elm):
        if type(elm) is str:
            # Got just the geocode
            return super()._filter(elm)
        else:
            # Complexe => dict
            return elm if super()._filter(elm["geocode"]) is not None else None


class GraphFilterParam(object):

    def __init__(self, computedSimulations):
        self._computedSimulations = {simu.shortid: simu for simu in computedSimulations}

    def filterSimulation(self, simulation, varname, label, geocodes, begin, end, **kwargs):
        if simulation[0:5] == 'bilan':
            # We have a real simuID equal to bilan => MeteorData
            return None, simulation
        if simulation not in self._computedSimulations:
            return None, None
        simu = self._computedSimulations[simulation]
        if simu.simu_type == 'scan':
            # Should be one year bilan.
            # Change shortid to bilanYEAR but do not save model!
            start_year = simu.framing_parameters['period']['start'][0:4]
            simu.real_shortid = 'bilan%s' % start_year
            # bilan accessible via shortid
            self._computedSimulations[simu.shortid] = simu
            return simu.real_shortid, simu.shortid
        else:
            return None, simu.shortid

    @staticmethod
    def toDate(date):
        if type(date) is str:
            return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            return date

    @staticmethod
    def dateIntersect(begin1, end1, begin2, end2):
        latest_start = max(begin1, begin2)
        earliest_end = min(end1, end2)
        if latest_start <= earliest_end:
            return latest_start, earliest_end
        else:
            return None, None

    @staticmethod
    def dateUnion(begin1, end1, begin2, end2):
        latest_end = max(end1, end2)
        earliest_start = min(begin1, begin2)
        return earliest_start, latest_end

    def filterDate(self, simulation, varname, label, geocodes, begin, end, **kwargs):
        begin = self.toDate(begin)
        end = self.toDate(end)
        if simulation[0:5] == 'bilan':
            # We have a real simuID equal to bilan => MeteorData
            sBegin = datetime.datetime(year=DOWNLOAD_DATA_YEAR, month=1, day=1)
            sEnd = datetime.datetime(year=DOWNLOAD_DATA_YEAR, month=12, day=31, hour=23)
        else:
            sBegin = self.toDate(self._computedSimulations[simulation].framing_parameters['period']['start'])
            sEnd = self.toDate(self._computedSimulations[simulation].framing_parameters['period']['end'])
        retBegin, retEnd = GraphFilterParam.dateIntersect(begin, end, sBegin, sEnd)

        return retBegin, retEnd

    def filterGeocodes(self, simulation, varname, label, geocodes, begin, end, **kwargs):
        # TODO!
        return geocodes

    def filterVarname(self, simulation, varname, label, geocodes, begin, end, **kwargs):
        # TODO
        return varname


# For now, just filter geocodes to split it as we want


class GraphFilterIterator(FilterIterator):

    def __init__(self, graphs, simuType, groups, parentFilterParam=None, geo=None, parameters=None):
        super().__init__(graphs)
        self._parentFilterParam = parentFilterParam
        self._geo = Geo(None, groups=list(groups.values())) if geo is None else geo
        self._simuType = simuType
        self._parameters = parameters

    def _filter(self, elm):
        geocodes = elm['territory']
        if self._parentFilterParam is None:
            # No parent => do not filter geocodes
            filterGeocodes = iter(geocodes)
        else:
            filterGeocodes = self._parentFilterParam.geocodeFilterIterator(geocodes)
        geocodes = []
        askedGeocodes = list(filterGeocodes)
        for geo in askedGeocodes:
            if (self._simuType in ["scan"] and self._geo.isGroups(geo)) or \
               (elm["graphicType"] == "map" and self._simuType not in ["scan"]):
                try:
                    subGeo = self._geo[geo]["sub"]
                except KeyError:
                    subGeo = []
                geocodes.extend(filter(lambda x: x not in askedGeocodes, subGeo))
            else:
                geocodes.append(geo)

        return {
            'precision': elm['precision'],
            'territory': geocodes,
            'startDate': elm['startDate'],
            'graphicType': elm['graphicType'],
            'endDate': elm['endDate'],
            'parameters': elm.get('parameters', self._parameters)
        }


class FilterParamByUser(object):

    def __init__(self, simulation, request, *args, parameters=None, graphs=None, geocodes=None, **kwargs):
        self._simulation = simulation
        self._request = request
        self._args = args
        self._kwargs = kwargs

        self._geocodes = geocodes
        self._parameters = parameters
        self._graphs = graphs
        self._groups = {}

        self._init()

    def _init(self):
        self._simuType = self._simulation.simu_type
        self._groupsGeocodes = []
        for F in self._simulation.territory_groups:
            # Add group id in groups geocodes
            self._groups[F['id']] = F
            self._groupsGeocodes.append(F['id'])
            self._groupsGeocodes.extend(F['geocodes'])

    @property
    def parameters(self):
        return list(self.parameterFilterIterator(self._parameters))

    def parameterFilterIterator(self, parameters):
            return iter(parameters)

    @property
    def geocodes(self):
        return list(self.geocodeFilterIterator(self._geocodes))

    def geocodeFilterIterator(self, geocodes):
        if self._simuType in ["scan"]:
            return GeocodesFilterIterator(geocodes, self._groupsGeocodes)
        else:
            # no filter
            return iter(geocodes)

    @property
    def graphs(self):
        return list(self.graphFilterIterator(self._graphs))

    def graphFilterIterator(self, graphs):
        return GraphFilterIterator(graphs, self._simuType, self._groups, self, parameters=self.parameters)
