from Global.Global import GlobalREFiltered
from copy import deepcopy
Alias = {}
Argument = {}
Filter = [
    'wattstrat\.simulation\.SimulationResults.*',
    'WS\..*',
]
Importer = GlobalREFiltered(alias=Alias, filters=Filter)

class AlreadyAliased(Exception):
    pass

class NoAlias(Exception):
    pass

class FilteredObject(Exception):
    pass

class DynamicLoader(object):
    CONFIG = {
        'uuid': [str],
        'configuration': [dict],
        }

    def __init__(self, *args, uuid=None, configuration=None, **kwargs):
        pass

    @classmethod
    def loadFromCellConfiguration(cls, *args, **kwargs):
        
        configSRD = kwargs["cell"]["attrs"].get("SRDConfig")
        pKwargs = {**kwargs, **configSRD}
        inputs = []
        for inp in kwargs["cell"]["inPorts"]:
            inpCell = kwargs["cellInputs"].get(inp, None)
            if inpCell is None:
                # TODO: print error?
                # Instanciation error
                continue
            if len(inpCell["cell"]["outPorts"]) != 1:
                # For now, add SpecificOutputBufferize if not the same length of output
                bufferedOutput = inpCell.get("bInst")
                if bufferedOutput is None:
                    bufferedOutput=BufferedSpecificOutputsIterable(inpCell["inst"], None)
                    inpCell["bInst"] = bufferedOutput
                # Specific output on the buffer
                inputs.append(SpecificOutputsIterable(bufferedOutput, [inpCell["cell"]["outPorts"].index(inpCell["port"])]))
            else:
                inputs.append(inpCell["inst"])
        if len(inputs)> 0:
            pKwargs["inputs"] = inputs
        
        return cls.fromConfig(pKwargs, *args)
    
    @classmethod
    def fromConfig(cls, config, *args):
        if config is None:
            raise EmptyConfig()


        if type(config) is str:
            dConfig = ast.literal_eval(config)
        elif type(config) is dict:
            dConfig = config
        else:
            raise TypeError("configuration parameter should be a string or a dict")

        for confVar, typeVar in cls.CONFIG.items():
            conf = dConfig.get(confVar)
            if conf is not None:
                if type(conf) not in typeVar:
                    raise TypeError("configuration parameter %s must be a %s not a %s" % ( confVar, typeVar, type(conf)))

        return cls(*args, **dConfig)

def addAlias(aliasName, className, args, kwargs):
    if aliasName in Alias:
        raise AlreadyAliased("%s is already aliased to %s" % (aliasName, Alias[aliasName]))

    Alias[aliasName] = className
    Argument[aliasName] = {'args': args, 'kwargs': kwargs}

def getSRD(SRD, *c_args, **c_kwargs):
    Arg = Argument.get(SRD)

    if Arg is None:
        raise NoAlias("No alias for %s" % (SRD))
    
    args = deepcopy(Arg["args"])
    kwargs = deepcopy(Arg["kwargs"])

    args = (*args, *c_args)
    kwargs = {**kwargs, **c_kwargs}

    return Importer.get_instance(SRD, *args, **kwargs)

def getSRDFromCell(SRD, *c_args, **c_kwargs):
    Arg = Argument.get(SRD)

    if Arg is None:
        raise NoAlias("No alias for %s" % (SRD))

    args = deepcopy(Arg["args"])
    kwargs = deepcopy(Arg["kwargs"])

    args = (*args, *c_args)
    kwargs = {**kwargs, **c_kwargs}

    classSRD = Importer.get_class(SRD)
    return classSRD.loadFromCellConfiguration(*args, **kwargs)

