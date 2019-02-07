class AMCharts {
    constructor(chartId, chartData){
	this._theme = chartData["theme"];
	this._values = chartData["values"];
	this._titles = chartData["titles"];
	this._divid = chartData["divid"];
	this._graphId = chartId;
    }

    get optExports() {
	return {
	    "enabled": true,
	    "menu": [ {
		"class": "export-main",
		"menu": [ {
		    "label": "Download as ...",
		    "menu": [ "PNG", "JPG", "SVG", AmCharts.exportPDF ]
		}, {
		    "label": "Annotate",
		    "action": "draw",
		    "menu": [ {
			"class": "export-drawing",
			"menu": [
			    "UNDO",
			    "REDO", {
				"label": "Save as ...",
				"menu": [ "PNG", "JPG", "SVG", AmCharts.exportPDF ]
			    },
			    AmCharts.exportPrint, "CANCEL" ]
		    } ]
		},
			  AmCharts.exportPrint ]
	    } ]
	};
    }

    get values(){
	return this._values;
    }

    get titles() {
	var titles = [];
	for(var title in self._titles){
	    titles.push({
		text: title["text"],
		"size": title["style"]["fontSize"],
		"alpha": title["style"]["alpha"],
		"bold": title["style"]["bold"],
		"color": title["style"]["color"],
		"tabIndex": title["index"],
	    });
	}
	return titles;
    }

    get Conf() {
	var conf = {
	    "theme": this._theme,
	    "marginTop": 10,
	    "marginBottom": 50,
	    "addClassNames": true,
	    "titles": this.titles,
	    "dataProvider": this.values,
	    "mouseWheelZoomEnabled": false,
	    "legend": {
//		"divId": "legenddiv-" + this._graphId,
		"useGraphSettings": true
	    },
	    "useScientificNotation": true,
	    "precision" : 3,
            "usePrefixes" : true,
	    "export" : this.optExports,
    	}
	return conf;
    }

    _initConf(){
    }

    makeChart(){
	this._initConf();
	var conf = this.Conf;
	var AMChart = AmCharts.makeChart(this._divid, conf);
	this.chart = AMChart;
	return AMChart;
    }
}

class SerialChart extends AMCharts {
    constructor(chartId, chartData) {
	super(chartId, chartData);
	this._ParamAbscisse = chartData["x"];
	this._ParamOrdonnees = chartData["y"];
	this._axis = chartData["axis"];
	this._Stacked = false;
	this._ordonnees = []
	this._abscisse = {}
    }

    get axis() {
	if(this._axis.length == 0){
	    return [this._defaultAxis]
	}
	for(var ind=0; ind < this._axis.length; ind++) {
	    var axe = this._axis[ind];
	    if(this._Stacked) {
		axe["stackType"] = "regular";
	    }
	}
	return this._axis;
    }
    get _defaultAxis() {
	for(var ordonnee in this._ordonnees){
	    ordonnee["valueAxis"] = "default";
	}
	return [{
	    "id" : "default",
	    "baseValue" : 0,
	    "useScientificNotation": true,
	    "unit" : this._ordonnees[0]["unit"],
	    "precision" : 3,
            "usePrefixes" : true,
	}]
    }

    _createOrdonnees(){
	this._ordonnee = [];
	for(var ind=0; ind < this._ParamOrdonnees.length; ind++){
	    var ordonnee = this._ParamOrdonnees[ind]
	    var ord = {
		"id": ordonnee["field"],
		"valueField": ordonnee["field"],
		"title": ordonnee["label"] + " (" + ordonnee["unit"] + ") :",
		"balloonText": ordonnee["shortLabel"] + " : <strong>[[value]]</strong> " + ordonnee["unit"],
	    }
	    if(ordonnee.hasOwnProperty(style)){
		for(var style in ordonnee["style"]){
		    ord[style] = ordonnee["style"][style];
		}
	    }
	    if(ordonnee.hasOwnProperty("axisID")){
		ord["valueAxis"] = ordonnee["axisID"];
	    }
	    this._ordonnees.push(ord);
	}
    }

    _createAbscisse() {
	this._abscisse["categoryField"] = this._ParamAbscisse["field"];
	if(this._ParamAbscisse["type"] == "date"){
	    this._abscisse["dataDateFormat"] = this._ParamAbscisse["format"];
	    this._abscisse["categoryAxis"] = {
		"parseDates": true,
		"minPeriod": this._ParamAbscisse["minPeriod"],
		"minorGridEnabled": true
	    };
	}
    }

    get scrollbar(){
	return {
		"graph": this._ordonnees[0]["field"],
		"autoGridCount": true,
		"oppositeAxis": false,
		"scrollbarHeight": 10,
		"offset": 30,
		"backgroundAlpha": 0,
		"selectedBackgroundAlpha": 0.1,
		"selectedBackgroundColor": "#888888",
		"graphFillAlpha": 0,
		"graphLineAlpha": 0.5,
		"selectedGraphFillAlpha": 0,
		"selectedGraphLineAlpha": 1,
		"color": "#AAAAAA"
	    }
    }

    get cursor(){
	var cursor = {
	    "cursorPosition": "mouse",
	    "pan": true,
	}
	if(this._ParamAbscisse["type"] == 'date'){
	    cursor["categoryBalloonDateFormat"] = this._ParamAbscisse["formatBalloon"];
	}
	return cursor;
    }

    get Conf() {
	var conf = super.Conf
	var confAdded = {
	    "type": "serial",
	    "chartScrollbar" : this.scrollbar,
	    "valueAxes": this.axis,
	    "valueScrollbar": {
		"oppositeAxis": false,
		"offset": 80,
		"scrollbarHeight": 10
	    },
	    "chartCursor": this.cursor,
    	}
	$.extend(conf, confAdded);
	for(var confAbscisse in this._abscisse){
	    conf[confAbscisse] = this._abscisse[confAbscisse];
	}
	// After create axis
	conf["graphs"] = this._ordonnees
	
	return conf;
    }

    _initConf(){
	super._initConf();
	this._createAbscisse();
	this._createOrdonnees();
    }
}

class LineChart extends SerialChart {
    _createOrdonnees() {
	super._createOrdonnees();
	for(var ind = 0; ind < this._ordonnees.length; ind++){
	    var ord = this._ordonnees[ind];
	    $.extend(ord, {
		"bullet": "round",
		"bulletBorderAlpha": 1,
		"bulletColor": "#FFFFFF",
		"bulletSize": 5,
		"hideBulletsCount": 50,
		"lineThickness": 2,
		"useLineColorForBulletBorder": true,
		"type": "line",
	    });
	}	    
    }
}

class StackedLineChart extends LineChart {
    constructor(chartId, chartData){
	super(chartId, chartData);
	this._Stacked = true;
    }
    _createOrdonnees(){
	super._createOrdonnees();
	for(var ind = 0; ind < this._ordonnees.length; ind++){
	    var ord = this._ordonnees[ind];
	    $.extend(ord, {
		"fillAlphas": 0.6,
	    });
	}
    }
}

class BarChart extends SerialChart {
    _createOrdonnees(){
	super._createOrdonnees();
	for(var ind = 0; ind < this._ordonnees.length; ind++){
	    var ord = this._ordonnees[ind];
	    $.extend(ord, {
		"fillAlphas": 0.8,
		"lineAlpha": 0.2,
		"type": "column",
	    });
	}
    }
}

class StackedBarChart extends BarChart {
    constructor(chartId, chartData){
	super(chartId, chartData);
	this._Stacked = true;
    }
}

class HistoFreqChart extends BarChart {
    get Conf() {
	var conf = super.Conf
	conf["chartScrollbar"] = false;
	return conf;
    }
    _createAbscisse() {
	super._createAbscisse()
	this._abscisse["categoryAxis"] = {"labelRotation" : 45};
    }


}

class PieChart extends AMCharts {
    constructor(chartId, chartData){
	super(chartId, chartData);
	this._titleField = chartData["titleField"];
	this._valueField = chartData["valueField"];

	this._changeTitle(chartData);
    }

    _changeTitle() {
	for(var ind = 0; ind < this._values.length; ind++){
	    this._values[ind][this._titleField] += " (" + this._values[ind]["unit"]+ ") :";
	}
    }

    get _filters() {
	var filters = [
	    {
		"id": "shadow",
		"width": "200%",
		"height": "200%",
		"feOffset": {
		    "result": "offOut",
		    "in": "SourceAlpha",
		    "dx": 0,
		    "dy": 0
		},
		"feGaussianBlur": {
		    "result": "blurOut",
		    "in": "offOut",
		    "stdDeviation": 5
		},
		"feBlend": {
		    "in": "SourceGraphic",
		    "in2": "blurOut",
		    "mode": "normal"
		}
	    }
	]
	return filters;
    }

    get _defs() {
	var defs = {
	    "filter": this._filters,
	}

	return defs;
    }

    get Conf(){
	var conf = super.Conf
	var confAdded = {
	    "type": "pie",
	    "startDuration": 0,
	    "innerRadius": "30%",
	    "defs": this._defs,
	    "labelsEnabled": false,
            "valueField": this._valueField,
            "titleField": this._titleField,
        }
	$.extend(conf, confAdded);
	conf["legend"]["useGraphSettings"]=false;
	return conf;
    }
}
