from wattstrat.settings.components.dir import BASE_DIR
from scripts.constants import GEOCODES_OUT_DIR
import json
import itertools
import threading
from Utils.Latinise import Latinise
from Utils.compatibilities import merge_two_dicts
from collections import OrderedDict

class NotLoaded(Exception):
    def __init__(self, classType):
        self._classNotLoaded = classType

        
class Variables(object):
    _VARIABLES = None
    _PATH = None
    _FLATTEN_TYPE = [1]
    _CONSOLIDATE_TYPE = [1]
    _loading = threading.Lock()
    def __init__(self, variables=None, parent=None, **kwargs):
        super().__init__()
        self._sVariables = variables
        self._parent = self if parent is None else parent

    @staticmethod
    def _afterLoad():
        return True

    @staticmethod
    def _formatItem(name, data):
        raise NotImplemented("_formatItem is virtual")

    
    @classmethod
    def _load(cls):
        if not cls._loading.acquire(False):
        # Wait for it!
#        if not cls._loading.acquire():
            raise NotLoaded(cls)
        if cls._VARIABLES is not None:
            cls._loading.release()
            return True
        cls._VARIABLES = OrderedDict()
        res = json.load(open(cls._PATH, encoding='utf-8'))
        res = cls._sortLoadedData(res)
        for name, d in res.items():
            (key, data) = cls._formatItem(name, d)
            cls._VARIABLES[key] = data

        ret = cls._afterLoad()
        cls._loading.release()
        return ret

    @staticmethod
    def _sortLoadedData(res):
        return OrderedDict(res)
    
    def __iter__(self):
        return IterVariables(self._parent, iter(self._VARIABLES.keys()))

    def __getitem__(self, key):
        return self.getVar(key)
    
    def getVar(self, key):
        if not self._load():
            raise NotLoaded(self.__class__)
        self.consolidate(self._VARIABLES[key])
        return self._VARIABLES[key]

    # Flatten tree of includes with a list of includes
    @classmethod
    def flatten(cls, var):
        # cache status of flatten : flatten already ?
        todoFlatten = var.get("_flatten")
        if todoFlatten is None:
            ret = []
            # trick to show loops : bad tree looping
            var["_flatten"] = False
            # not flatten
            if var["_type"] in cls._FLATTEN_TYPE:
                # flatten only ALIAS variable inside includes
                includes = var.get("includes")
                if includes is None:
                    # Error? no includes, but not REAL variable
                    # For now, just ignore them
                    pass
                else:
                    for incl in includes:
                        ret.extend(cls.flatten(incl))
            else:
                ret = [var]
            var["includes"] = ret
            var["_flatten"] = True
        elif not todoFlatten:
            # Error, we are looping
            # TODO: print AN ERROR
            return []
        return var["includes"]

    @property
    def variables(self):
        if not self._load():
            return {}
        if self._sVariables is None:
            return {k: self.consolidate(self._VARIABLES[k]) for k in self._VARIABLES.keys()}
        
        return {k: self.consolidate(self._VARIABLES[k]) for k in self._sVariables if k in self._VARIABLES}

    def consolidate(self, var):
        # cache status of flatten : flatten already ?
        todoConsolidate = var.get("_consolidate")
        if todoConsolidate is None:
            # trick to not handle myself again or to show loops (bad tree looping)
            var["_consolidate"] = False
            if var["_type"] in self._CONSOLIDATE_TYPE:
                # Consolidate alias variables inside includes
                includes = var.get("includes")
                if includes is not None:
                    ret = []
                    for incl in includes:
                        try:
                            V = self._parent.getVar(incl)
                            # V = self.filterV(V)
                            NV = self.consolidate(V)
                            if NV is not None:
                                ret.append(NV)
                        except KeyError:
                            # No key corresponding to V
                            pass
                    var["includes"] = ret
            else:
                var["includes"] = [var]

            self.alterV(var)
            var["_consolidate"] = True
        elif not todoConsolidate:
            # Error, we are looping
            # TODO: print AN ERROR
            return None

        return var

    @classmethod
    def filterV(cls, var):
        return var

    @classmethod
    def alterV(cls, var):
        return var


class RestrictKeyMixIn(object):
    _RESTRICT_KEYS = []
    _RESTRICT_INCLUDE_KEYS = []

    @classmethod
    def filterV(cls, var):
        # flatten the variable => one level of includes
        cls.flatten(var)
        # Copy just what needed
        ret = {k: var.get(k) for k in cls._RESTRICT_KEYS if k in var}
        if "includes" in ret:
            # filter also includes var
            ret["includes"] = [{k: incl.get(k) for k in cls._RESTRICT_INCLUDE_KEYS if k in incl} for incl in var["includes"]]
        return ret

class DefaultFilterVariablesMixIn(RestrictKeyMixIn):
    _RESTRICT_KEYS = ["includes", "label", "varname"]
    _RESTRICT_INCLUDE_KEYS = ["label", "varname"]

class DefaultFilterGeocodesMixIn(RestrictKeyMixIn):
    _RESTRICT_KEYS = ["order", "includes", "label", "geocode", "sub"]
    _RESTRICT_INCLUDE_KEYS = ["label", "geocode", "sub"]

class InfosGeocodesMixIn(RestrictKeyMixIn):
    _RESTRICT_KEYS = ["order", "includes", "label", "geocode", "sub"]
    _RESTRICT_INCLUDE_KEYS = ["label", "geocode", "sub", "labelinfo"]

class ResultVariablesMixin(object):
    @staticmethod
    def alterV(var):
        # == Unit ==
        if 'unit' not in var:
            # create unit property
            allVar = var.get('includes', [])
            if len(allVar) > 0:
                var['unit'] = allVar[0]['unit']
            else:
                # unknown unit
                var['unit'] = "ukn"

class RealResultVariables(ResultVariablesMixin, Variables):
    _PATH = BASE_DIR / "static" / "results" / "tags.json"
    
    @staticmethod
    def _formatItem(name, data):
        varname = data[0]
        unit = data[1]
        tags = [t.strip() for t in data[2:]]
        return varname, {
            'tags': tags,
            'label': name,
            'unit': unit,
            'varname': varname,
            'l_label': Latinise.transform(name),
            'l_tags': list(map(Latinise.transform, tags)),
            '_type': 0,
        }

    

class AliasResultVariables(ResultVariablesMixin, Variables):
    _PATH = BASE_DIR / "static" / "results" / "alias.json"
    _CONSOLIDATE_TYPE = [1, 2]
    _FLATTEN_TYPE = [1, 2]

    @staticmethod
    def _formatItem(name, data):
        varnames = data.get('includes', [data["varname"]])
        tags = [t.strip() for t in data['tags']]
        ret = {
            'tags': tags,
            'label': name,
            'includes': varnames,
            'varname': data["varname"],
            'l_label': Latinise.transform(name),
            'l_tags': list(map(Latinise.transform, tags)),
            '_type': 1,
        }
        if "aggregate" in data and data["aggregate"]:
            ret["_type"] = 2

        return data["varname"], ret


class IterOrderVariables(object):
    def __init__(self, *iterators):
        self._iterators = iterators
        self._current = None
    def __next__(self):
        if self._current is None:
            self._current = []
            for ind in range(len(self._iterators)):
                try:
                    self._current.append(next(self._iterators[ind]))
                except StopIteration:
                    self._current.append(None)
        ind = self._indexMin(self._current)
        if ind == -1:
            raise StopIteration()
        ret = self._current[ind]
        try:
            self._current[ind] = next(self._iterators[ind])
        except StopIteration:
            self._current[ind] = None

        return ret
        
    def __iter__(self):
        return self

    @classmethod
    def _indexMin(cls, listVal):
        c = len(listVal)
        
        minimal = (9223372036854775807, "")
        ind = -1
        
        for index in range(c):
            if listVal[index] is None:
                continue
            cur = cls.order(listVal[index])
            if cur < minimal:
                ind = index
                minimal = cur
        return ind

class GeocodeIterOrderVariables(IterOrderVariables):
    @staticmethod
    def order(var):
        return (var.get("order", 99), var.get("labelmatch", ""))
    
class IterVariables(object):
    def __init__(self, objVar, iterKeys):
        self._iterObj = iterKeys
        self._objVar = objVar
        
    def __iter__(self):
        return self
    
    def __next__(self):
        v = next(self._iterObj)
        ret = self._objVar.getVar(v)
        return ret

# class IterVariables(object):
#     def __init__(self, objVar, iterKeys, key=None):
#         self._iterObj = iterKeys
#         self._objVar = objVar
#         self._key = key
        
#     def __iter__(self):
#         return self
    
#     def __next__(self):
#         v = next(self._iterObj)
#         if type(v) is dict and self._key is not None:
#             v=v[self._key]
#         ret = self._objVar.getVar(v)
#         return ret


class AliasRealVariables(Variables):
    clsREAL = None
    clsALIAS = None
    
    def __init__(self, variables=None, parent=None,  **kwargs):
        if parent is None:
            parent = self
        super().__init__(variables, parent, **kwargs)
        self._real = self.clsREAL(variables, parent=parent, **kwargs)
        self._alias = self.clsALIAS(variables, parent=parent, **kwargs)
        
    @classmethod
    def _load(cls):
        return cls.clsREAL._load() and cls.clsALIAS._load()

    def getVar(self, key):
        try:
            return self._real.getVar(key)
        except KeyError:
            pass
        d = self._alias.getVar(key)
        return d

    def __iter__(self):
        if not self._load():
            raise NotLoaded(AliasRealVariables)
        iterator = itertools.chain(iter(self._real), iter(self._alias))
        return iterator
    
    def __getitem__(self, key):
        return self.getVar(key)
            
    @property
    def variables(self):
        if self._sVariables is None:
            return {k: self.getVar(k) for k in itertools.chain(iter(self.clsREAL._VARIABLES.keys()), iter(self.clsALIAS._VARIABLES.keys()))}
        else:
            return {k: self.getVar(k) for k in self._sVariables}


class ResultVariables(RestrictKeyMixIn, AliasRealVariables):
    clsREAL = RealResultVariables
    clsALIAS = AliasResultVariables
    _RESTRICT_KEYS = ["label", "unit", "includes", "varname", "_type"]
    _RESTRICT_INCLUDE_KEYS = ["label", "unit", "varname"]
    _FLATTEN_TYPE = [1, 2]
    pass

class RealParameterVariables(Variables):
    _PATH = BASE_DIR / "static" / "simulation" / "tags.json"
    @staticmethod
    def _formatItem(name, data):
        varname = data[0]
        tags = [t.strip() for t in data[1].split(';')]
        return varname, {
            'tags': tags,
            'label': name,
            'varname': varname,
            'l_label': Latinise.transform(name),
            'l_tags': list(map(Latinise.transform, tags)),
            '_type': 0
        }

class AliasParameterVariables(Variables):
    _PATH = BASE_DIR / "static" / "simulation" / "alias.json"
    @staticmethod
    def _formatItem(name, data):
        varnames = data.get('includes', [data["varname"]])
        varname = data["varname"]
        tags = [t.strip() for t in data["tags"]]
        return varname, {
            'tags': tags,
            'label': name,
            'varname': varname,
            'includes': varnames,
            'l_label': Latinise.transform(name),
            'l_tags': list(map(Latinise.transform, tags)),
            '_type': 1,
        }

class ParameterVariables(DefaultFilterVariablesMixIn, AliasRealVariables):
   clsREAL = RealParameterVariables
   clsALIAS = AliasParameterVariables
   pass


class AliasGeo(Variables):
    _PATH = BASE_DIR / "static" / "geo" / "geocodes" / "alias.json"
    @staticmethod
    def _formatItem(name, data):
        includes = data['includes']
        return name, {
            'order': 15,
            'sub': includes,
            'includes': includes,
            'geocode': name,
            'postal': name,
            'label': data['label'],
            'labelmatch': Latinise.transform(data['label'].lower()),
            '_type': 1,
        }

# TODO: Geo like RealVariables / Variables => RealGeo

class RealGeo(Variables):
    def __init__(self, geocodes = None, groups=None, mainSimu=None,parent=None):
        super().__init__(geocodes, parent)
        self._geocodes = geocodes
        self._groupsByID = {}
        self._groups = {}
        self._mainSimu = mainSimu
        self._groupsBySet = self._loadGroups(groups) if groups is not None else None

    def _loadGroups(self, groups):
        ret = {}
        # Multiple definition of group depending on the simulation
        if isinstance(groups, list):
            # List => simu inside each members or simu not set
            groups = {self._mainSimu: groups}
        
        for simu, gs in groups.items():
            for g in gs:
                simu = g.get("simulation", simu)
                s = frozenset(g['geocodes'])
                try:
                    self._groupsByID[simu][g['id']] = s
                except KeyError:
                    self._groupsByID[simu] = { g['id']: s}
                if s in ret:
                    ret[s]['simulations'].add(simu)
                else:
                    ret[s] = {'simulations': set([simu]), 'order' : 5, 'sub': list(s), 'name': g['name'], 'geocode': g['id'], 'postal':  g['id'], 'label': g['name'], 'labelmatch': g['name'], '_type': 2}
                self._groups["%s_%s" % (g['id'], simu)] = ret[s]
        return ret

    def __iter__(self):
        if self._groups is not None and len(self._groups) > 0:
            return itertools.chain(iter(self._groups.values()), iter(self._VARIABLES.values()))
        else:
            return iter(self._VARIABLES.values())

    def getVar(self, key, simu = None):
        if key.startswith('group_'):
            g = key.split('_')
            if len(g) == 3:
                return self._groups[key]
            else:
                if simu is None:
                    simu = self._mainSimu
            set_of_geocodes = self._groupsByID[simu][key]
            return self._groupsBySet[set_of_geocodes]
        else:
            if not self._load():
                raise NotLoaded(self.__class__)
            self.consolidate(self._VARIABLES[key])
            return self._VARIABLES[key]

    @staticmethod
    def _load():
        if not RealGeo._loading.acquire(False):
            return False

        if RealGeo._VARIABLES is not None:
            RealGeo._loading.release()
            return True

        country = "france"
        geocodes = json.load(open(GEOCODES_OUT_DIR / (country + '.json')), encoding='utf-8')
        # Order geocdes

        RealGeo._VARIABLES = OrderedDict(sorted(geocodes.items(), key=lambda d: (d[1].get("order", 99), d[1].get("labelmatch", ""))))

        RealGeo._loading.release()
        return True
    
    @property
    def geocodes(self):
        if not RealGeo._load():
            return []
        if self._geocodes is None:
            return list(RealGeo._VARIABLES.values()) + self._groups
        return [self.__getitem__(geo) for geo in self._geocodes]

    @staticmethod
    def isProvinces(geocode):
        geocode = geocode.lower()
        return (len(geocode) == 7) and geocode.startswith('fr991')
    
    @staticmethod
    def isCounties(geocode):
        geocode = geocode.lower()
        return (len(geocode) == 7) and geocode.startswith('fr992')
    
    @staticmethod
    def isCities(geocode):
        geocode = geocode.lower()
        return (len(geocode) == 7) and not geocode.startswith('fr99')
    
    @staticmethod
    def isGroups(geocode):
        geocode = geocode.lower()
        return geocode.startswith('group_')
    
# class Geo(object):
#     _dgeocodes = None
#     _all = None
#     _loading = threading.Lock()
#     def __init__(self, geocodes = None, groups=None):
#         self._alias = AliasGeo(geocodes)
#         self._real = RealGeo(geocodes, groups)


#     @property
#     def iterAll(self):
#         if self._groups is not None and len(self._groups) > 0:
#             return itertools.chain(iter(self._groups.values()), iter(self._all))
#         else:
#             return iter(self._all)

#     def __getitem__(self, key):
#         if key.startswith('group_'):
#             return self._groups[key]
#         else:
#             if not self._load():
#                 raise KeyError("Asynchronous loading in course, retry later")
#             return Geo._dgeocodes[key]
            
#     @staticmethod
#     def _load():
#         if not RealGeo._load():
#             return False

#         if not AliasGeo._load():
#             return False
        
#         return True
    
#     @property
#     def geocodes(self):
#         if not Geo._load():
#             return []
#         if self._geocodes is None:
#             return list(Geo._dgeocodes.values()) + self._groups
#         return [geo for geo in self._geocodes]

#     @staticmethod
#     def isProvinces(geocode):
#         return RealGeo.isProvinces(geocode)
    
#     @staticmethod
#     def isCounties(geocode):
#         return RealGeo.isProvinces(geocode)
    
#     @staticmethod
#     def isCities(geocode):
#         return RealGeo.isProvinces(geocode)
    
#     @staticmethod
#     def isGroups(geocode):
#         return RealGeo.isProvinces(geocode)

class GeoInfos(InfosGeocodesMixIn, Variables):
    _FLATTEN_TYPE = [1, 2]
    pass

class Geo(DefaultFilterGeocodesMixIn, AliasRealVariables):
    clsREAL = RealGeo
    clsALIAS = AliasGeo

    @property
    def _groups(self):
        return self._real._groups

    @_groups.setter
    def _groups(self, groups):
        self._real._groups = self._real._loadGroups(groups) if groups is not None else None
        return self._real._groups
    
    @staticmethod
    def isProvinces(geocode):
        return RealGeo.isProvinces(geocode)
    
    @staticmethod
    def isCounties(geocode):
        return RealGeo.isCounties(geocode)
    
    @staticmethod
    def isCities(geocode):
        return RealGeo.isCities(geocode)
    
    @staticmethod
    def isGroups(geocode):
        return RealGeo.isGroups(geocode)


    # Get ordered geocodes
    def __iter__(self):
        if not self._load():
            raise NotLoaded(Geo)
        iterator = GeocodeIterOrderVariables(iter(self._real), iter(self._alias))
        return iterator

    @property
    def geocodes(self):
        ret = self._real.geocodes
        ret.extend(self._alias.variables.values())
        return ret

# Static geocode variable without group
StaticGeo = Geo()
StaticGeo._load()
