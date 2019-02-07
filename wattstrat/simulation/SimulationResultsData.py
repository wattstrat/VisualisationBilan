import itertools

import ast

from .SimulationResultsCommonFunction import changeLabelWithGeocode_SplitDictFilter_funMetaDataVar, addGeocodeField_SplitDictFilter_funMetaDataVar

if __debug__:
    import logging
    logger = logging.getLogger(__name__)

from . import SimulationResultsDataConfig as SRDConfig

# import pprint
# pp = pprint.PrettyPrinter(indent=4)

class EmptyConfig(Exception):
    pass




class AdditionalParams(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

class SimulationResultsDataCosts(object):
    def cost(self):
        return 0.0


# Iterator on specific output on SimulationResultsData
class SpecificOutputsIterable(SRDConfig.DynamicLoader, SimulationResultsDataCosts, AdditionalParams):
    def __init__(self, inputVar, listOutputIndexes, *args, varname2index=None, **kwargs):
        # Bypass super()
        SRDConfig.DynamicLoader.__init__(self,  *args, **kwargs)
        AdditionalParams.__init__(self, *args, **kwargs)
        self._input = inputVar
        if listOutputIndexes is None:
            listOutputIndexes = list(range(self._input.nOutputs))
        self._outputIndexes = listOutputIndexes
        self._var2ind = varname2index

    def __iter__(self):
        return self

    def __next__(self):
        ret = []
        for k in self._outputIndexes:
            try:
                ret.append(self._input[k])
            except (IndexError, KeyError, StopIteration):
                pass
        if len(ret) == 0:
            raise StopIteration            
        return ret

    def __getitem__(self, key):
        if type(key) is str:
            key = self._var2ind[key]
        if type(key) is int:
            if key >= len(self._outputIndexes):
                raise IndexError("%d is out of bound (%d)" % (key, len(self._outputIndexes)))
            index = key
        else:
            raise TypeError("%s (%s) is not a correct indexing value (type)" % ( key, type(key)))
        return self._input[self._outputIndexes[index]]

class BufferedSpecificOutputsIterable(SpecificOutputsIterable):
    def __init__(self, inputVar, listOutputIndexes, *args, varname2index=None, **kwargs):
        super().__init__(inputVar, listOutputIndexes, *args, varname2index=varname2index, **kwargs)
        self._accessed = {}
        self._outs = {}
        self._index = {}
        self._indexIn = {}

    def __iter__(self):
        return self

    def __next__(self):
        ret = []
        for k in range(len(self._outputIndexes)):
            try:
                ret.append(self.__getitem__(k))
            except StopIteration:
                pass
        if len(ret) == 0:
            raise StopIteration
            
        return ret

    def __getitem__(self, key):
        if type(key) is str:
            key = self._var2ind[key]
        if type(key) is int:
            if key >= len(self._outputIndexes):
                raise IndexError("%d is out of bound (%d)" % (key, len(self._outputIndexes)))
            index = key
        else:
            raise TypeError("%s (%s) is not a correct indexing value (type)" % ( key, type(key)))

        indexIt = self._index.get(index, None)
        indexOut = self._outputIndexes[index]
        outIt = self._indexIn.get(indexOut, -1)

        #If outIt == -1 => indexIt is None
        if indexIt is None:
            # Never access this output => return first value
            indexIt = 0
        else:
            indexIt += 1

        if outIt < indexIt:
            # should be < by 1
            ret = self._input[indexOut]
            outIt += 1
            self._indexIn[indexOut] = outIt
            d = self._outs.get(outIt, {})
            d[indexOut] = ret
            self._outs[outIt] = d
        else:
            ret = self._outs[indexIt][indexOut]
            
        # Access first cache line one more time
        if indexIt not in self._accessed:
            self._accessed[indexIt] = 1
        else:
            self._accessed[indexIt] += 1
        if self._accessed[indexIt] > len(self._outputIndexes):
            self.dropCache(indexIt)

        self._index[index] = indexIt
        return ret

    def dropCache(self, index):
        try:
            del self._outs[index]
        except IndexError:
            pass
    

class SimulationResultsData(SRDConfig.DynamicLoader, SimulationResultsDataCosts, AdditionalParams):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
        'uuid': [str],
        }

    @staticmethod
    def _checkInput(el):
        if isinstance(el, (SimulationResultsData, SpecificOutputsIterable)):
            return el
        else:
           raise TypeError("Inputs (%s) type is not SimulationResultsData subclass instance or string but %s" %  (el, type(el)))

    
    def __init__(self, *args, inputs=None, nOutputs=None, uuid=None, configuration=None, **kwargs):
        # Bypass super
        SRDConfig.DynamicLoader.__init__(self, *args, **kwargs)
        AdditionalParams.__init__(self, *args, **kwargs)
        super().__init__(*args, **kwargs)
        if type(inputs) is not list:
            self._inputs = [inputs]
        else:
            self._inputs = inputs
        self._outs = None
        self._conf = configuration
        self._nOutputs = nOutputs
        self._actualNumberOutput = 0
        self._id = uuid

        self._buildInputs()
        
        # Iterator index

        self._cIndex = None
        self._cOutIndex = None
        self._varname2index = {}

    def _buildInputs(self):
        retInputs = []
        for el in self._inputs:
            if el is None:
                
                # Discard None iput
                # TODO: WARNING
                continue
            retInputs.append(SimulationResultsData._checkInput(el))
        self._inputs = retInputs

    def addInput(self, IterableInput):
        self._inputs.append(SimulationResultsData._checkInput(IterableInput))


    def __getitem__(self, key):
        if type(key) is str:
            key = self._varname2index[key]
        if type(key) is int:
            if self._nOutputs is not None and key >= self._nOutputs:
                raise IndexError("%d is out of bound (%d)" % (key, self._nOutputs))
            index = key
        else:
            raise TypeError("%s (%s) is not a correct indexing value (type)" % ( key, type(key)))

        if self._cOutIndex is None or self._cOutIndex[index] == self._cIndex:
            next(self)

        if (self._cIndex - self._cOutIndex[index]) > 1:
            if __debug__:
                logger.debug("Output %d going from value %d to %d: losing value", self._cOutIndex[index], self._cIndex)

        self._cOutIndex[index] = self._cIndex

        return self._outs[index]

    @property
    def values(self):
        return [c["values"] for c in self._outs]
    
    @property
    def numberOutput(self):
        return self._actualNumberOutput
    
    def __iter__(self):
        return self                

    def __next__(self):        
        if self._cIndex is None:
            self._cIndex = 0

        # in cas of StopIteration, keep last value for others
        old_outs = self._outs
        self._outs = []
        
        for input_iterator in self._inputs:
            try:
                ret = next(input_iterator)
                if type(ret) is list:
                    self._outs.extend(ret)
                else:
                    self._outs.append(ret)
            except StopIteration:
                # Pass and don't add values:
                # Maybe we should add None? [None]*number ?
                pass

        self._actualNumberOutput = len(self._outs)
        if self._actualNumberOutput == 0:
            # No more data in any inputs
            # Restore last outs
            self._outs = old_outs
            raise StopIteration()
        
        if self._nOutputs is not None:
            # Ok, hardwired number of outputs
            if self._actualNumberOutput > self._nOutputs:
                # Reduce
                self._outs = self._outs[:self._nOutputs]
            elif self._actualNumberOutput < self._nOutputs:
                # Grow
                self._outs = self._outs + [None]*(self._nOutputs - self._actualNumberOutput)
            self._actualNumberOutput = self._nOutputs

        # Reduce/Grow index of outputs iterator
        if self._cOutIndex is None:
            self._cOutIndex = [self._cIndex] * self._actualNumberOutput
        else:
            if len(self._cOutIndex) > self._actualNumberOutput:
                self._cOutIndex = self._cOutIndex[:self._actualNumberOutput]
            else:
                self._cOutIndex = self._cOutIndex + [self._cIndex] * (self._actualNumberOutput - len(self._cOutIndex))

        # We got a new value
        self._cIndex += 1

        return self._outs


class ProxySRD(SimulationResultsData):
    def __init__(self, *args, obj, uuid=None, configuration=None, **kwargs):
        super().__init__(*args, inputs=[], nOutputs=1, uuid=uuid, configuration=configuration, **kwargs)
        self.__obj = obj
        
    def __getattr__(self, name):
        return getattr(self.__obj, name)

    def __iter__(self):
        return iter(self.__obj)

    def __next__(self):
        return next(self.__obj)
    
    def __getitem__(self, key):
        return self.__obj[key]
    
    def cost(self):
        return self.__obj.cost()


class BufferedFilter(SimulationResultsData):
    def __init__(self, *args, inputs=None, nOutputs=None, uuid=None, configuration=None, **kwargs):
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)
        self._accessed = {}
        self._outs = {}

    def __getitem__(self, key):
        if type(key) is str:
            key = self._varname2index[key]
        if type(key) is int:
            if self._nOutputs is not None and key >= self._nOutputs:
                raise IndexError("%d is out of bound (%d)" % (key, self._nOutputs))
            index = key
        else:
            raise TypeError("%s (%s) is not a correct indexing value (type)" % ( key, type(key)))

        if self._cOutIndex is None or self._cOutIndex[index] == self._cIndex:
            next(self)

        ret = self._outs[self._cOutIndex[index]][index]

        # Remove buffered value?
        self._accessed[self._cOutIndex[index]] += 1
        if self._accessed[self._cOutIndex[index]] >= len(self._outs[self._cOutIndex[index]]):
            # Every iterator accessed this value
            # We could delete it
            del self._outs[self._cOutIndex[index]]
            del self._accessed[self._cOutIndex[index]]
            
        self._cOutIndex[index] += 1

        return ret

    @property
    def numberOutput(self):
        return self._actualNumberOutput

    def __next__(self):        
        if self._cIndex is None:
            self._cIndex = 0

        outs = []
        
        for input_iterator in self._inputs:
            try:
                ret = next(input_iterator)
                if type(ret) is list:
                    outs.extend(ret)
                else:
                    outs.append(ret)
            except StopIteration:
                # Pass and don't add values:
                # Maybe we should add None? [None]*number ?
                pass

        self._actualNumberOutput = len(outs)
        if self._actualNumberOutput == 0:
            # No more data in any inputs
            raise StopIteration()
        
        if self._nOutputs is not None:
            # Ok, hardwired number of outputs
            if self._actualNumberOutput > self._nOutputs:
                # Reduce
                outs = outs[:self._nOutputs]
            elif self._actualNumberOutput < self._nOutputs:
                # Grow
                outs = outs + [None]*(self._nOutputs - self._actualNumberOutput)
            self._actualNumberOutput = self._nOutputs

        # Reduce/Grow index of outputs iterator
        if self._cOutIndex is None:
            self._cOutIndex = [self._cIndex] * self._actualNumberOutput
        else:
            if len(self._cOutIndex) < self._actualNumberOutput:
                self._cOutIndex = self._cOutIndex + [self._cIndex] * (self._actualNumberOutput - len(self._cOutIndex))

        # Save the new value
        self._outs[self._cIndex] = outs
        self._accessed[self._cIndex] = 0
        
        # We got a new value
        self._cIndex += 1

        return outs

    def dropCache(self, index):
        try:
            del self._outs[index]
        except IndexError:
            pass

# Linearise iterable
class LineriseFilter(SimulationResultsData):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
        'uuid': [str],
        'steps': [int],
    }

    def __init__(self, *args, inputs=None, nOutputs=None, funCombineVar=[], uuid=None, steps=1, configuration=None, **kwargs):
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)
        self._steps = steps
        self._funCombineVar = funCombineVar

    def __next__(self):
        outs = []
        try:
            if self._steps is None:
                while True:
                    outs.append(super().__next__())
            else:
                for it in range(self._steps):
                    outs.append(super().__next__())
        except StopIteration:
            pass
        if len(outs) == 0:
            raise StopIteration()

        self._outs = LineriseFilter._combine(outs, self._funCombineVar)
        return self._outs

    @staticmethod
    def _combine(outs, functions):
        if len(outs) == 0:
            return []

        ret = outs.pop(0)
        if any([type(x) is not dict for x in ret]):
            raise TypeError("Output should be variable, aka dict")
        for val in outs:
            LineriseFilter._combineOut(ret, val, functions)

        return ret
    
    @staticmethod
    def _combineOut(ret, val, functions):
        for index in range(max(len(ret), len(val))):    
            try:
                valOut = val[index]
            except IndexError:
                # no more to combien
                return
            try:
                output = ret[index]
            except IndexError:
                #ret is too smal, append last item
                ret.extend(val[index:len(val)])
                return

            if type(functions) is list:
                
                try:
                    comb = functions[index]
                except IndexError:
                    comb = LineriseFilter._dCombineVar
            else:
                comb = functions
            ret[index] = comb(output, valOut)

    @staticmethod
    def _dCombineVar(var1, var2):
        # should be a dict
        if type(var2) is not dict:
            raise TypeError("Output should be variable, aka dict")
        values = var2["values"]
    
        if type(values) is dict:
            # Geocode inside
            var1["values"] = LineriseFilter._combineGeocode(var1["values"], values)
        else:
            if type(var1["values"]) is not list:
                var1["values"] = [var1["values"]]
            if type(values) is list:
                var1["values"].extend(values)
            else:
                var1["values"].append(values)

        return var1
    
    @staticmethod
    def _combineGeocode(ret, val):
        return { k: LineriseFilter._combineValue(ret.get(k, []), val.get(k, [])) for k in set(ret) | set (val)}

    @staticmethod
    def _combineValue(val1, val2):
        if type(val1) is not list:
            val1 = [val1]
        if type(val2) is list:
            val1.extend(val2)
        else:
            val1.append(val2)

        return val1

    @staticmethod
    def _combineTimelyVariable(d1, d2):
        # Combine variable when iter on time (should be contigu after all combine
        ret = LineriseFilter._dCombineVar(d1, d2)
        ret["begin"] = min(d1["begin"], d2["begin"])
        ret["end"] = max(d1["end"],d2["end"])
        return ret

class MetaFilter(SimulationResultsData):
    CONFIG = {
        'inputs': [list],
        'nOutputs': [int],
        'uuid': [str],
        'elements': [dict],
        'links': [dict],
        'keepChildUUID': [bool], 
    }
    def __init__(self, *args, inputs=None, nOutputs=None, confElements = {}, links ={}, uuid = None, keepChildUUID=True, configuration=None, **kwargs):
        self._rInputs = inputs
        self._confElements = confElements
        self._links = links
        # TODO: use it
        self._keepChildUUID = keepChildUUID
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)
        
        self._elements = {}
        self._createGraph()
        self._instElements()

    def _createGraph(self):
        graph = { k: set([t[0] for t in v]) for k, v in self._links.items()}
        self._topo = list(toposort(graph))
        self._revLinks = self._revertLinks()

        # check that every node is connected to an input execpt _in node 
        for n, t in self._rLinks.items():
            if len(t) == 0 and not n.startswith('_in'):
                if __debug__:
                    logger.warning("Node %s is not connected to anyone.", n)

    def _revertLinks(self):
        self._revLinks = {}
        for n, v in self._links.items():
            for t in v:
                s = self._revLinks.get(t[0], set())
                s.add(n)
                self._revLinks[t[0]] = s

    # Instantiate elements in topo order
    def _instElements(self):
        for meta in self._topo:
            for node in meta:
                if node.startswith('_in'):
                    continue
                self._instElement(node)

    def _instElement(self, node):
        inputs = [self._buildInput(inputNode) for inputNode in self._links[node]]
        if node == "_out":
            self._inputs = inputs
        else:
            classNode = self._confElements[node]["class"]
            classInst = classNode(inputs=inputs, **self._confElements[node]["config"])
            self._elements[node] = classInst

    def _buildInput(self, inNode):
        nodeID = inNode[0]
        listInputIndex = inNode[1]
        bufferize = False
        if len(inNode) > 2:
            bufferize = inNode[2]

        # Specific node _in
        if nodeID.startswith('_in') and nodeID not in self._elements:
            index = nodeID.split(':')
            if len(index) > 1:
                node = self._rInputs[int(index[1])]
            else:
                # regroup inputs in 1 big node
                node = SimulationResultsData(inputs=self._rInputs)
            self._elements[nodeID] = node
        else:
            #topo order : should be instantiate
            node = self._elements[nodeID]

        if listInputIndex is None:
            if bufferize:
                return BufferedFilter([node])
            else:
                return node

        # Specific output
        if bufferize:
            return BufferedSpecificOutputsIterable(node, listInputIndex)
        else:
            return SpecificOutputsIterable(node, listInputIndex)
        

class SplitFilter(SimulationResultsData):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
        'uuid': [str],
    }

    def __init__(self, *args, inputs=None, nOutputs=None, funMetaDataVar=None, uuid=None, configuration=None, **kwargs):
        self._funMetaDataVar = funMetaDataVar
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)

    def __next__(self):
        outs = super().__next__()
        self._outs = []
        for out in outs:
            self._outs.extend(self._split(out))
        return self._outs

    def _split(self, out):
        raise NotImplemented("split method not implemented in base class")


class SplitListFilter(SplitFilter):
    def _split(self, out):
        if type(out["values"]) is not list:
            return [out]
        ret = []
        for ind in range(len(out["values"])):
            value = out["values"][ind]
            if self._funMetaDataVar is None:
                newVar = out.copy()
            else:
                newVar = self._funMetaDataVar(index, value, out, parentObject=self)
            newVar["values"] = value
            ret.append(newVar)
        return ret


class SplitDictFilter(SplitFilter):
    def __init__(self, *args, inputs=None, nOutputs=None, funMetaDataVar=None, funSortKey=None, geo=None, uuid=None, configuration=None, **kwargs):
        self._funSortKey = funSortKey
        self._geo = geo
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, funMetaDataVar=funMetaDataVar, uuid=uuid, configuration=configuration, **kwargs)

    def _split(self, out):
        if type(out["values"]) is not dict:
            return [out]
        ret = []
        if self._funSortKey is None:
            keys = out["values"].keys()
        else:
            keys = self._funSortKey(out["values"].keys())
        for ind, k in enumerate(keys):
            v = out["values"][k]
            if self._funMetaDataVar is None:
                newVar = out.copy()
                newVar['dictkey'] = k
            else:
                newVar = self._funMetaDataVar(k, v, ind, keys, out, parentObject=self)
            newVar["values"] = v
            ret.append(newVar)
        return ret


class CombineFilter(SimulationResultsData):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
        'uuid': [str],
    }

    def __init__(self, *args, inputs=None, nOutputs=None, funMetaDataVar=None, geo=None, uuid=None, configuration=None, **kwargs):
        self._funMetaDataVar = funMetaDataVar
        self._geo = geo
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)

    def __next__(self):
        outs = super().__next__()

        if len(outs) == 0:
            # should be > 0 : raise stopiteration in case not raise inside super
            raise StopIteration()
        
        if self._funMetaDataVar is None:
            ret = outs[0].copy()
            del ret["values"]
        else:
            ret = self._funMetaDataVar(outs, parentObject=self)

        ret["values"] = self._combine(outs)
        self._outs = [ret]
        return self._outs

    def _combine(self, out):
        raise NotImplemented("combine method not implemented in base class")

class CombineListFilter(CombineFilter):
    def _combine(self, outs):
        return [out["values"] for out in outs]

class CombineDictFilter(CombineFilter):
    def __init__(self, *args, inputs=None, nOutputs=None, funMetaDataVar=None, funCreateKey=None, uuid=None, configuration=None, **kwargs):
        self._funCreateKey = CombineDictFilter._defaultCreateKey if funCreateKey is None else funCreateKey
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, funMetaDataVar=funMetaDataVar, uuid=uuid, configuration=configuration, **kwargs)

    def _combine(self, outs):
        keys = self._funCreateKey(outs)
        if len(keys) != len(outs):
            raise ValueError("number of key(%d) should be the same as outputs(%d)" % (len(keys), len(outs)))
        return {keys[ind]: outs[ind]["values"] for ind in range(len(outs))}
    
    @staticmethod
    def _defaultCreateKey(outs):
        return list(range(len(outs)))
    



class IterableFilter(SimulationResultsData):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
        'uuid': [str],
    }

    def __init__(self, *args, inputs=None, nOutputs=None, funMetaDataVar=None, funIterableFromOuts=None, uuid=None, configuration=None, **kwargs):
        self._funMetaDataVar = IterableFilter._defaultMetaData if funMetaDataVar is None else funMetaDataVar
        self._funIterableFromOuts = IterableFilter._defaultIter if funIterableFromOuts is None else funIterableFromOuts
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)
        self._cIndex = -1
        self._cIterator = None
        self._cOuts = None
        
    def __next__(self):
        if self._cIterator is None:
            self._cOuts = super().__next__()
            self._cInsideIndex = [0]*len(self._cOuts)
            self._cIndex += 1
            self._cIterator = [self._funIterableFromOuts(out["values"]) for out in self._cOuts]

        self._outs = []
        for ind in range(len(self._cIterator)):
            ret = self._funMetaDataVar(self._cInsideIndex[ind], self._cIndex, ind, self._cOuts[ind], parentObject=self)
            try:
                val = self._iterablize(self._cIterator[ind], ind, ret)
            except StopIteration:
                continue
            ret["values"] = val
            self._outs.append(ret)

        if len(self._outs) == 0:
            self._cIterator = None
            self._outs = self.__next__()
        return self._outs

    def _iterablize(self, iterable, ind, ret):
        raise NotImplemented("iterablize method not implemented in base class")

    @staticmethod
    def _defaultIter(iterableEl):
        return iter(iterableEl)

    @staticmethod
    def _defaultMetaData(inInd, ind, outNum, out, parentObject=None):
        ret = out.copy()
        del ret["values"]
        return ret

class IterableListFilter(IterableFilter):
    def _iterablize(self, iterable, ind, ret):
        return next(iterable)
        

class IterableDictFilter(IterableFilter):
    def __init__(self, *args, inputs=None, nOutputs=None, funMetaDataVar=None, funIterableFromOuts=None, funAlterVar=None, uuid=None, configuration=None, **kwargs):
        self._funAlterVar = funAlterVar
        if funIterableFromOuts is None:
            funIterableFromOuts = IterableDictFilter._defaultDictIter
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, funMetaDataVar=funMetaDataVar, funIterableFromOuts=funIterableFromOuts, uuid=uuid, configuration=configuration, **kwargs)

    def _iterablize(self, iterable, ind, ret):
        key, val = next(iterable)
        if self._funAlterVar is not None:
            self._funAlterVar(key, val, ret)

        return val
    
    def _defaultDictIter(iterableEl):
        return iter(sorted(iterableEl.items()))

class AgregateFilter(SimulationResultsData):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
        'uuid': [str],
    }

    def __init__(self, *args, inputs=None, nOutputs=None, funMetaDataVar=None, funSlicing=None, funAgregate=None, precisionName=None, uuid=None, configuration=None, **kwargs):
        self._precisionName = precisionName
        self._funSlicing = funSlicing
        self._funAgregate = funAgregate
        self._funMetaDataVar = funMetaDataVar
        
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)
        
    def __next__(self):
        def sliceF(ind, val, out):
            if type(val) is dict:
                return { k: sliceF(ind, v, out) for k, v in val.items()}
            elif type(val) is list:
                return [ val[sl] for sl in self._funSlicing(ind, val, out)]
            else:
                return val
            
        outs = super().__next__()
        for ind in range(len(outs)):
            val = outs[ind]["values"]
            if self._funMetaDataVar is not None:
                self._funMetaDataVar(outs[ind], parentObject=self)
            if self._funSlicing is not None:
                val = sliceF(ind, val, outs[ind])
            if self._funAgregate is not None:
                val = self._funAgregate(ind, val, outs[ind])
            outs[ind]["values"] = val
            if self._precisionName is not None:
                outs[ind]['precision']=self._precisionName

        return outs


class RenameFilter(SimulationResultsData):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
    }

    def __init__(self, *args, inputs=None, nOutputs=None, funRenameVar=None, uuid=None, configuration=None, **kwargs):
        self._funRenameVar = funRenameVar
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)

    def __next__(self):
        outs = super().__next__()
        self._outs = []
        for ind, out in enumerate(outs):
            self._outs.append(self._funRenameVar(out, ind, outs, parentObject=self))
        return self._outs

class FilterStaticFun(SimulationResultsData):
    CONFIG = {
        'nOutputs': [int],
        'inputs': [list],
    }

    def __init__(self, *args, inputs=None, nOutputs=None, funOut=None, funOuts=None, funOutsMeta=None, uuid=None, configuration=None, **kwargs):
        self._funOut = funOut
        self._funOuts = funOuts
        self._funOutsMeta = funOutsMeta
        super().__init__(*args, inputs=inputs, nOutputs=nOutputs, uuid=uuid, configuration=configuration, **kwargs)

    def __next__(self):
        outs = super().__next__()
        if self._funOuts is not None:
            outs = self._funOuts(outs, parentObject=self)
        if self._funOut is None:
            self._outs = outs
        else:
            self._outs = []
            for ind, out in enumerate(outs):
                self._outs.append(self._funOut(out, ind, outs, parentObject=self))

        return self._outs




#TODO : FunctionFilter

"""
class FilterFunParam(object):
    MAX_RET_VAR_NUM = 20
    def __init__(self, function, filterParam=None):
        self._filter = filterParam
        self._ast = asteval.Interpreter()
        self._function = self._sanetize(function)
        self._restrict()
        self._current = None
        self._params = None
        
    def _restrict(self):
        # For now, consider all asteval function as safe
        # To delete function :
        # self._ast.symtable.pop('removedfunction')
        pass

    def _sanetize(self, function):
        # For now use the user function
        # confidence in asteval
        return function

    def __next__(self):
        
        if self._current is not None and len(self._current) > 0:
            try:
                return next(self._current)
            except StopIteration:
                # OK, current is empty, try the rest
                pass

        all_param = None
        if self._filter is None and self._current is None:
            # No other filter, get param from setted params
            all_params = self._params
        else:
            # Get next parameters from  previous filter
            all_params = next(self._filter)

        # Set variable inside AST
        xs = all_params["x"]
        variables = []
        if type(xs) is not list:
            variables = [xs]
        else:
            variables = list(xs)
            
        for varindex in range(len(variables)):
            self._ast.symtable['_%d' % (varindex)] = list(xs[varindex].value)
            
        y = all_params.get("y", None)
        if y is not None:
            self._ast.symtable["_y"] = list(y.value)
        # Execute AST
        try:
            ret = self._ast.eval(self._function)
            if y is not None:
                # We have process Y, get result on Y via __y
                y = self._ast.symtable.get("__y", None)
                if y is not None:
                    all_params["y"].value = y
            # Get value from ret?
            if type(ret) is list and len(ret) > 0:
                self._current = ParamVariables(ret, all_params)
            else:
                self._current = ParamVariables([val for (var, val) in self._ast.symtable.items()], all_params)
        except SyntaxError as e, NameError as e:
            if __debug__:
                logger.error(e)
        return next(self)

    def __iter__(self):
        return self
    
    def __call__(self, params):
        
        # No Y because we sum all data

        if len(xs) == 1:
            if __debug__:
                logger.warning("Sum data for chart but just one X")
        # Put data Xs in form of list(dict())
        
        data = [{'value': x.sumvalue, 'category': x.field} for x in xs]
        params["dataProvider"] = data
        return params


class ParamVariables(object):
    def __init__(self,listVar, params_org):
        self._orgParams = params_org
        length = len(params_org["x"])
        
        if type(listVar) is not list:
            # One var, One value : Should have at min 1 X
            self._current = [[ParamVariable(listVar, params_org["x"][0])]]
        else:
            try:
                if type(listVar[0]) is list:
                    #Multiple variable, multiple values
                    # Multiple split?
                    try:
                        if type(listVar[0][0]) is not list:
                            # Multiple variable, multiple values, one splits
                            # or Multiple splits, multiple variables, dict of var
                            if type(listVar[0][0]) is dict:
                                # Multiple splits, multiple variables, dict of var
                                self._current = [ [ ParamVariable(var[ind], params_org["x"][ind] if ind < length else params_org["x"][0]) for var in split] for split in listVar]
                            else:
                                # Multiple variable, multiple values, one splits
                                self._current = [[ParamVariable(var, params_org["x"][0]) for var in listVar]
                        else:
                            # Multiple splits, multiple variables, list of value
                            self._current = [ [ ParamVariable(var, params_org["x"][0]) for var in split] for split in listVar]
                        
                    except IndexError:
                        # No value in first variable!
                        raise SyntaxError("No value in first variable in current filter")
                else:
                   #One variable, multiple value
            except IndexError:
                # No variables at all!
                raise SyntaxError("Not variable in current filter")

"""             


SRDConfig.addAlias("WS.Utils.SpecificOutputsIterable", "wattstrat.simulation.SimulationResultsData.SpecificOutputsIterable", (), {})
SRDConfig.addAlias("WS.Utils.BufferedSpecificOutputsIterable", "wattstrat.simulation.SimulationResultsData.BufferedSpecificOutputsIterable", (), {})
SRDConfig.addAlias("WS.SimulationResultsData", "wattstrat.simulation.SimulationResultsData.SimulationResultsData", (), {})
SRDConfig.addAlias("WS.Utils.ProxySRD", "wattstrat.simulation.SimulationResultsData.ProxySRD", (), {})
SRDConfig.addAlias("WS.Utils.BufferedFilter", "wattstrat.simulation.SimulationResultsData.BufferedFilter", (), {})
SRDConfig.addAlias("WS.Utils.LineriseFilter", "wattstrat.simulation.SimulationResultsData.LineriseFilter", (), {})
SRDConfig.addAlias("WS.MetaFilter", "wattstrat.simulation.SimulationResultsData.MetaFilter", (), {})
SRDConfig.addAlias("WS.SplitFilter", "wattstrat.simulation.SimulationResultsData.SplitFilter", (), {})
SRDConfig.addAlias("WS.SplitFilter.List", "wattstrat.simulation.SimulationResultsData.SplitListFilter", (), {})
SRDConfig.addAlias("WS.SplitFilter.Dict", "wattstrat.simulation.SimulationResultsData.SplitDictFilter", (), {})
SRDConfig.addAlias("WS.CombineFilter", "wattstrat.simulation.SimulationResultsData.CombineFilter", (), {})
SRDConfig.addAlias("WS.CombineFilter.List", "wattstrat.simulation.SimulationResultsData.CombineListFilter", (), {})
SRDConfig.addAlias("WS.CombineFilter.Dict", "wattstrat.simulation.SimulationResultsData.CombineDictFilter", (), {})
SRDConfig.addAlias("WS.IterableFilter", "wattstrat.simulation.SimulationResultsData.IterableFilter", (), {})
SRDConfig.addAlias("WS.IterableFilter.List", "wattstrat.simulation.SimulationResultsData.IterableListFilter", (), {})
SRDConfig.addAlias("WS.IterableFilter.Dict", "wattstrat.simulation.SimulationResultsData.IterableDictFilter", (), {})
SRDConfig.addAlias("WS.AgregateFilter", "wattstrat.simulation.SimulationResultsData.AgregateFilter", (), {})
SRDConfig.addAlias("WS.Utils.RenameFilter", "wattstrat.simulation.SimulationResultsData.RenameFilter", (), {})
#SRDConfig.addAlias("WS.FilterFunParam", "wattstrat.simulation.SimulationResultsData.FilterFunParam", (), {})
#SRDConfig.addAlias("WS.ParamVariables", "wattstrat.simulation.SimulationResultsData.ParamVariables", (), {})
