import datetime
from copy import deepcopy

from .SimulationResultsData import SimulationResultsData
from . import SimulationResultsDataConfig as SRDConfig
if __debug__:
    import logging
    logger = logging.getLogger(__name__)


SRDConfig.addAlias("WS.Variable.FromIterator", "wattstrat.simulation.SimulationResultsVariableStatic.VariableFromIterator", (), {})
# Create variable from an iterator.
# For all geocode, use the same value of the iterator
class VariableFromIterator(SimulationResultsData):
    def __init__(self, *args, simulation, varname, label, geocodes, begin, end, iterator, shortLabel=None, field=None, deepcopy=False, uuid=None, configuration=None, **kwargs):
        self._simulation = simulation
        self._varname = varname
        self._label = label
        self._geocodes = geocodes
        if shortLabel is None:
            self._shortLabel = label
        else:
            self._shortLabels = shortLabel
        if field is None:
            self._field = varname
        else:
            self._field = field

        self._deepcopy = deepcopy
        self._iterator = iterator

        self._ybegin = begin
        self._yend = end
        self._year = begin.year
        
        super().__init__(*args, inputs=[], nOutputs=1, uuid=uuid, configuration=configuration, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        val = next(self._iterator)
        self._outs = [{'simulation': self._simulation,
                'varname': self._varname,
                'label': self._label,
                'shortLabel': self._shortLabel,
                'field': self._field,
                'year': self._year,
                'begin': self._ybegin,
                'end': self._yend,
                'values': { geo: deepcopy(val) if self._deepcopy else val for geo in self._geocodes},
                'precision': 'h',
        }]

        return self._outs
