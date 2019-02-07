from django.conf import settings
import numpy as np
import math
import datetime

from django.db.models import Q

from Utils.Geocodes import geodep_from_geocode, curvproj_from_geodep, mapproj_from_geocode
from wattstrat.simulation.communication import get_simulation_results, get_geocodes
import ast
from Utils.deltas import deltaYears, HourIndex
from Utils.Numpy import div0
from .SimulationResultsData import SimulationResultsData, AgregateFilter, ProxySRD
from . import SimulationResultsDataConfig as SRDConfig

from world import models as wmodels
from django.contrib.gis.db.models.functions import Area
from babel.dot.VarNameUtils import VarNames

if __debug__:
    import logging
    logger = logging.getLogger(__name__)

# import pprint
# pp = pprint.PrettyPrinter(indent=4)

ZERO_ABSOLU = -273.15

PROJECTION_CURVE_1 = settings.PROJECTION_CURVE_1
PROJECTION_CURVE_2 = settings.PROJECTION_CURVE_2
PROJECTION_MAP_1 = settings.PROJECTION_MAP_1
PROJECTION_MAP_2 = settings.PROJECTION_MAP_2
PROJECTION_SPLIT_LIMIT = settings.PROJECTION_SPLIT_LIMIT

SRDConfig.addAlias("WS.Variable.HourlyByYear", "wattstrat.simulation.SimulationResultsVariable.VariableHourlyByYear", (), {})
SRDConfig.addAlias("WS.Variable.TimelyByYear", "wattstrat.simulation.SimulationResultsVariable.VariableTimelyByYear", (), {})
SRDConfig.addAlias("WS.Variable.ByYear", "wattstrat.simulation.SimulationResultsVariable.VariableByYearFiltered", (), {})
SRDConfig.addAlias("WS.Variable.Batiment", "wattstrat.simulation.SimulationResultsVariable.VariableBatiments", (), {})

# "Query" variable on Curve
class VariableHourlyByYear(SimulationResultsData):
    # Get projection from MAP
    def __init__(self, *args, simulation, varname, label, geocodes, begin, end, shortLabel=None, field=None, unit=None, uuid=None, configuration=None, **kwargs):
        self._simulation = simulation
        # In case of bilan
        self._rsimulation = kwargs.get('realSimulation')
        self._varname = varname
        self._label = label if label is not None else VarNames.fromVarNames(varname)['label']
        self._geocodes = geocodes if type(geocodes) is list else [geocodes]
        if shortLabel is None:
            try:
                self._shortLabel = VarNames.fromVarNames(varname)['short']
            except KeyError:
                self._shortLabel = label
        else:
            self._shortLabels = shortLabel
        if field is None:
            self._field = varname
        else:
            self._field = field

        if unit is None:            
            try:
                self._unit = VarNames.fromVarNames(varname)['units']
            except KeyError:
                self._unit = "NaU"
        else:
            self._unit = unit

        if type(begin) is str:
            self._begin = datetime.datetime.strptime(begin, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self._begin = begin
        if type(end) is str:
            self._end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self._end = end
        # from client, end is inclusive.
        # for us, it's exlusive (Utils.Deltas)
        self._end += datetime.timedelta(hours=1)

        super().__init__(*args, inputs=[], nOutputs=1, uuid=uuid, configuration=configuration, **kwargs)

        self._inferGeocode = {}
        self._dept_to_remove = None
        self._valGeoMap = {}
        self._projections = {PROJECTION_CURVE_1: [], PROJECTION_CURVE_2: []}
        self._mproj = {PROJECTION_MAP_1: [], PROJECTION_MAP_2: []}

        # Populate set and list
        self._populate()

        # Iterator

        self._cCoeff = None
        self._cVMap = None
        self._year = None
        self._cRes = None
        self._deltaYear = deltaYears(1, self._begin, self._end)
        self._results = None
        self._ybegin = None
        self._yend = None

    def _populate(self):
        depgeo_map = set()
        query_curve = set()
        query_dept = set()
        if self._geocodes is None:
            self._geocodes = get_geocodes()

        for geocode in self._geocodes:
            geodep = geodep_from_geocode(geocode)
            query_curve.add(geodep)
            if geodep != geocode:
                # Commune => should infer data
                mapproj = mapproj_from_geocode(geocode)
                self._inferGeocode[geocode] = {'dep': geodep, 'proj': mapproj}
                self._valGeoMap[geodep] = {}
                self._valGeoMap[geocode] = {}
                self._mproj[mapproj].append(geocode)
                depgeo_map.add(geodep)
            else:
                query_dept.add(geocode)

        self._dept_to_remove = depgeo_map.difference(query_dept)
        
        self._mproj[PROJECTION_MAP_2].extend(list(depgeo_map))

        for geocode in query_curve:
            curveproj = curvproj_from_geodep(geocode)
            self._projections[curveproj].append(geocode)

    def _get_number_weeks(self):
        isocal = datetime.date(self._year, 12, 31).isocalendar()
        if self._year > isocal[0]:
            return 52
        return isocal[1]
    
    def _getMapVal(self):
        if self._year is None:
            return
        # get value of the map for every geocode commune and associate dep
        for proj, listGeo in self._mproj.items():
            if self._rsimulation is None:
                simulation = self._simulation
            else:
                simulation = self._rsimulation

            results = get_simulation_results(simulation=simulation,
                                             variable_name=self._varname,
                                             year=self._year,
                                             projection=proj,
                                             geocodes=listGeo
            )
            for geocode in listGeo:
                # get only weeks value
                if results:
                    val = results.get(geocode)
                    if val is None:
                        continue
                    val = val[13:]
                else:
                    val = [0.0]*self._get_number_weeks()
                    
                self._valGeoMap[geocode] = val
                
        self._cVMap = self._year

    def _calcCoeff(self):
        if self._year is None:
            return
        if self._cVMap is None or self._cVMap != self._year:
            self._getMapVal()

        for geocode, infogeo in self._inferGeocode.items():
            geodep = infogeo["dep"]
            valGeoDep = self._valGeoMap[geodep]
            valGeo = self._valGeoMap[geocode]
            coefGeo = None
            if valGeo is not None and valGeoDep is not None:
                if self._varname == 'Global_Weather_Temperature':
                    valGeo = np.add(valGeo, -ZERO_ABSOLU)
                    valGeoDep = np.add(valGeoDep, -ZERO_ABSOLU)
                coefGeo = div0(valGeo, valGeoDep)
            infogeo["coeff"] = coefGeo

        self._cCoeff = self._year
    
    def _inferData(self):
        # We calculate all data for every hour in year for missing commne
        if self._year is None or len(self._inferGeocode) == 0:
            return
        if self._cCoeff is None or self._cCoeff != self._year:
            self._calcCoeff()

        start_ind = HourIndex.hour_index_from_start_year(self._ybegin)
        stop_ind = HourIndex.hour_index_end_from_start_year(self._yend, self._year)
        
        for geocode, infogeo in self._inferGeocode.items():
            geodep = infogeo["dep"]
            # for missing cummune, data is data from curve of the departement
            geoval = self._results[geodep]
            geocoeff = self._inferGeocode[geocode]["coeff"]
            self._results[geocode] = None
            if geoval is not None and geocoeff is not None:
                # Redressed by coeff extended to hour by weeks coeff
                coeff = [c for c in geocoeff for h in range(7*24)][start_ind:stop_ind]
                # save results as list
                if self._varname == 'Global_Weather_Temperature':
                    geoval = np.add(geoval, -ZERO_ABSOLU)
                georet = np.multiply(geoval, coeff[:len(geoval)])
                if self._varname == 'Global_Weather_Temperature':
                    georet = np.add(georet, ZERO_ABSOLU)
                self._results[geocode] = list(georet)

    def _cleanResults(self):
        if self._dept_to_remove is None:
            return

        for geodep in self._dept_to_remove:
            try:
                del self._results[geodep]
            except KeyError:
                pass
        
    def _getCurveVal(self):
        # getvalue of the curve for every geocode not a commune
        if self._year is None:
            return
        # Clean results
        self._results = {}

        
        start_ind = HourIndex.hour_index_from_start_year(self._ybegin)
        stop_ind = HourIndex.hour_index_end_from_start_year(self._yend, self._year)

        # Get value from the CURVE for every geocode dep/group/...
        for proj, listGeo in self._projections.items():
            if self._rsimulation is None:
                simulation = self._simulation
            else:
                simulation = self._rsimulation

            results = get_simulation_results(simulation=simulation,
                                             variable_name=self._varname,
                                             year=self._year,
                                             projection=proj,
                                             geocodes=listGeo
            )
            for geocode in listGeo:
                if results:
                    val = results.get(geocode)
                    if val is None:
                        continue
                    else:
                        val = val[start_ind:stop_ind]
                else:
                    val = [0.0]*(stop_ind-start_ind)
                self._results[geocode]=val

    @property
    def values(self):
        if self._year is None:
            return [[]]
        if self._cRes is None or self._cRes != self._year:
            # compute value
            self._getCurveVal()
            self._inferData()
            self._cleanResults()
            self._cRes = self._year
            
        return [self._results]

    def __iter__(self):
        return self

    def __next__(self):
        self._ybegin, self._yend = next(self._deltaYear)
        self._year = self._ybegin.year
        self._outs = [{'simulation': self._simulation,
                       'varname': self._varname,
                       'label': self._label,
                       'shortLabel': self._shortLabel,
                       'field': self._field,
                       'year': self._year,
                       'begin': self._ybegin,
                       'end': self._yend,
                       'values': self.values[0],
                       'precision': 'h',
                       'unit': self._unit,
        }]

        return self._outs

    def resetIter(self):
        self._deltaYear = deltaYears(1, self._begin, self._end)

    def cost(self):
        delta = self._end - self._begin
        hoursCalc = delta.days * 24 + delta.seconds/3600
        return len(self._geocodes) * hoursCalc**(0.4)

# "Query" variable on Curve
class VariableTimelyByYear(SimulationResultsData):
    # Get projection from MAP
    def __init__(self, *args, simulation, varname, label, geocodes, begin, end, shortLabel=None, field=None, precision=None, unit=None, uuid=None, configuration=None, **kwargs):
        self._simulation = simulation
        # In case of bilan
        self._rsimulation = kwargs.get('realSimulation')
        self._varname = varname
        self._label = label if label is not None else VarNames.fromVarNames(varname)['label']
        self._geocodes = geocodes if type(geocodes) is list else [geocodes]
        if shortLabel is None:
            try:
                self._shortLabel = VarNames.fromVarNames(varname)['short']
            except KeyError:
                self._shortLabel = label
        else:
            self._shortLabels = shortLabel
            
        if field is None:
            self._field = varname
        else:
            self._field = field
        if unit is None:            
            try:
                self._unit = VarNames.fromVarNames(varname)['units']
            except KeyError:
                self._unit = "NaU"
        else:
            self._unit = unit

        if type(begin) is str:
            self._begin = datetime.datetime.strptime(begin, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self._begin = begin
        if type(end) is str:
            self._end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self._end = end

        # from client, end is inclusive.
        # for us, it's exlusive (Utils.Deltas)
        self._end += datetime.timedelta(hours=1)

        super().__init__(*args, inputs=[], nOutputs=1, uuid=uuid, configuration=configuration, **kwargs)

        self._projections = {PROJECTION_MAP_1: [], PROJECTION_MAP_2: []}

        if precision not in ['w','m','y']:
            self._precision = 'w'
        else:
            self._precision = precision

        # populate projections
        self._populate()
        
        # Iterator

        self._year = None
        self._cRes = None

        self._deltaYear = deltaYears(1, self._begin, self._end)
        self._results = None
        self._ybegin = None
        self._yend = None

    def _populate(self):
        if self._geocodes is None:
            self._projections = {PROJECTION_MAP_1: None, PROJECTION_MAP_2: None}
        else:
            for geocode in self._geocodes:
                proj = mapproj_from_geocode(geocode)
                self._projections[proj].append(geocode)

    def _get_start_index(self):
        if self._precision == 'y':
            return 0
        elif self._precision == 'm':
            return self._ybegin.month
        else:
            isocal = self._ybegin.isocalendar()
            if self._year > isocal[0]:
                return 13
            elif self._year < isocal[0]:
                return 52+12
            return isocal[1]+12

    def _get_stop_index(self):
        if self._precision == 'y':
            return 1
        elif self._precision == 'm':
            if self._yend.year != self._ybegin.year:
                # end is in january next year
                return 13
            else:
                return self._yend.month + 1
        else:
            isocal = self._yend.isocalendar()
            if self._year > isocal[0]:
                return 14
            elif self._year < isocal[0]:
                return 52+13
            return isocal[1]+13

    def _getMapVal(self):
        # getvalue of the curve for every geocode not a commune
        if self._year is None:
            return
        # Clean results
        self._results = {}

        start_ind = self._get_start_index()
        stop_ind = self._get_stop_index()

        # Get value from the CURVE for every geocode dep/group/...
        for proj, listGeo in self._projections.items():
            if self._rsimulation is None:
                simulation = self._simulation
            else:
                simulation = self._rsimulation
            results = get_simulation_results(simulation=simulation,
                                             variable_name=self._varname,
                                             year=self._year,
                                             projection=proj,
                                             geocodes=listGeo
            )
            if listGeo is None:
                for k in ["_id", "year", "projection", "varname","timestamp"]:
                    try:
                        del results[k]
                    except KeyError:
                        pass
                listGeo = results.keys()
            for geocode in listGeo:
                if results:
                    val = results.get(geocode)
                    if val is None:
                        continue
                    else:
                        val = val[start_ind:stop_ind]
                else:
                    val = [0.0]*(stop_ind-start_ind)
                self._results[geocode]=val

    @property
    def values(self):
        if self._year is None:
            return [[]]
        if self._cRes is None or self._cRes != self._year:
            # compute value
            self._getMapVal()
            self._cRes = self._year
            
        return [self._results]

    def __iter__(self):
        return self

    def __next__(self):
        self._ybegin, self._yend = next(self._deltaYear)
        self._year = self._ybegin.year
        self._outs = [{'simulation': self._simulation,
                       'varname': self._varname,
                       'label': self._label,
                       'shortLabel': self._shortLabel,
                       'field': self._field,
                       'year': self._year,
                       'begin': self._ybegin,
                       'end': self._yend,
                       'values': self.values[0],
                       'precision': self._precision,
                       'unit': self._unit,
        }]
        return self._outs

    def resetIter(self):
        self._deltaYear = deltaYears(1, self._begin, self._end)

    def cost(self):
        delta = self._end - self._begin
        hoursCalc = delta.days * 24 + delta.seconds/3600
        if self._precision == 'y':
            timecounter = hoursCalc / 8760
        elif self._precision == 'm':
            timecounter = hoursCalc / (8760/12)
        elif self._precision == 'w':
            timecounter = hoursCalc / (8760/52)

        return len(self._geocodes) * timecounter**(0.4)
        

AgregateByUnit = {
    '℃': np.mean,
    'W/m²': np.mean,
    'm/s': np.mean,
}

def VariableByKH(*args, K, precision, simulation, varname, label, geocodes, begin, end, shortLabel=None, field=None, unit=None, uuid=None, configuration=None, **kwargs):
    varname = VariableHourlyByYear(*args, simulation=simulation, varname=varname, label=label, geocodes=geocodes, begin=begin, end=end, shortLabel=shortLabel, field=field, unit=unit, uuid=uuid, configuration=configuration, **kwargs)

    def STEP(ind):
        return datetime.timedelta(hours=ind*K), None

    AM = {
        'balloon': 'DD/MM/YYYY JJh',
        'format': 'YYYYMMDDJJ',
        'minPeriod': 'hh',
    }
    timeformat = '%Y%m%d%H'
    def SLICE(ind, val, out):
        return [slice(ind*K,(ind+1)*K) for ind in range(0, math.ceil(len(val)/K))]

    def AGREGATE(ind, val, out):
        if type(val) is list:
            # Should be a list of list
            # remove value with not the same len as the first element
            if len(val) == 0:
                return []
            l = len(val[0])
            val = [v for v in val if len(v) == l]
            Fagregate = AgregateByUnit.get(out["unit"], np.sum)
            return list(Fagregate(val, axis=1))
        elif type(val) is dict:
            return {k: AGREGATE(ind, v, out) for k, v in val.items()}
        else:
            return val

    def METADATA(out, parentObject=None):
        out['timeformat'] = timeformat
        out['AMCHARTS'] = AM
        out['step'] = STEP

    obj = AgregateFilter(*args, inputs=varname, precisionName=precision, funSlicing=SLICE, funAgregate=AGREGATE, funMetaDataVar=METADATA, **kwargs)
    
    def aggregateCostForVarname():
        return varname.cost() / K**(0.4)
    obj.cost = aggregateCostForVarname
    return obj


def VariableByDay(*args, precision, simulation, varname, label, geocodes, begin, end, shortLabel=None, field=None, unit=None, uuid=None, configuration=None, **kwargs):
    return VariableByKH(*args, K=24, precision=precision, simulation=simulation, varname=varname, label=label, geocodes=geocodes, begin=begin, end=end, shortLabel=shortLabel, field=field, unit=unit, uuid=uuid, configuration=configuration, **kwargs)


def VariableBy6H(*args, precision, simulation, varname, label, geocodes, begin, end, shortLabel=None, field=None, unit=None, uuid=None, configuration=None, **kwargs):
    return VariableByKH(*args, K=6, precision=precision, simulation=simulation, varname=varname, label=label, geocodes=geocodes, begin=begin, end=end, shortLabel=shortLabel, field=field, unit=unit, uuid=uuid, configuration=configuration, **kwargs)


class VariableByYear(ProxySRD):
    # Proxy variable depending on precision.
    TransfoPrecision = {
        'd': VariableByDay,
        '6h': VariableBy6H,
    }

    def __init__(self, *args, simulation, varname, label, geocodes, begin, end,  shortLabel=None, field=None, precision=None, unit=None, uuid=None, configuration=None, **kwargs):
        self._precision = precision
        if self._precision in ['w','m','y']:
            obj = VariableTimelyByYear(*args, simulation=simulation, varname=varname, label=label, geocodes=geocodes, begin=begin, end=end, shortLabel=shortLabel, field=field, precision=precision, unit=unit, uuid=uuid, configuration=configuration, **kwargs)
        elif self._precision in VariableByYear.TransfoPrecision.keys():
            obj = VariableByYear.TransfoPrecision[self._precision](*args, precision=self._precision, simulation=simulation, varname=varname, label=label, geocodes=geocodes, begin=begin, end=end, shortLabel=shortLabel, field=field, unit=unit, uuid=uuid, configuration=configuration, **kwargs)
        else:
            obj = VariableHourlyByYear(*args, simulation=simulation, varname=varname, label=label, geocodes=geocodes, begin=begin, end=end, shortLabel=shortLabel, field=field, precision=precision, unit=unit, uuid=uuid, configuration=configuration, **kwargs)
        super().__init__(*args, obj=obj, uuid=uuid, configuration=configuration, **kwargs)
        
class VariableByYearFiltered(VariableByYear):
    def __init__(self, *args, simulation, varname, label, geocodes, begin, end,  shortLabel=None, field=None, precision=None, unit=None, uuid=None, configuration=None, **kwargs):
        # Filter simulation name first
        filterSimulation = kwargs.get("filterSimulation")
        if filterSimulation is not None:
            rsimulation, simulation = filterSimulation(simulation, varname, label, geocodes, begin, end, **kwargs)
            if simulation is None:
                raise SRDConfig.FilteredObject("simulation is empty")
                    
        # Filter begin/end date
        filterDate = kwargs.get("filterDate")
        if filterDate is not None:
            begin, end = filterDate(simulation, varname, label, geocodes, begin, end, **kwargs)
            if begin is None or end is None:
                raise SRDConfig.FilteredObject("Date is invalid")
        # Filter allowed geocodes
        filterGeocode = kwargs.get("filterGeocode")
        if filterGeocode is not None:
            geocodes = filterGeocode(simulation, varname, label, geocodes, begin, end, **kwargs)
            if len(geocodes) == 0:
                raise SRDConfig.FilteredObject("Geocodes is empty")

        # Filter allowed varname
        filterVarname = kwargs.get("filterVarname")
        if filterVarname is not None:
            varname = filterVarname(simulation, varname, label, geocodes, begin, end, **kwargs)
            if varname is None:
                raise SRDConfig.FilteredObject("varname is empty")

        super().__init__(*args, simulation=simulation, varname=varname, label=label, geocodes=geocodes, begin=begin, end=end, shortLabel=shortLabel, field=field, precision=precision, unit=unit, uuid=uuid, configuration=configuration, realSimulation=rsimulation, **kwargs)
        
        
            
    
# Infer batiments variables
class VariableBatiments(SimulationResultsData):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
        'uuid': [str],
        'steps': [int],
    }

    #TODO : for now, str for s_tot_2...
    DispatchFunctions = {
        'BySurface': lambda vc,b,c: np.multiply(vc, float(b.s_tot_2)/c.area.sq_m)
    }
    FunctionsArgs = {
        'BySurface': lambda vals, b, coms: (vals[b.geocode_com], b, coms[b.geocode_com])
    }
    FunctionsByVar = {
        None: 'BySurface'
    }
    VarWithoutBat = []
    
    def __init__(self, *args, inputs=None, nOutputs=None, funCombineVar=[], uuid=None, steps=1, configuration=None, **kwargs):
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)
        self._httpRequest = kwargs.get("httpRequest")
    def __next__(self):
        outs = []
        current = super().__next__()
        self._outs =  [self._addBatiValue(out) for out in current]
        return self._outs

    def _computeBatimentValue(self, bat, dictValues, out, ignC, osmC):
        if out["varname"] in self.VarWithoutBat:
            return None
        
        try:
            funcN = self.FunctionsByVar.get(out["varname"], self.FunctionsByVar[None])
            func=self.DispatchFunctions[funcN]
            funcArg=self.FunctionsArgs[funcN]
            return func(*funcArg(dictValues, bat, ignC))
        except ValueError:
            # Error in calculs
            # TODO
            print("Error in bat calc")
        return None    
    
    def _addBatiValue(self, out):
        dictValues = out['values']
        # Should be dict of DEP/COMM => list of values
        askedCommunes = list(dictValues.keys())
        dataBati, ignCommune, osmCommune = self._get_bati(askedCommunes)
        datasB = {bat.id_bat: self._computeBatimentValue(bat, dictValues, out, ignCommune, osmCommune)
                 for bat in dataBati}
        out['batiments'] = {k:v for k,v in datasB.items() if v is not None}
        
        return out
        
    def _get_bati(self, askedCommunes):
        if self._httpRequest is None:
            return []
        
        dataBati = self._httpRequest.user.account.communes
        ign_list = list(set(dataBati.get("communes", {}).keys()).intersection(set(askedCommunes)))
        ign_list_withoutfr = [x[2:] for x in ign_list]

        commune_ign_m = wmodels.Communes.objects.annotate(area=Area('geom')).filter(insee_com__in=ign_list_withoutfr)
        commune_ign = {'FR' + comm.insee_com: comm for comm in commune_ign_m}

        commune_osm_m = wmodels.OSMCommunes.objects.annotate(area=Area('geom')).filter(insee__in=ign_list_withoutfr)
        commune_osm = {'FR' + comm.insee: comm for comm in commune_osm_m}
        
        
        if len(ign_list) == 0:
            bati_c_query = None
        else:
            bati_c_query=Q(geocode_com__in=ign_list)

        ign_bati_list = [x['ign'] for k, x in dataBati.get("batiments", {}).items()]
        if len(ign_bati_list) == 0:
            bati_ign_query = bati_c_query
        else:
            bati_ign_query = Q(geocode_com__in=askedCommunes) & Q(id_bat__in=ign_bati_list)
            if bati_c_query is not None:
                bati_ign_query |= bati_c_query

        if bati_ign_query is not None:
            bati_ign=wmodels.Batiments.objects.filter(bati_ign_query)
        else:
            bati_ign = []
        return bati_ign, commune_ign, commune_osm
    
