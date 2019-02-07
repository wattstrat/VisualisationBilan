import jinja2
from path import Path

from Utils.GeoJSON import GeoJSON

if __debug__:
    import logging
    logger = logging.getLogger(__name__)



class NoChart(Exception):
    pass


class TemplateCharts(object):
    def VarToTemplate(var):
        if type(var) is str:
            return '"%s"' % var
        elif type(var) is bool:
            return "true" if var else "false"
        elif type(var) in [float, int]:
            return var
        else:
            return str(var)

    ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(str(Path(__file__).dirname() / 'report' / 'template')))
    ENV.filters['repr'] = VarToTemplate


class Chart(object):
    AXIS_DEF = {
        'default': {
            'baseValue': 0,
            'useScientificNotation': True,
            'precision' : 3,
            'usePrefixes': True,
        }
    }

    @staticmethod
    def createAxis(data):
        axis = {}
        if 'y' in data:
            for ind, y in enumerate(data['y']):
                unit = y.get('unit', 'NaU')
                if unit not in axis:
                    axis[unit] = Chart.AXIS_DEF.get(unit, Chart.AXIS_DEF['default']).copy()
                    axis[unit]['id'] = "v%d" % (len(axis))
                    axis[unit]['unit'] = unit
                    axis[unit]['position'] = "left" if (len(axis)%2) else "right"
                data['y'][ind]['axisID'] = axis[unit]['id']
            return list(axis.values())
        return []

    def __init__(self, divid, number, data, templates=[]):
        self._divid = divid
        self._data = data
        self._templates = templates
        self._number = number
        
        self._html = None
        self._js = None
        
    @property
    def JS(self):
        if self._js is None:
            self._renderChart()
        return self._js

    @property
    def html(self):
        if self._html is None:
            self._renderChart()
        return self._html
    
    def _renderChart(self):
        template = None
        templateJS = None
        templateName = None
        for nameTemplate in self._templates:
            try:
                template = TemplateCharts.ENV.get_template('graph/' + nameTemplate + '.html')
                templateJS = TemplateCharts.ENV.get_template('graph/' + nameTemplate + '.js')
                templateName = nameTemplate
                break
            except TemplateNotFound as e:
                pass
        if template is None or templateJS is None:
            if __debug__:
                logger.error("template %s not found" % e.name)
            raise NoChart("template %s not found" % e.name)
        
        context = self._get_context()
        context['graphNumber'] = self._number
        context['templateName'] = templateName
        context['axis'] = self._createAxis()
        
        try:
            self._html = template.render(context)
            self._js = templateJS.render(context)
        except jinja2.TemplateError as e:
            raise
            raise NoChart("template render error")

    def _createAxis(self):
        return Chart.createAxis(self._data)
            
    def _get_context(self):
        return {
            'data': self._data,
            'divid': self._divid,
            'values': self._data['values']
        }
    
class MapChart(Chart):
    def __init__(self, divid, number, data, templates=[]):
        super().__init__(divid, number, data, templates)
        self._geojson = GeoJSON(list(data["values"].keys()))
        self._features = None
        
    def _constructGeoJSON(self):
        if self._features is None:
            self._features = self._geojson.jsonFeatures
    
    def _get_context(self):
        self._constructGeoJSON()
        ret = super()._get_context()
        ret["features"] = self._features
        return ret


class StackedLineChart(Chart):
    def _get_context(self):
        ret = super()._get_context()
        ret["Stacked"] = True
        return ret

class BarChart(Chart):
    def _get_context(self):
        ret = super()._get_context()
        ret["graphtype"]="bar"
        return ret

class StackedBarChart(BarChart):
    def _get_context(self):
        ret = super()._get_context()
        ret["Stacked"] = True
        return ret


class Charts(object):
    NB_CHARTS = 0
    def __init__(self, divid, data, templates=[], templateRendering=None):
        self._divid = divid
        self._data = data
        self._templates = templates
        self._charts = []
        self._tRendering = templateRendering

    @property
    def nbCharts(self):
        if self._tRendering is None:
            return Charts.NB_CHARTS
        else:
            return self._tRendering.nbCharts
        
    @nbCharts.setter
    def nbCharts(self, value):
        if self._tRendering is None:
            Charts.NB_CHARTS = value
        else:
            self._tRendering.nbCharts = value
    
    def createCharts(self, templates=None):
        ret = []
        if templates is None:
            templates = self._templates
            
        for data in self._data:
            for params in self._filter_data(data):
                try:
                    num = self.nbCharts
                    divid = self._createDivID(num)
                    chart = self._getChart(divid, num, params, params.get("template", templates))
                    self._charts.append(chart)
                    ret.append(chart.html)
                    if self._tRendering is not None:
                        self._tRendering.addGraph(divid, chart)
                    self.nbCharts = num + 1
                except NoChart:
                    pass
        return ret

    def _getChart(self, divid, number, data, templates=[]):
        return Chart(divid, number, data, templates=templates)

    @property
    def js(self):
        return [chart.js for chart in self._charts]

    @staticmethod
    def allJS():
        return [chart.js for chart in Charts.AllCharts.values()]
    
    def _filter_data(self, data):
        # data is a list of outputs
        return data

    def _createDivID(self, number):
        divid = self._divid if self._divid is not None else "chart"
        return "%s-%d" % (divid, number)
    

class MapCharts(Charts):
    def __init__(self, data, templates=None, templateRendering=None):
        if templates is None:
            templates = ["mapchart"]

        super().__init__("mapchart", data, templates, templateRendering)

    def _getChart(self, divid, number, data, templates=[]):
        return MapChart(divid, number, data, templates=templates)

    def _filter_data(self, data):
        # formatter return dict of leaflet map depending on variable. Split all.
        return [{ 'values': d['values'], 'min': d['min'], 'max': d['max'], 'varname': k} for out in data for k,d in out.items()]


class LineCharts(Charts):
    def __init__(self, data, templates=None, templateRendering=None):
        if templates is None:
            templates = ["linechart"]

        super().__init__("linechart", data, templates, templateRendering)

        
class StackedLineCharts(Charts):
    def __init__(self, data, templates=None, templateRendering=None):
        if templates is None:
            templates = ["linechart"]

        super().__init__("linechart", data, templates, templateRendering)

    def _getChart(self, divid, number, data, templates=[]):
        return StackedLineChart(divid, number, data, templates=templates)


class PieCharts(Charts):
    def __init__(self, data, templates=None, templateRendering=None):
        if templates is None:
            templates = ["piechart"]

        super().__init__("piechart", data, templates, templateRendering)
        
class BarCharts(Charts):
    def __init__(self, data, templates=None, templateRendering=None):
        if templates is None:
            templates = ["barchart"]

        super().__init__("barchart", data, templates, templateRendering)

    def _getChart(self, divid, number, data, templates=[]):
        return BarChart(divid, number, data, templates=templates)

        
class StackedBarCharts(Charts):
    def __init__(self, data, templates=None, templateRendering=None):
        if templates is None:
            templates = ["barchart"]

        super().__init__("barchart", data, templates, templateRendering)

    def _getChart(self, divid, number, data, templates=[]):
        return StackedBarChart(divid, number, data, templates=templates)
