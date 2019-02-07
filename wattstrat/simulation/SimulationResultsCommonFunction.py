import numpy as np
import copy
from Utils.Variables import Geo

AgregateByUnit = {
    '℃': np.mean,
    'W/m²': np.mean,
    'm/s': np.mean,
}

def changeLabelWithSimulation_RenameFilter_funRenameVar(var, ind, allVars, parentObject=None):
    newvar = var.copy()
    if parentObject is None:
        simuName = var["simulation"]
    else:
        simus = parentObject._kwargs.get("simus")
        if simus is None:
            simuName = var["simulation"]
        else:
            # Simulation object
            simuName = simus[var["simulation"]].name
        
    newvar["shortLabel"] = "%s(%s)" % (var["shortLabel"],simuName)
    newvar["label"] = "%s(%s)" % (var["label"],simuName)
    newvar["field"] = "%s-%s" % (var["field"],simuName)
    return newvar

def changeLabelWithGeocode_SplitDictFilter_funMetaDataVar(key, values, ind, keys, out, parentObject=None):
    geo = None
    if parentObject is not None and '_geo' in parentObject.__dict__:
        geo = parentObject._geo
        
    if geo is None:
        geo = Geo()
    newvar = out.copy()
    if len(keys) > 1:
        try:
            geoname=geo.getVar(key)["name"]
        except KeyError:
            geoname=key
            print("error with %s" % key)
            
        newvar["shortLabel"] = "%s / %s" % (out["shortLabel"], geoname)
        newvar["label"] = "%s / %s" % (out["label"], geoname)
        newvar["field"] = "%s-%s" % (out["field"], key)
    newvar["dictkey"] = key

    return newvar

def changeLabelWithGeocodeSimulation_SplitDictFilter_funMetaDataVar(key, values, ind, keys, out, parentObject=None):
    geo = None
    if parentObject is not None and '_geo' in parentObject.__dict__:
        geo = parentObject._geo
        
    if geo is None:
        geo = Geo()
    newvar = out.copy()
    if parentObject is None:
        simuName = out["simulation"]
    else:
        simus = parentObject._kwargs.get("simus")
        if simus is None:
            simuName = out["simulation"]
        else:
            # Simulation object
            simuName = simus[out["simulation"]].name

    if len(keys) > 1:
        try:
            geoname=geo.getVar(key)["name"]
        except KeyError:
            geoname=key
            print("error with %s" % key)
        newvar["shortLabel"] = "%s(%s) / %s" % (out["shortLabel"],simuName, geoname)
        newvar["label"] = "%s(%s) / %s" % (out["label"],simuName, geoname)
        newvar["field"] = "%s-%s-%s" % (out["field"],simuName, key)
    else:
        newvar["shortLabel"] = "%s(%s)" % (out["shortLabel"],simuName)
        newvar["label"] = "%s(%s)" % (out["label"],simuName)
        newvar["field"] = "%s-%s" % (out["field"],simuName)
        
    newvar["dictkey"] = key

    return newvar

def addGeocodeField_SplitDictFilter_funMetaDataVar(key, values, ind, keys, out, parentObject=None):
    geo = None
    if parentObject is not None and '_geo' in parentObject.__dict__:
        geo = parentObject._geo
         
    if geo is None:
        geo = Geo()
    newvar = out.copy()
    try:
        geoname=geo.getVar(key)["name"]
        geocode=geo.getVar(key)["geocode"]
    except KeyError:
        geoname=key
        geocode=key

    newvar["geocode"] = geocode
    newvar["geoLabel"] = geoname
    newvar["dictkey"] = key

    return newvar

def sortListWithReturn(listKeys):
    ret = list(listKeys)
    ret.sort()
    return ret


def AgregateGeocode_FilterStaticFun_funOut(out, ind, outs, parentObject=None):
    # geo = None
    # if parentObject is not None and '_geo' in parentObject.__dict__:
    #     geo = parentObject._geo
         
    # if geo is None:
    #     geo = Geo()
    newvar = out.copy()

    vals = out["values"]
        
    if type(vals) is not dict:
        print("Error, should be dict to calculate Sum foreach territories")
        return out
    Fagregate = AgregateByUnit.get(out["unit"], np.sum)

    newvar["values"] =  list(Fagregate(list(vals.values()), axis=0))
    # geocodes = []
    # geolabels = []
    # for key in vals.keys():
    #     try:
    #         geoname=geo.getVar(key)["name"]
    #         geocode=geo.getVar(key)["geocode"]
    #     except KeyError:
    #         geoname=key
    #         geocode=key
    #     geocodes.append(geocode)
    #     geolabels.append(geoname)
        

    # newvar["geocode"] = ','.join(geocodes)
    newvar["geocode"] = ','.join(list(vals.keys()))
    #newvar["geoLabel"] = 'Somme de ' + ','.join(geolabels)
    newvar["geoLabel"] = 'Somme des territoiress'

    return newvar



def AgregateTerritory_FilterStaticFun_funOut(out, ind, outs, parentObject=None):
    if parentObject is None:
        return out
    territories = parentObject._kwargs.get("territories")
    replace = parentObject._kwargs.get("replace", False)

    if territories is None:
        return out

    vals = out["values"]
    if replace:
        retvals = {}
    else:
        retvals = vals
        
    if type(vals) is not dict:
        print("Error, should be dict to calculate Sum foreach territories")
        return out
    Fagregate = AgregateByUnit.get(out["unit"], np.sum)
    

    for territory in territories:
        if territory["id"] in vals:
            retvals[territory["id"]] = vals[territory["id"]]
        else:
            try:
                retvals[territory["id"]] = list(Fagregate([vals[geocode] for geocode in territory["geocodes"]], axis=0))
            except KeyError as e:
                print("Some geocode missing : %s" % str(e))

    out["values"] = retvals
    return out



def AgregateInputs_FilterStaticFun_funOuts(outs, parentObject=None):
    if len(outs) == 0:
        return []
    elif len(outs) == 1:
        return outs
    
    val = outs[0]["values"]
    
    if parentObject is not None and parentObject._funOutsMeta is not None:
        ret = parentObject._funOutsMeta(outs, parentObject)
    else:
        ret = { k: copy.deepcopy(v) for k,v in outs[0].items() if k != "values"}

    Fagregate = AgregateByUnit.get(ret["unit"], np.sum)
    if type(val) is list:
        # Should be a list of list
        # pad/remove items if not same size
        if len(val) == 0:
            return [[]]
        l = len(val)
        vals = [v["values"][:l]+[0]*(l-len(v["values"])) for v in outs]
        ret["values"] = list(Fagregate(val, axis=0))
    elif type(val) is dict:
        geo = set()
        for v in outs:
            geo = geo.union(set(v["values"].keys()))
        ret["values"] = {g: list(Fagregate([v["values"][g] for v in outs if  g in v["values"]], axis=0)) for g in geo}
    else:
        ret["values"] = list(Fagregate([v["values"] for v in outs]))

    return [ret]
                         
def AgregateInputs_FilterStaticFun_funOutsMeta(outs, parentObject=None):
    if len(outs) == 0:
        out = {}
    else:
        out = outs[0]
    ret = { k: copy.deepcopy(v) for k,v in out.items() if k != "values"}

    if parentObject is None:
        return ret

    for var in ['varname', 'label', 'shortLabel', 'field']:
        ret[var]=parentObject._kwargs.get(var, ret.get(var, var))
    return ret
