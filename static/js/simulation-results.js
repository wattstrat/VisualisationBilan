var angular, moment, chroma, AmCharts, L, BatResultsOLMap;

var simulationResults = angular.module('simulationResults', ['ngMessages', 'ui.bootstrap', 'ng.django.urls', 'wattstrat'])
.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
})
.config(function (datepickerConfig) {
    datepickerConfig.showWeeks = false;
    datepickerConfig.startingDay = 1;
})
    .factory('shortid', function(){
	if(window.location.pathname == '/simulation/data/'){
	    return 'bilan2015';
	}
	else{
	    return window.location.pathname.split('/')[2];
	}
})
.factory('parametersUrl', function(djangoUrl, shortid){
    return djangoUrl.reverse('simulation:results:parameters',{
	shortid: shortid
    });
})
.factory('chartUrl', function(djangoUrl, shortid){
    return djangoUrl.reverse('simulation:results:chart',{
        shortid: shortid
    });
})
.factory('downloadResultURL', function(djangoUrl, shortid){
    return djangoUrl.reverse('simulation:results:download',{
        shortid: shortid,
	filetype: 'xlsx'
    });
})
.factory('userinfoUrl', function(djangoUrl){
    return djangoUrl.reverse('accounts:userinfo');
});

/**
 * PDF-specfic configuration
 */
AmCharts.exportPDF = {
    "format": "PDF",
    "content": [ "Saved from:", window.location.href, {
        "image": "reference",
        "fit": [ 523.28, 769.89 ] // fit image to A4
    } ]
};

/**
 * Print-specfic configuration
 */
AmCharts.exportPrint = {
    "format": "PRINT",
    "label": "Print"
};


proj4.defs("EPSG:2154","+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs");


/***********************/
/* OL Map Manager */
/***********************/


// formatage nb
// d3Format.format('.2s')(from).concat(activeTerritory.unit)



/************/
/* Services */
/************/

class FilteredGeocodes extends Geocodes {
    constructor ($http, djangoUrl, locale, shortid) {
	super($http, djangoUrl, locale)
	this._dataLocation = djangoUrl.reverse('simulation:simugeocodesfilter', {'shortid': shortid})
    }
    static factory($http, djangoUrl, locale, shortid){
	return new FilteredGeocodes($http, djangoUrl, locale, shortid);
    }
}
FilteredGeocodes.factory.$inject = ["$http", "djangoUrl", "locale", "shortid"];

wattstrat.service('filteredgeocodes', FilteredGeocodes.factory);

class GeocodesInfos extends Geocodes {
    constructor ($http, djangoUrl, locale, shortid) {
    super($http, djangoUrl, locale)
    this._dataLocation = djangoUrl.reverse('simulation:geocodesinfos', {'shortid': shortid})
    this.allGeo = this.match("");
    }
    static factory($http, djangoUrl, locale, shortid){
    return new GeocodesInfos($http, djangoUrl, locale, shortid);
    }
}
GeocodesInfos.factory.$inject = ["$http", "djangoUrl", "locale", "shortid"];

wattstrat.service('geocodesinfos', GeocodesInfos.factory);

class FilteredResultVariables extends ResultVariables {
    constructor ($http, djangoUrl, shortid) {
	super($http, djangoUrl)
	this._dataLocation = djangoUrl.reverse('simulation:simuresultvariablesfilter', {'shortid': shortid})
    }
    static factory($http, djangoUrl, shortid){
	return new FilteredResultVariables($http, djangoUrl, shortid);
    }
}

FilteredResultVariables.factory.$inject = ["$http", "djangoUrl", "shortid"];

wattstrat.service('filteredresultvariables', FilteredResultVariables.factory);

class AllFilteredResultVariables extends ResultVariables {
    constructor ($http, djangoUrl, shortid) {
	super($http, djangoUrl)
	this._dataLocation = djangoUrl.reverse('simulation:simuallresultvariablesfilter', {'shortid': shortid})
	// get all values at statup
	//this.allVars = [];
	// var self = this;
	// this.match("").then(function(data) {
	//     self.allVars = data;
	// });
	this.allVars = this.match("");
    }
    static factory($http, djangoUrl, shortid){
	return new AllFilteredResultVariables($http, djangoUrl, shortid);
    }
}

AllFilteredResultVariables.factory.$inject = ["$http", "djangoUrl", "shortid"];

wattstrat.service('allfilteredresultvariables', AllFilteredResultVariables.factory);

function SimulationParameters($http, messages, wsUtils, parametersUrl, results, datepickerConfig, filteredgeocodes){
    var simulationparameters = this;
    this.messages = messages;
    
    this.dataPromise = $http.get(parametersUrl)
        .success(function(data){
            simulationparameters.setParametersDefinition(data);
        })
        .error(function(){
            messages.show('error');
        });

    this.setParametersDefinition = function(data){
        results.startDate = data.start_date;
        results.endDate = data.end_date;
        for (idx=0; idx<results.graphs.length; idx++){
            results.graphs[idx].startDate = data.start_date
            results.graphs[idx].endDate = data.end_date
        }
        datepickerConfig.minDate = data.start_date
        datepickerConfig.maxDate = data.end_date
    };
}
simulationResults.service('simulationparameters', SimulationParameters);

simulationResults.service('results', function($http, $q, filteredgeocodes, filteredresultvariables, allfilteredresultvariables, geocodesinfos, locale, chartUrl, djangoUrl, shortid, messages, userinfo){
    var results = this;
    var wsAGeocodes = filteredgeocodes;
    this.allVars = [{'label': "Not Initialized"}]; 
    allfilteredresultvariables.allVars.then(function(data) {
        var mydict = {} ;
        for (var i = 0; i < data.length; i++) {
            var tempSplit = data[i]['label'].split("-")
            var myname = tempSplit[0].trim()
            if (myname != 'Bilan' & myname != 'Global' & tempSplit.length>2){
                data[i]['index_label'] = tempSplit.slice(2).join('-');
            } else {
                data[i]['index_label'] = data[i]['label'];
            };
            if (myname in mydict) {
                if (tempSplit[1].trim() in mydict[myname]){
                    mydict[myname][tempSplit[1].trim()].push(data[i]);
                }
                else {
                    mydict[myname][tempSplit[1].trim()] = [data[i]]
                }
            } else {
                mydict[myname] = {}
                mydict[myname][tempSplit[1].trim()] = [data[i]]
            };
        }

        results.allKeys = Object.keys(mydict).sort();
        results.allSubKeys = {}
        results.allVars = mydict
        for (i =0; i< results.allKeys.length; i++) {
            results.allSubKeys[results.allKeys[i]] = Object.keys(results.allVars[results.allKeys[i]]).sort()
        }
        
        for (i =0; i< results.allKeys.length; i++) {
            var mykeys = Object.keys(results.allVars[results.allKeys[i]])
            for (j =0; j< mykeys.length; j++){
                results.allVars[results.allKeys[i]][mykeys[j]].sort()
            }  
        }
    });
    geocodesinfos.allGeo.then(function(data) {
	results.allGeoInfos = _(data).map(function(value) {
	    if ('includes' in value){
		incl = value['includes'].map(function(incl) {
		    if(!incl.hasOwnProperty("labelinfo")){
			incl.labelinfo = incl.label;
		    }
		    return incl;
		});
		value.includes=incl;
	    }
	    else{
		if(!value.hasOwnProperty("labelinfo")){
		    value.labelinfo = value.label;
		}
		value.includes=[value]
	    }
	    return value;
	}).groupBy('order').mapValues(function(value){
	    return {'order': value[0]['order'], 'geocodes': _.sortBy(value, 'label')};
	}).sortBy('order').map(function(a) {return a['geocodes'];}).value();
    });
    
    this.selectedResult = null;
    this.parameters = {};

    this.viewableTerritories = [];

    this.noParametersSelected = function(){
	return this.variables.length === 0;
    };
    this.noGeocodesSelected  = function(){
	return this.geocodes.length === 0;
    };

    this.changeDownload = function(){
	var type = $("select[name=typeResult]").val();
	if(type == "download"){
	    $(".show-panel").hide();
	    $(".dwl-panel").show();
	}
	else{
	    $(".dwl-panel").hide();
	    $(".show-panel").show();
	}
    }
 
    /********************/
    /* Graph management */
    /********************/
    
    this.MAX_GRAPHS = 3;
    this.MAP_TYPE ='map';
    this.LINE_CHART_TYPE ='lineChart';
    this.HISTOFREQ_CHART_TYPE ='histofreqChart';
    this.STACKEDLINE_CHART_TYPE ='stackedLineChart';
    this.PIE_CHART_TYPE ='pieChart';
    this.HISTODATE_CHART_TYPE ='histodateChart';    
    var graphCounter = 1;
    this.maps = [];
    this.GraphsRender = []

    
    var AbstractGraphRenderer = function(graphId, param){
        this.graphId = graphId;
	this.param = param;
        this.width = '100%';
        this.height = '500px';
        this.createGraphDiv = function(){
            $("#charts-wrapper")
		.append(
		    $('<div style="margin: 5px 0 5px 0;position: relative;"></div>')
			.attr('id', "legenddiv-" + this.graphId)
		).append(
		    $("<div></div>").append(
			$("<div></div>")
			    .attr('id', this.graphId)
			    .css('width', this.width)
			    .css('height', this.height)
			
		    )
		)
        };

        this.render = function(){
            throw "render() Not Implemented";
        };
    };
    var MapRenderer = function(graphId, param){
        AbstractGraphRenderer.call(this, graphId, param);
        this.height = '600px';

        this.render = function(territoriesData){
	    var self = this;
	    var openlayer = new BatResultsOLMap(territoriesData, param);
	    openlayer.makeMap(self.graphId);
	    results.maps.push(openlayer);
	    self.chart = openlayer;
        };
    };
    var AbstractAMChartsGraphRenderer = function(graphId, param){
	AbstractGraphRenderer.call(this, graphId, param);
	this.getChart = function(chartData){
	    throw "getChart Not Implemented";
        };
	
	this.render = function(chartData){
            var chart = this.getChart(chartData);
	    this.chart = chart;
	    var cChart = chart.makeChart();
	    var graphDiv = $("#" + this.graphId);
	    // By default, consider it's AMCharts
	    graphDiv.height(graphDiv.height() + graphDiv.find(".amChartsLegend").height());
	    cChart.invalidateSize();
	    return;
        };

    };
    
    var LineChartRenderer = function(graphId, param){
        AbstractAMChartsGraphRenderer.call(this, graphId, param);

	this.getChart = function(chartData) {
	    return new LineChart(this.graphId, chartData);
        };
    };
    var StackedLineChartRenderer = function(graphId, param){
        AbstractAMChartsGraphRenderer.call(this, graphId, param);

	this.getChart = function(chartData) {
            return new StackedLineChart(this.graphId, chartData);
        };
    };

    var PieChartRenderer = function(graphId, param){
        AbstractAMChartsGraphRenderer.call(this, graphId, param);

	this.getChart = function(chartData) {
            return new PieChart(this.graphId, chartData);
        };
    };
    var HistodateChartRenderer = function(graphId, param){
        AbstractAMChartsGraphRenderer.call(this, graphId, param);

	this.getChart = function(chartData) {
            return new StackedBarChart(this.graphId, chartData);
        };
    };

    var HistofreqChartRenderer = function(graphId, param){
        AbstractAMChartsGraphRenderer.call(this, graphId, param);

	this.getChart = function(chartData) {
	    return  new HistoFreqChart(this.graphId, chartData);
        };
    };

    this.graphTypes = {};
    this.graphTypes[this.MAP_TYPE] = { 'name': this.MAP_TYPE, label: 'Cartographie', renderer: MapRenderer };
    this.graphTypes[this.LINE_CHART_TYPE] = { 'name': this.LINE_CHART_TYPE, label: 'Graph linéaire', renderer: LineChartRenderer  };
    this.graphTypes[this.STACKEDLINE_CHART_TYPE] = { 'name': this.STACKEDLINE_CHART_TYPE, label: 'Graph empilé', renderer: StackedLineChartRenderer };
    this.graphTypes[this.PIE_CHART_TYPE] = { 'name': this.PIE_CHART_TYPE, label: 'Camembert', renderer: PieChartRenderer };
    this.graphTypes[this.HISTODATE_CHART_TYPE] = { 'name': this.HISTODATE_CHART_TYPE, label: 'Histogramme temporel', renderer: HistodateChartRenderer };
    this.graphTypes[this.HISTOFREQ_CHART_TYPE] = { 'name': this.HISTOFREQ_CHART_TYPE, label: 'Histogramme fréquentiel', renderer: HistofreqChartRenderer };

    this.precisions = {}
    this.precisions["y"] = { 'name': "y", label: 'Annuelle'};
    this.precisions["m"] = { 'name': "m", label: 'Mensuelle'};
    this.precisions["w"] = { 'name': "w", label: 'Hebdomadaire'};
    this.precisions["d"] = { 'name': "d", label: 'Journalière'};
    this.precisions["6h"] = { 'name': "6h", label: 'Quart-journalière'};
    this.precisions["h"] = { 'name': "h", label: 'Horaire'};
    
    var Graph = function(){
        this.graphicType = results.graphTypes[results.MAP_TYPE];
        this.startDate = results.startDate;
        this.endDate = results.endDate;
        this.territory = results.geocodes;
        this.precision = results.precisions["y"];
	this.batiments = false;
	this.sumterr = false;
	this.sumgeocode = false;
	this.territories = current_simulation.territory_groups;
	
        this.getParams = function(){
            return {
                graphicType: this.graphicType.name,
                startDate: this.startDate,
                endDate: this.endDate,
                territory: this.territory,
		precision: this.precision.name,
		batiments: this.batiments,
		sumterr: this.sumterr,
		sumgeocode: this.sumterr,
		// for now, just one simu terr groups
		territories: this.territories,
            };
        };

    };
    
    var RenderGraph = function(graphID, param, graphData){
	this.data = graphData;
	this.graphType = results.graphTypes[graphData["graphType"]]
	this.graphID = graphID;
	this.param = param;
	this.param.simutype = graphData["simuType"];
	
        this.render = function(){
            var GraphRenderer = this.graphType.renderer;
            var graphRenderer = new GraphRenderer(this.graphID, param);
            graphRenderer.createGraphDiv();
            graphRenderer.render(this.data);
        };
        
    };

    this.variables = [];

    this.toggleVariable = function(varname){
	var ind = this.variables.findIndex(i => i.varname === varname.varname);
	if(ind >= 0){
	    this.removeVariable(varname);
	}
	else{
	    this.addVariable(varname);
	}
    };
    
    this.addVariable = function(varname){
	var self = this;
	if(varname._type == 2){
	    if(findWithAttr(self.variables, "varname", varname.varname) < 0){
		self.variables.push(varname);
		self.addModalCoche(varname.varname);
	    }
	}
	else{
	    varname.includes.forEach(function(varname){
		if(findWithAttr(self.variables, "varname", varname.varname) < 0){
		    self.variables.push(varname);
		    self.addModalCoche(varname.varname);
		}
		
	    });
	}
	    
    };

    this.removeVariable = function(varname){
	var ind = this.variables.findIndex(i => i.varname === varname.varname);
	if(ind >= 0){
	    this.delModalCoche(varname.varname);
	    this.variables.splice(ind, 1);
	}
    };

    this.geocodes = [];
    this.toggleGeocode = function(geocode){
	var ind = this.geocodes.indexOf(geocode.geocode);
	if(ind >= 0){
	    this.removeGeocode(geocode.geocode);
	}
	else{
	    this.addGeocode(geocode);
	}
    };
    
    this.addGeocode = function(geocodes){
	var self = this;
	if(geocodes.hasOwnProperty('includes')){
	    geocodes.includes.forEach(function(geocode){
		if(self.geocodes.indexOf(geocode.geocode) < 0) {
		    self.geocodes.push(geocode.geocode);
		    self.addModalCoche(geocode.geocode);
		    wsAGeocodes.cGeocodes[geocode.geocode] = geocode;
		}
	    });
	}
	else{
	    if(self.geocodes.indexOf(geocodes.geocode) < 0) {
		self.geocodes.push(geocodes.geocode);
		self.addModalCoche(geocodes.geocode);
		wsAGeocodes.cGeocodes[geocodes.geocode] = geocodes;
	    }
	}
    };

    this.removeGeocode = function(geocode){
	var ind = this.geocodes.indexOf(geocode);
	if(ind >= 0){
	    this.delModalCoche(geocode);
	    this.geocodes.splice(ind, 1);
	}
    };

    this.addModalCoche = function(id){
	$('.coche.'+id).show();
    }
    this.delModalCoche = function(id){
	$('.coche.'+id).hide();
    }
    
    

    this.graphs = [new Graph()];
    this.renderGraphs = [];
    
    this.addGraph = function(){
        this.graphs.push(new Graph());
    };
    this.removeGraph = function(index){
        this.graphs.splice(index, 1);
    };
    
    this.renderGraphs = function (allGraphData, param) {
	var rPromises = [];
	var gRender = [];
        // Empty previous graphs
        $('#charts-wrapper').html('');
        this.maps = [];

        angular.forEach( allGraphData, function(graphParam, graphID){
	    if(graphID == 'more'){
		messages.show('error');
	    }
	    rGraph = new RenderGraph(graphID, param[graphParam["indexParam"]], graphParam)
	    gRender.push(rGraph);
            rPromises.push(rGraph.render());
        });
	this.GraphsRender = gRender;

	return $q.all(rPromises);
    };

    this.loadResultsParams = function(download=false){
	var parametersList = $.map(this.variables, function(variable){
	    return variable.varname;
        });
	var simus = $('#simulationscompare').val();
	if (! simus) {
	    // no compare option available, use shortid
	    simus = [shortid]
	}
	else if(simus.length == 0){
		// no compare simu selected. By default use the current shortid
		simus = [shortid]
	}
	// currently, just one graph
	if (this.graphs.length == 0) {
	    return
	}
	var geocodes = _.map(this.graphs[0].territory, function(el) {return wsAGeocodes.cGeocodes[el]});
	var start = this.graphs[0].startDate;
	var end = this.graphs[0].endDate;
	var precision = this.graphs[0].precision.name;
	var graphType = this.graphs[0].graphicType.name;

	var batiment = this.graphs[0].batiments;
	var sumterr = this.graphs[0].sumterr;
	var territories =  this.graphs[0].territories;
	var sumgeocode = this.graphs[0].sumgeocode;
	// save requested parameters
	results.parameters = $.map(this.variables, function(variable){
	    ret = {};
	    ret['name'] = variable.varname;
	    ret['label'] = variable.label;
	    if(variable._type == 2){
		ret['includes'] = variable.includes;
		ret['_type'] = variable._type;
	    }
	    else{
		ret['_type'] = 0;
	    }
	    return ret;
        });

	// Instanciate a virtual acyclic graph to represent the request
	var VG = new DefaultVirtualGraph(results.parameters, simus, geocodes, precision, start, end, graphType, batiment, sumterr, territories, sumgeocode, download);
        var graphsParams = [];
        angular.forEach( this.graphs, function(graph){
            graphsParams.push(graph.getParams());
        });
	return {
	    params_urls: {
		workspace : VG.json(),
		startDate: start,
		endDate: end
            },
	    graphsParams: graphsParams
	};
    }
    this.load = function(){
	allParams = this.loadResultsParams();
	graphsParams = allParams['graphsParams'];
	messages.hide('error');
        var chartFetch = $http.post(chartUrl, allParams['params_urls']).success(
	    function(allGraphData){
		return results.renderGraphs(allGraphData, graphsParams);
            });

        return chartFetch;
    };
});

/***************/
/* Controllers */
/***************/

simulationResults.controller('MessagesCtrl', function($scope, messages){
    $scope.messages = messages;
});

simulationResults.controller('resultVariablesCtrl', function($scope, results, filteredresultvariables, simulationparameters){
    $scope.resultvariables = filteredresultvariables;
    $scope.selectedResultVariables = null;
    $scope.startsWith = function(name, viewValue) {
        if(name.label){
            return name.label.substr(0, viewValue.length).toLowerCase() == viewValue.toLowerCase();
	}
    };
});

simulationResults.controller('resultGeocodesCtrl', function($scope, results, filteredgeocodes){
    $scope.geocodes = filteredgeocodes;
    $scope.selectedGeocode = null;
    
    $scope.startsWith = function(name, viewValue) {
        if(name.label){
            return name.label.substr(0, viewValue.length).toLowerCase() == viewValue.toLowerCase();
	}
    };
});

simulationResults.controller('SimulationsCtrl', function($scope, $window, $timeout){
    $scope.simulations = $window.simulations;
    $scope.current_simulation = $window.current_simulation;
    $timeout(function() {
    	$('#simulationscompare').fSelect();
    }
     	     , 0);
});
simulationResults.controller('ResultsCtrl', function($scope, $timeout,  results, simulationparameters, downloadResultURL, $window){
    $scope.results = results;
    
    $scope.chartsVisible = false;
    $scope.chartsLoading = false;
    $scope.download = "graphic";
    $scope.loadCharts = function(){
        if( results.noParametersSelected() || results.noGeocodesSelected()){
            return;
        }

        $scope.chartsLoading = true;
        var chartReady = results.load();
        chartReady.then(function(){
            $scope.chartsVisible = true;
            $scope.chartsLoading = false;
            // Debounce map rendering to the next scope digest, so the map div is visible
            $timeout(function(){
                angular.forEach( results.maps, function(ol){
		    ol.centerMap();
                    ol.map.updateSize();
                });
            });
        });
    };
    $scope.downloadResults = function(){
        if( results.noParametersSelected() || results.noGeocodesSelected()){
            return;
        }

        $scope.chartsLoading = true;
	var downloadResultsParam = results.loadResultsParams(true)['params_urls'];
	var xhr = new XMLHttpRequest();
	xhr.open('POST', downloadResultURL, true);
	xhr.responseType = 'arraybuffer';
	xhr.onload = function () {
	    $scope.chartsLoading = false;
	    $scope.$apply();
	    if (this.status === 200) {
		var filename = "";
		var disposition = xhr.getResponseHeader('Content-Disposition');
		if (disposition && disposition.indexOf('attachment') !== -1) {
		    var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
		    var matches = filenameRegex.exec(disposition);
		    if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
		}
		var type = xhr.getResponseHeader('Content-Type');
		
		var blob = new Blob([this.response], { type: type });
		if (typeof window.navigator.msSaveBlob !== 'undefined') {
		    // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
		    window.navigator.msSaveBlob(blob, filename);
		} else {
		    var URL = window.URL || window.webkitURL;
		    var downloadUrl = URL.createObjectURL(blob);
		    
		    if (filename) {
			// use HTML5 a[download] attribute to specify filename
			var a = document.createElement("a");
			// safari doesn't support this yet
			if (typeof a.download === 'undefined') {
			    window.location = downloadUrl;
			} else {
			    a.href = downloadUrl;
			    a.download = filename;
			    document.body.appendChild(a);
			    a.click();
			}
		    } else {
			window.location = downloadUrl;
		    }
		    
		    setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup
		}
	    }
	};
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	xhr.send(JSON.stringify(downloadResultsParam));	
    };
});
