import json
from path import Path

if __debug__:
    import logging
    logger = logging.getLogger(__name__)

RES_DIR = Path(__file__).dirname()


class VarNames(object):
    ldatas = None
    vdatas = None

    def __init__(self, varnames=None):
        self._varnames = varnames

    @staticmethod
    def _load():
        if VarNames.ldatas is None:
            VarNames.load_data()

    @staticmethod
    def load_data():
        VarNames.ldatas = json.load(open(RES_DIR / 'result_tags.json', encoding='utf-8'))

        VarNames.vdatas = {v[0]: {'label': k, 'units': v[1], 'short': v[2], 'tags': v[3:]}
                           for k, v in VarNames.ldatas.items()}

    @property
    def ldata(self):
        return self.fromLabels(self._varnames)

    @property
    def vdata(self):
        return self.fromVarNames(self._varnames)

    @property
    def labels(self):
        VarNames._load()
        if type(self._varnames) is str:
            return VarNames.vdatas[self._varnames]['label']
        elif type(self._varnames) is list:
            return {k: VarNames.vdatas[k]['label'] for k in self._varnames}
        elif type(self._varnames) is dict:
            return {k: VarNames.vdatas[k]['label'] for k in self._varnames.keys()}

        return {k: VarNames.vdatas[k]['label'] for k in VarNames.vdatas.keys()}

    @property
    def varnames(self):
        VarNames._load()
        if type(self._varnames) is str:
            return VarNames.ldatas[self._varnames][0]
        elif type(self._varnames) is list:
            return {k: VarNames.ldatas[k][0] for k in self._varnames}
        elif type(self._varnames) is dict:
            return {k: VarNames.ldatas[k][0] for k in self._varnames.keys()}

        return {k: VarNames.ldatas[k][0] for k in VarNames.ldatas.keys()}

    @staticmethod
    def fromLabels(labels=None):
        VarNames._load()
        if labels is None:
            return VarNames.ldatas
        elif type(labels) is str:
            return VarNames.ldatas[labels]
        elif type(labels) is list:
            return {k: VarNames.ldatas[k] for k in labels}
        elif type(labels) is dict:
            return {k: VarNames.ldatas[k] for k in labels.keys()}
        return VarNames.ldatas.copy()

    @staticmethod
    def fromVarNames(varnames=None):
        VarNames._load()
        if varnames is None:
            return VarNames.vdatas
        elif type(varnames) is str:
            return VarNames.vdatas[varnames]
        elif type(varnames) is list:
            return {k: VarNames.vdatas[k] for k in varnames}
        elif type(varnames) is dict:
            return {k: VarNames.vdatas[k] for k in varnames.keys()}
        return VarNames.vdatas.copy()
