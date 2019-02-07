import csv
import io
import numpy as np
import itertools
from collections import OrderedDict
from zipfile import ZipFile
from datetime import timedelta, datetime, time
from dateutil.relativedelta import relativedelta
from toposort import toposort_flatten
from copy import deepcopy
import uuid

from django.conf import settings
from django.utils.dateparse import parse_datetime

from wattstrat.simulation.communication import get_simulation_results

from Utils.deltas import deltaYears, HourIndex
import Utils.GeoJSON as GeoJSON
from Utils.Variables import Geo, StaticGeo
import babel.dot.VarNameUtils
from babel.dot.averaged_variables import weighted_update

from . import SimulationResultsVariable as srv
from . import SimulationResultsProvider as srp
from . import SimulationResultsData as srd
from . import SimulationResultsGraph as srg

from .SimulationResultsCommonFunction import changeLabelWithGeocode_SplitDictFilter_funMetaDataVar,changeLabelWithGeocodeSimulation_SplitDictFilter_funMetaDataVar, addGeocodeField_SplitDictFilter_funMetaDataVar, changeLabelWithSimulation_RenameFilter_funRenameVar, sortListWithReturn, AgregateTerritory_FilterStaticFun_funOut, AgregateGeocode_FilterStaticFun_funOut, AgregateInputs_FilterStaticFun_funOuts, AgregateInputs_FilterStaticFun_funOutsMeta
from .SimulationResultsContainer import ZipContainer
from . import SimulationResultsDataConfig as SRDConfig

# import pprint
# pp = pprint.PrettyPrinter(indent=4)

SRDConfig.addAlias("WS.SplitFilter.DictMetaDataChangeVarMultipleSimu", "wattstrat.simulation.SimulationResultsData.SplitDictFilter", (), {"funMetaDataVar":changeLabelWithGeocodeSimulation_SplitDictFilter_funMetaDataVar})
SRDConfig.addAlias("WS.SplitFilter.DictMetaDataChangeVar", "wattstrat.simulation.SimulationResultsData.SplitDictFilter", (), {"funMetaDataVar":changeLabelWithGeocode_SplitDictFilter_funMetaDataVar})
SRDConfig.addAlias("WS.Utils.RenameFilterWithSimulation", "wattstrat.simulation.SimulationResultsData.RenameFilter", (), {"funRenameVar":changeLabelWithSimulation_RenameFilter_funRenameVar})

SRDConfig.addAlias("WS.SplitFilter.DictMetaDataAddVar", "wattstrat.simulation.SimulationResultsData.SplitDictFilter", (), {"funMetaDataVar":addGeocodeField_SplitDictFilter_funMetaDataVar})

SRDConfig.addAlias("WS.Utils.LineriseFilterTimely", "wattstrat.simulation.SimulationResultsData.LineriseFilter", (), {'steps': None, "funCombineVar":srd.LineriseFilter._combineTimelyVariable})

SRDConfig.addAlias("WS.Utils.AggregateTerritory", "wattstrat.simulation.SimulationResultsData.FilterStaticFun", (), {"funOut":AgregateTerritory_FilterStaticFun_funOut})
SRDConfig.addAlias("WS.Utils.AggregateGeocode", "wattstrat.simulation.SimulationResultsData.FilterStaticFun", (), {"funOut":AgregateGeocode_FilterStaticFun_funOut})
SRDConfig.addAlias("WS.Utils.AggregateInputs", "wattstrat.simulation.SimulationResultsData.FilterStaticFun", (), {"funOuts":AgregateInputs_FilterStaticFun_funOuts, "funOutsMeta":AgregateInputs_FilterStaticFun_funOutsMeta})



if __debug__:
    import logging
    logger = logging.getLogger(__name__)

# TODO
# SRDConfig.addAlias("FunctionFilter", "AgregateFilter", (), {})
# SRDConfig.addAlias("FunctionFilter", "AgregateFilter", (), {})

class SRDUser(object):
    def __init__(self, username, simus, MetaFunctions = {}):
        self._username = username
        self._simus = simus
    @property
    def MetaFunctions(self):
        return self._MetaFunctions
    @MetaFunctions.setter
    def MetaFunctions(self, mf):
        self._MetaFunctions = mf
        

class SRDSimu(object):
    def __init__(self, simuUUID, user, restrictions):
        self._simuUUID = simuUUID
        self._user = user
        self._restrictions = restriction
        self._MetaFunctions = {}


class SimulationResultWorkspace(object):
    END = [
        'WS.Graph.map',
        'WS.Graph.lineChart',
        'WS.Graph.stackedLineChart',
        'WS.Graph.pieChart',
        'WS.Graph.histofreqChart',
        'WS.Graph.histodateChart',
        'WS.Provider.CSV',
        'WS.Provider.XLSX',
        'WS.Provider.Zip',
        'WS.Provider.LocalFile',
        'WS.Provider.Concat',
        'WS.Provider.ConcatFields',
        'WS.Container.Concat',
        'WS.Container.ConcatFields',
        'WS.Container.Zip',
        'WS.Container.LocalFile',
        #### Graphic Provider
        'WS.Provider.Graphic.map',
        'WS.Provider.Graphic.lineChart',
        'WS.Provider.Graphic.stackedLineChart',
        'WS.Provider.Graphic.pieChart',
        'WS.Provider.Graphic.histofreqChart',
        'WS.Provider.Graphic.histodateChart',
        ### TEST
        "WS.Utils.LineriseFilterTimely"
    ]

    def __init__(self, user, request=None, filterParams=None, simus=None, httpRequest=None):
        self._user = user
        self._httpRequest = httpRequest
        self._graph = None
        if self._user is not None:
            self._MetaFunction = self._user.MetaFunctions
        else:
            self._MetaFunction = {}
        
        self._requestCellByID = None
        self._requestGraph = None
        self._request = request
        self._endNodes = None
        self._accGraph = None
        self._instanceSRD = None
        self._graphProvider = None
        self._filterParams = filterParams
        self._simus = None
        if simus is not None:
            self._simus = { simu.shortid: simu for simu in simus}
        elif filterParams is not None:
            self._simus = filterParams._computedSimulations

    def _initGraphProvider(self):
        if self._graph is None:
            if self._request is None:
                raise Exception("No request to parse")
            self.buildGraph(self._request)
        if self._endNodes is None:
            endNodes,accGraph = self._removeNotAccessible(typeAccessible = SimulationResultWorkspace.END)
            self._endNodes = endNodes
            self._accGraph = accGraph
        if self._instanceSRD is None:
            self._instanceSRD = self._instanciateSRD(self._accGraph)
        if self._graphProvider is None:
            self._graphProvider = itertools.chain(*[self._instanceSRD[nodeID] for nodeID in self._endNodes])

    def __iter__(self):
        return self

    def __next__(self):
        if self._graphProvider is None:
            self._initGraphProvider()
        
        data = next(self._graphProvider)

        return data

    def buildGraph(self, requestGraph):
        cells = deepcopy(requestGraph)
        self._requestGraph = cells
        MetaFun = self._MetaFunction

        hCells = {}

        links = {}
        hCellsP = {}
        for cell in cells:
            hCells[cell["id"]] = cell
            parent = cell.get("parent")
            if cell["type"] == "devs.Link":
                try:
                    links[parent][cell["id"]] = cell
                except KeyError:
                    links[parent] = {cell["id"]:  cell}
                continue
            elif cell["type"] == "WS.MetaFunctionImpl":
                if cell["name"] in MetaFun:
                    print("Override previous def of Meta function %s" % cell["name"])
                MetaFun[cell["name"]] = cell
                # This meta function is from this request
                cell["localToRequest"] = True
            try:
                hCellsP[parent][cell["id"]] = cell
            except KeyError:
                hCellsP[parent] ={cell["id"]: cell}

        # Add cells & links to Meta Function local to this request

        for mfName, mf in MetaFun.items():
            if mf["localToRequest"]:
                mf["childCells"] = hCellsP[mf["id"]]
                mf["childLinks"] = links[mf["id"]]
    
        deps = {nID: {MetaFun[cell["name"]]["id"] for cID,cell in nCells.items() if cell["type"] in ["WS.MetaFunctionImpl","WS.MetaFunction"]} for nID,nCells in hCellsP.items()}
        for cellID in  toposort_flatten(deps):
            if cellID is None or (cellID in hCellsP and hCellsP[cellID].get("localToRequest", False)):
                self._flattenCell(cellID, links.get(cellID, {}),hCellsP.get(cellID), hCells, links, hCellsP, MetaFun)

        self._requestCellByID = hCells
        self._MetaFunction = MetaFun
        self._graph = {"cells": hCellsP.get(None), "links": links.get(None, {})}
        
    def _flattenCell(self, pCellID, cLinks, Cells, hCells, links, hCellsP, MetaFun):
        if Cells is None:
            return
        # Get all links to a specific cellID
        hLinks = {nID: {'in': {}, 'out': {}} for nID in Cells.keys()}
        for linkID,link in cLinks.items():
            try:
                hLinks[link["source"]["id"]]["out"][link["source"]["port"]].append(link)
            except KeyError:
                hLinks[link["source"]["id"]]["out"][link["source"]["port"]] = [link]
            try:
                hLinks[link["target"]["id"]]["in"][link["target"]["port"]].append(link)
            except KeyError:
                hLinks[link["target"]["id"]]["in"][link["target"]["port"]] = [link]
    
        for cellID in list(Cells.keys()):
            cell = Cells[cellID]
            if cell["type"] == "WS.MetaFunction" or cell["type"] == "WS.MetaFunctionImpl":
                metaImpl = MetaFun[cell["name"]]
                metaImplID = metaImpl["id"]
                dups, dupsLinks = self._duplicateMeta(pCellID, metaImpl,metaImpl["childLinks"], metaImpl["childCells"])
                self._recoverLinks(dups, dupsLinks, hLinks[cell["id"]], cLinks)
                # Add remainding Link and cells to global Links & cell
                # Add non-virtual cells
                for nid,node in dups.items():
                    if node["type"][0:10] != "WS.virtual":
                        Cells[nid]=node
                # All links to virtual stuff should be removed in recoverLinks
                cLinks.update(dupsLinks)
                cell["parent"] = None
                del Cells[cellID]
    
        
    def _recoverLinks(self, dups, dupsLink, linkCellMeta, cLinks):
        nLink = {}
        for lID in list(dupsLink.keys()):
            link = dupsLink[lID]
            if dups[link["source"]["id"]]["type"] == "WS.virtual.In":
                if dups[link["target"]["id"]]["type"] == "WS.virtual.Out":
                    link["target"]["virtual"] = True
                nLink[link["source"]["port"]] = link["target"]
            elif dups[link["target"]["id"]]["type"] == "WS.virtual.Out":
                nLink[link["target"]["port"]] = link["source"]
            else:
                continue
            del dupsLink[lID]
            
        for portID, links in linkCellMeta["in"].items():
            if nLink.get(portID) is None:
                # no link with name, delete links
                for link in links:
                    del cLinks[link["id"]]
            else:
                if nLink[portID].get("virtual", False):
                    # Source & Target are virtual
                    oLinks = linkCellMeta["out"][nLink[portID]["port"]]
                    if len(oLinks) == 0:
                        # No out link delete input link
                        for link in links:
                            del cLinks[link["id"]]
                    elif len(links) != len(oLinks):
                        # Not the same length : use only the first one
                        for link in links:
                            link["target"] = oLinks[0]["target"]
                        # delete all others oLinks
                        for ind in range(1,len(oLinks)):
                            del cLinks[oLinks[ind]["id"]]
                    else:
                        # Same length : map one to one
                        for iLink, oLink in zip(links, oLinks):
                            iLink["target"] = oLink["target"]
                            del cLinks[oLink["id"]]
                else:
                    for link in links:
                        link["target"] = dict(nLink[portID])
        for portID, links in linkCellMeta["out"].items():
            if nLink.get(portID) is None or nLink[portID].get("virtual", False):
                # ignore virtual to virtual : should be done by previous loop
                continue
            for link in links:
                link["source"] = dict(nLink[portID])
    
    def _duplicateMeta(self, parent,metaImpl,linksMeta, cellMeta):
        # deepcopy cellMeta / linksMeta
        nLinks = deepcopy(linksMeta)
        nCells = deepcopy(cellMeta)
        # oldUUID => randomOne (dict comprehension)
        mappingLinks = { k: str(uuid.uuid4()) for k in nLinks.keys()}
        mappingCells = { k: str(uuid.uuid4()) for k in nCells.keys()}
        # mapping oldUUID => newUUID for links
        retCells = { nID: nCells[oID] for oID,nID in mappingCells.items()}
        retLinks = { nID: nLinks[oID] for oID,nID in mappingLinks.items()}
    
        for k,c in retCells.items():
            c["id"] = k
            c["parent"] = parent
        for k,l in retLinks.items():
            l["id"] = k
            l["parent"] = parent
            l["source"]["id"] = mappingCells[l["source"]["id"]]
            l["target"]["id"] = mappingCells[l["target"]["id"]]
        return retCells,retLinks

    def _removeNotAccessible(self, typeAccessible = None, uuidAccessible = None):
        if self._graph is None:
            return
        if typeAccessible is None:
            accType = []
        elif typeAccessible is str:
            accType = [typeAccessible]
        else:
            accType = typeAccessible

        if uuidAccessible is None:
            accUUID = []
        elif uuidAccessible is str:
            accUUID = [uuidAccessible]
        else:
            accUUID = uuidAccessible

        endNodes = set()
        
        for cellID,cell in self._graph["cells"].items():
            if cell["type"] in accType or cell["id"] in accUUID:
                endNodes.add(cell["id"])

        reverseLinks = self._buildReverseLinks()
        normalLink = self._buildLinks()
        # Remove ending node with out link
        for nodeID in list(endNodes):
            if nodeID in normalLink:
                endNodes.remove(nodeID)
        nodesGraph = self._parcoursGraph(endNodes,links=reverseLinks)
        retLinks = self._buildLinks(inclNodes=nodesGraph)
        retRevLinks = self._buildReverseLinks(inclNodes=nodesGraph)
        retNodes = {nodeUUID: self._graph["cells"][nodeUUID] for nodeUUID in nodesGraph}
        return endNodes, {"cells": retNodes, "links": retLinks, "revLinks": retRevLinks}
        
    def _buildAllLinks(self, reverse, inclNodes=None):
        retLinks = {}
        if reverse:
            keyStr = ("target", "source")
        else:
            keyStr = ("source", "target")
        for linkID, link in self._graph["links"].items():
            if inclNodes is not None and (link["source"]["id"] not in inclNodes or link["target"]["id"] not in inclNodes):
                continue
            fID = link[keyStr[0]]["id"]
            tID = link[keyStr[1]]["id"]
            pfID = link[keyStr[0]]["port"]
            ptID = link[keyStr[1]]["port"]
            try:
                retLinks[fID][pfID] = {'linkID' : linkID, 'port': ptID, 'id': tID}
            except KeyError:
                retLinks[fID] = {pfID: {'linkID' : linkID, 'port': ptID, 'id': tID}}
        return retLinks

    def _buildReverseLinks(self, inclNodes=None):
        return self._buildAllLinks(True, inclNodes)
    
    def _buildLinks(self, inclNodes=None):
        return self._buildAllLinks(False, inclNodes)
    
    def _parcoursGraph(self, startNodes, nodes=None, links=None, alreadyVisits = None):
        if alreadyVisits is None:
            alreadyVisits = set()
        if nodes is None:
            nodes = set(self._graph["cells"].keys())
        if links is None:
            links = self._buildLinks(inclNodes = nodes)

        alreadyVisits |= startNodes
        accNodes = {target["id"] for node in startNodes for port, target in links.get(node, {}).items()}
        newAccNodes = accNodes - alreadyVisits
        if len(newAccNodes) == 0:
            return alreadyVisits
        return self._parcoursGraph(newAccNodes, nodes=nodes, links=links, alreadyVisits=alreadyVisits)
    
    def _instanciateSRD(self, accGraph):
        instances = {}
        others_kwargs = {}
        if self._httpRequest is not None:
            others_kwargs["httpRequest"] = self._httpRequest
        if self._simus is not None:
            others_kwargs["simus"] = self._simus
        deps = { nID: { vtID["id"] for tID,vtID in accGraph["revLinks"].get(nID, {}).items()} for nID,cell in accGraph["cells"].items()}
        for nID in toposort_flatten(deps):
            kwargs = {port: {"cell": accGraph["cells"][t["id"]], "inst": instances[t["id"]], "tPort": t["port"]} for port, t in accGraph["revLinks"].get(nID,{}).items()}
            try:
                if self._filterParams is None:
                    instances[nID] = SRDConfig.getSRDFromCell(accGraph["cells"][nID]["type"], cell=accGraph["cells"][nID], cellInputs=kwargs, **others_kwargs)
                else:
                    instances[nID] = SRDConfig.getSRDFromCell(accGraph["cells"][nID]["type"], cell=accGraph["cells"][nID], cellInputs=kwargs,
                                                              filterSimulation=self._filterParams.filterSimulation,
                                                              filterDate=self._filterParams.filterDate,
                                                              filterGeocodes=self._filterParams.filterGeocodes,
                                                              filterVarname=self._filterParams.filterVarname,
                                                              **others_kwargs)
            except SRDConfig.FilteredObject:
                # TODO print error
                instances[nID] = None
        return instances

    def cost(self):
        if self._instanceSRD is None:
            self._initGraphProvider()
        if self._instanceSRD is not None:
            return sum([SRD.cost() for key, SRD in self._instanceSRD.items()])
        return 0
    

class SimulationResultDownloader(object):
    FILETYPE = {
        'csv': srp.CSVProvider,
        'xlsx': srp.XLSXProvider,
    }

    def __init__(self, simulation, parameters,
                 start_date, end_date, precision,
                 geocodes, fileType, ZipIt=False):
        self._simuObj = simulation
        self._parameters = parameters
        self._simulation = simulation.shortid
        self._precision = precision

        # Start at midnight of the start date.
        # Don't go before the start of the studied period
        perimeter_period_start = parse_datetime(self._simuObj.framing_parameters[
                                                'period']['start']).replace(tzinfo=None)
        self._start_date = max(datetime.combine(start_date, time()), perimeter_period_start)
        perimeter_period_end = parse_datetime(self._simuObj.framing_parameters['period']['end']).replace(tzinfo=None)
        # complete date with hour=23
        perimeter_period_end = datetime.combine(perimeter_period_end, time(23, 0, 0))
        self._end_date = min(datetime.combine(end_date, time(23, 0, 0)), perimeter_period_end)
        # [start, end] provided and delta need [start, end [
        ## ALREADY DONE???? TO CHECK
#        self._end_date += timedelta(hours=1)
        self._realSimulation = None
        # GES or SCAN ? => realSimulation=bilanYEAR
        if simulation.simu_type in ['scan', 'ges']:
            self._realSimulation = "bilan%d" % self._start_date.year
            
        self._geocodes = geocodes if type(geocodes) is list else [geocodes]
        self._geo = Geo()
        self._fileType = fileType

        self._paramFetcher = {}
        self._graphProvider = None
        self._container = ZipContainer(zipname="results-%s.zip" % self._simulation) if ZipIt else None
        self._initProvider()
        self._iterate = False

    def _initFetcher(self):
        for param in self._parameters:
            self._paramFetcher[param] = srd.FilterStaticFun(
                inputs=srv.VariableByYear(
                    simulation=self._simulation, varname=param, label=None,
                    geocodes=self._geocodes, begin=self._start_date, end=self._end_date,
                    precision=self._precision, realSimulation=self._realSimulation),
                funOut=AgregateTerritory_FilterStaticFun_funOut, replace=False,
                territories=self._simuObj.territory_groups);
            self._paramFetcher[param] = srd.SplitDictFilter(
                inputs=self._paramFetcher[param], funMetaDataVar=addGeocodeField_SplitDictFilter_funMetaDataVar, funSortKey=sortListWithReturn)
            if self._precision in ['d', 'w', 'm', 'y']:
                self._paramFetcher[param] = srd.LineriseFilter(
                    inputs=self._paramFetcher[param], steps=None, funCombineVar=srd.LineriseFilter._combineTimelyVariable)
            self._paramFetcher[param] = srd.BufferedSpecificOutputsIterable(self._paramFetcher[param], list(range(len(self._geocodes)+len(self._simuObj.territory_groups))))

    def _initProvider(self):
        self._initFetcher()

        # Split each results to have one file by geocode

        # Sort param
        parameters = list(self._parameters)
        parameters.sort()
        geocodes = list(self._geocodes)+[t["id"] for t in self._simuObj.territory_groups]
        geocodes.sort()

        filenames = []
        for indexGeo in range(len(geocodes)):
            filename = geocodes[indexGeo]
            try:
                try:
                    filename = StaticGeo.getVar(geocodes[indexGeo])["name"]
                except KeyError:
                    filename = geocodes[indexGeo]
            except (NotLoaded,KeyError):
                pass
            filenames.append(filename)
            
        self._Providers = [SimulationResultDownloader.FILETYPE[
            self._fileType](inputs=[srd.SpecificOutputsIterable(self._paramFetcher[parameters[indexParam]], [indexGeo]) for indexParam in range(len(parameters))], filename=filenames[indexGeo]) for indexGeo in range(len(geocodes))]

    def getDataFile(self):
        if self._container is None:
            return [data for data in P for P in self._Providers]
        for P in self._Providers:
            for data in P:
                self._container.write(data)
        return self._container.read()

    def __iter__(self):
        self._iterate = False
        return self

    def __next__(self):
        if self._iterate:
            raise StopIteration()
        self._iterate = True
        return self.getDataFile()
