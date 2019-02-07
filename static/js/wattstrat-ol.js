var angular;

var BaseOLMap = function(){
    this.map = null;
    var self= this;
    
    this.attribution = [
        new ol.Attribution({
            html: 'Tiles &copy; Esri'
        }),
        ol.source.OSM.ATTRIBUTION
    ];

    
   this.baseFeatureStyle = new ol.style.Style({
	fill: new ol.style.Fill({
	    color: [170,170,170,0.7],
	}),
	stroke: new ol.style.Stroke({
	    width: 0.5,
	    color: [255,255,255,1],
	})
    });
    
    this.highlightedFeatureStyle = new ol.style.Style({
	fill: new ol.style.Fill({
	    color: [170,170,170,1],
	}),
	stroke: new ol.style.Stroke({
	    width: 5,
	    color: [102,102,102,1],
	})
    });
    this.noStyle = new ol.style.Style({
	display: "non",
    });

    this.getGeocodeFromFeature = function(feature) {
    	var geocode = null;
	var props = feature.getProperties();
	// TODO : faire un truc correct...
	if(props.geocode){
	    geocode = props.geocode;
	}
	else if(props.insee_com){
	    geocode = 'FR' + props.insee_com;
	}
	else if(props.code_dept){
	    geocode = 'FR992' + props.code_dept;
	}
	else if(props.insee){
	    geocode = 'FR' + props.insee;
	}
	else if(props.code_insee){
	    geocode = 'FR992' + props.code_insee;
	}


	return geocode;
    };

    this.getIdFromFeature = function(feature){
	var id=this.getGeocodeFromFeature(feature);
	var props = feature.getProperties();
	if(id){
	    return id;
	}
	if(props.osm_id !== undefined){
	    return "BATOSM" + props.osm_id;
	}
	if(props.id_bat !== undefined){
	    return props.id_bat;
	}
	return null;
    };
	
	

    this.styleFunction = function(feature) {
	var style = null;
	var baseStyle = null;
	var base = null;

	var id = self.getIdFromFeature(feature);
	var styleKey = self.getFillColor(id);
	var highlight=false;
	
	if(id === null || styleKey === null){
	    return this.noStyle;
	}
	
	highlight = self.highlightedFeature[id];
	 
	if(highlight){
	    base = self.highlightStyleCache;
	    baseStyle =  self.highlightedFeatureStyle;
	}
	else{
	    base = self.styleCache;
	    baseStyle = self.baseFeatureStyle;
	}
	style = base[styleKey];
	if (!style) {
	    var stroke = baseStyle.getStroke();
	    var fill = baseStyle.getFill();
	    var newFill = fill.clone();
	    var fillAlpha = fill.getColor()[3];
	    // should be a alpha channel on base style
	    var color = self.getFillColorArray(id, fillAlpha);
	    if(color === null){
		return this.noStyle;
	    }
	    newFill.setColor(color);
	    style = new ol.style.Style({
		stroke: stroke,
		fill: newFill
	    });
	    base[styleKey] = style;
	}
	return style;
    };

    this.addControl = function(){
	// add location search for france only
	var filterData = function(data){
	    return data.address == null || data.address.country == "France";
	}
	this.map.addControl(new ol.control.LocationSearch({filter: filterData}));
	// add fullcreen mode
	this.map.addControl(new ol.control.FullScreen({
	    tipLabel: 'Alterner le plein écran'
	}));
	// Add Layer Switch
	this._layerSwitch = new ol.control.LayerSwitcher();
	this.map.addControl(this._layerSwitch);
	this.map.getView().on('change:resolution', function(evt) {
	    self._layerSwitch.enableOneByGroup();
	});

	// Add  Download control
	this._download = new ol.control.Download();
	this.map.addControl(this._download);
	
	// TODO: add mesure control
	
	
    }
    var osmVectCommune = new ol.source.VectorTile({
		format: new ol.format.MVT(),
		url: '/world/tiles/communes-osm/' +
		    '{z}/{x}/{y}.mvt'
    });
    this.BaseRaster=[
        new ol.layer.Tile({
            title: 'Vue satellite (ESRI)',
            type: 'base',
	    group: 'base',
            visible: false,
	    source: new ol.source.XYZ({
		attributions: [
		    new ol.Attribution({
			html: 'Tiles © <a href="https://services.arcgisonline.com/ArcGIS/' +
		            'rest/services/World_Imagery/MapServer">ArcGIS</a>'
		    })],
		url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
	    })
        }),
        new ol.layer.Tile({
            title: 'Vue OpenStreetMap',
            type: 'base',
	    group: 'base',
            visible: true,
            source: new ol.source.OSM()
        })
    ];
    this.VectLayers=[
	new ol.layer.VectorTile({
	    title: 'Département',
	    visible: true,
	    group: 'calque',
	    name: 'Departement',
	    maxResolution: 4000,
	    minResolution: 20,
	    source: new ol.source.VectorTile({
		format: new ol.format.MVT(),
		url: '/world/tiles/departements-osm/' +
		    '{z}/{x}/{y}.mvt'
	    }),
	    style: this.styleFunction,
	}),
	new ol.layer.VectorTile({
	    title: 'Communes',
	    visible: false,
	    group: 'calque',
	    name: 'Commune',
	    maxResolution: 500,
	    minResolution: 3,
	    source: osmVectCommune,
	    style: this.styleFunction,
	}),
	new ol.layer.VectorTile({
	    title: 'Batiments',
	    name: 'Bat',
	    visible: false,
	    group: 'calque',
	    maxResolution: 3,
	    source: new ol.source.VectorTile({
		format: new ol.format.MVT(),
		url: '/map/bati/' +
		    '{z}/{x}/{y}.mvt'
	    }),
	    style: this.styleFunction,
	}),

    ];

    this.addBaseLayers = function(){
	this.map.addLayer(new ol.layer.Group({
            'title': 'Fond de carte',
            layers: this.BaseRaster
        }));
    }
    
    this.addVectorLayers = function(){
	this.map.addLayer(new ol.layer.Group({
	    'title': 'Calque',
            layers: this.VectLayers
        }));
    }

    
    this.makeMap = function(mapId){
	this.map = new ol.Map({
            target: mapId,
            view: new ol.View({
		//projection: 'EPSG:2154',
		//projection: 'EPSG:3857',
		center: [295964.2735202024, 5950103.069783269],
		zoom: 6
            }),
	});
	this.legends = document.createElement('div');
	this.legends.className = "ol-legends";
	
	document.getElementsByClassName("ol-overlaycontainer-stopevent")[0].appendChild(this.legends);
	
	this.map.WSR = this;
	this.highlightedFeature = {};
	this.legenddiv = $('#legenddiv-' + mapId);
	this.map.on('pointermove', function(evt) {
	    if (evt.dragging) return;
	    
	    self.highlightedFeature = {};

	    self.map.forEachFeatureAtPixel(evt.pixel, function(feature) {
		self.highlightedFeature[self.getIdFromFeature(feature)] = true;
	    });
	    self.updateStyleFeature();
	});
	
	this.addBaseLayers();
	this.addVectorLayers();
	this.addControl();
    };

    this.styleCache = {};
    this.highlightStyleCache = {};

    this.updateStyleFeature = function(){
	for(var ind=0;ind<this.VectLayers.length; ind++){
	    this.VectLayers[ind].getSource().dispatchEvent('change');
	}
    }


    this.highlightStyleFunction = function(feature) {
	this.styleFunction(feature, true);
    };
    this.getFillColor = function(feature) {
        return "grey";
    };

    this.getFillColorArray = function(feature) {
        return [170,170,170];
    };
	

};



// formatage nb
// d3Format.format('.2s')(from).concat(activeTerritory.unit)

var ResultsOLMap = function(territoriesData){
    var self=this;
    BaseOLMap.call(this);

    this.BATIMENTBUY_COLOR = [68,68,68, 0.8];
    this.BATIMENTNOTCOMPUTE_COLOR = [0,0,0, 1];
    this.territoriesData = territoriesData;
    this.parametersList = territoriesData.parametersList;
    this.parametersLabel = territoriesData.parametersLabel;
    
    this.parameterIdx = 0;
    this.activeTerritory = this.territoriesData[this.parametersList[this.parameterIdx]];
   
    this.colorScaleConfig = {
        startColor: '#FFCC00',
        endColor: '#990000',
        steps: 10,
        colorSpace: 'lab'
    };
    
    this.colorScale = null;

    this.formatData = function(val, datas){
	return d3.format('.2s')(val) + self.activeTerritory.unit;
    }
    this.extractDataDept = function(data){
	if(data.geocode.substr(0,5) == 'FR992'){
	    return data.value;
	}
	return null;
    }
    this.extractDataCom = function(data){
	if(data.geocode.substr(0,5) !== 'FR99'){
	    return data.value;
	}
	return null;
    }

    this.formatDisplayVariable = function(element){
	return this.formatData(element);
    }


    this.displayVariableGeocode = function(feature, layer, all=false){
	var innerHTML ='';
	var info=false;
	var props = feature.getProperties();
	var geocode = self.getIdFromFeature(feature);

	if(geocode == null){
	    return '';
	}
	var name = props.nom;
	if (!name){
	    name = layer.get('name');
	}
	innerHTML += '<div class="variable-info ' + layer.get('name') + '"><h3><span class="variable-title">';
	innerHTML += name;
	innerHTML += '</span>';
	if(!all && self.activeTerritory.values[geocode]){
	    innerHTML += ' : <span class="variable-value">';
	    innerHTML += self.formatDisplayVariable(self.activeTerritory.values[geocode]);
	    innerHTML += '</span>';
	    info=true;
	}
	innerHTML += '</h3>';
	if(all){
	    innerHTML += '<ul>'
	    for(var index=0;index < self.parametersLabel.length; index++){
		if(self.territoriesData[self.parametersList[index]].values[geocode]){
		    innerHTML += '<li>' + self.parametersLabel[index] + ': ';
		    innerHTML += self.formatDisplayVariable(self.territoriesData[self.parametersList[index]].values[geocode]);
		    innerHTML += '</li>';
		    info=true;
		}
	    }
	    innerHTML += '</ul>';
	}
	innerHTML += '</div>';
	if(!info)
	    return '';
	return innerHTML;
    };

    this.displayAllVariablesGeocode = function(feature, layer){
	return self.displayVariableGeocode(feature, layer, true);
    };

    this.displayBat = function(feature, layer){
	var props = feature.getProperties();

	if(props.IGN){
	    return self.displayBatimentVariable(feature, layer);
	}
	else{
	    return self.displayBatBuyData(feature, layer)
	}
    }
    
    this.popupDisplayBat = function(feature, layer){
	var props = feature.getProperties();

	if(props.IGN){
	    return self.displayBatimentVariable(feature, layer);
	}
	return '';
    }
    this.displayBatBuyData = function(feature, layer){
	var innerHTML = '<div class="variable-info buy-batiment">';
	innerHTML += '<h3>Achat de données Batiments</h3>';
	//	innerHTML += '<a href="/buybatimentdata.html">Cliquez ici pour acheter les données de ce batiment</a><br />';
	//	innerHTML += '<a href="/buybatimentscommunedata.html">Cliquez ici pour acheter les données des batiments de toute la commune</a>';
	innerHTML += '<a href="/support/">Pour acheter les données de ce batiment ou de la commume, veuillez nous contacter</a>';
	innerHTML += '</div>';
	return innerHTML;
    };

    this.displayBatimentVariable = function(feature, layer){
	var innerHTML = '<div class="variable-info batiment">';
	innerHTML += '<h3>Batiment</h3>';
	innerHTML += '<span>Not Yet Implemented</span>';
	innerHTML += '</div>';
	return innerHTML;
	
    };
    
    this.popupFunctionByLayer = {
	Monde: this.displayVariableGeocode,
	Departement: this.displayVariableGeocode,
	Commune:this.displayVariableGeocode,
	BatIGN:this.displayBatimentVariable,
	Bat:this.popupDisplayBat,
    };

    this.clickpopupFunctionByLayer = {
	Monde: this.displayAllVariablesGeocode,
	Departement: this.displayAllVariablesGeocode,
	Commune:this.displayAllVariablesGeocode,
	BatIGN:this.displayBatimentVariable,
	BatOSM:this.displayBatBuyData,
	Bat:this.displayBat,
    };

    this.displayTooltip = function (evt, functionsByLayer) {
	var pixel = evt.pixel;
	var innerHTML = '';
	var alreadyDisplayedData = {};
	self.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
	    var nLayer=layer.get('name');
	    var idFeature = self.getIdFromFeature(feature);
	    if(!functionsByLayer[nLayer] || alreadyDisplayedData[idFeature]){
		return;
	    }
	    innerHTML += functionsByLayer[nLayer](feature, layer);
	    alreadyDisplayedData[idFeature]=true;
	});

	return innerHTML;
    };


    // on pointer move
    this.displayTooltipPointerMove = function(evt){
	if (evt.dragging) return;
	if(self.popup.isOpened()){
	    if(self.tooltip.style.display != 'none'){
		self.tooltip.style.display = 'none';
	    }
	    return;
	}
	else{
	    var innerHTML = self.displayTooltip(evt,self.popupFunctionByLayer);
	    if(innerHTML == ''){
		if(self.tooltip.style.display != 'none'){
		    self.tooltip.style.display = 'none';
		}
		return;
	    }
	    if(self.tooltip.style.display == 'none'){
		self.tooltip.style.display = 'block';
	    }
	    self.overlay.setPosition(evt.coordinate);
	    self.tooltip.innerHTML = innerHTML;
	}
    };
    
    //on pointerclick
    this.displayTooltipPointerClick = function(evt){
	var innerHTML = self.displayTooltip(evt,self.clickpopupFunctionByLayer);
	if(innerHTML == ''){
	    return;
	}
	self.tooltip.style.display = 'none';
	self.popup.show(evt.coordinate, innerHTML);
    }
    
    this.makeTooltipOverlay = function(){
	this.tooltip = document.createElement('div');
	this.tooltip.className = 'tooltip';
	this.map.getTargetElement().appendChild(this.tooltip);
	
	this.overlay = new ol.Overlay({
	    element: this.tooltip,
	    offset: [10, 0],
	    positioning: 'bottom-left'
	});
	
	this.map.addOverlay(this.overlay);

	this.popup = new ol.Overlay.Popup();
	this.map.addOverlay(this.popup);
    };

    this._superMakeMap = this.makeMap;
    this.makeMap = function(mapId){
        this._superMakeMap(mapId);
	this.makeLegend();
	this.makeCenterMapTool();
	this.makeVariableSelector();
	this.makeTooltipOverlay();
	if(this.activeTerritory){
	    this.setDataIndex(0);
	    // Have we dept in data?
	    var dept=false;
	    for( var mykey in this.activeTerritory.values ) {
		if(mykey.substring(0,5) == 'FR992'){
		    dept=true;
		    break;
		}
	    }
	    if(dept){
		this.VectLayers[0].setVisible(true);
		this.VectLayers[1].setVisible(false);
	    }
	    else{
		this.VectLayers[0].setVisible(false);
		this.VectLayers[1].setVisible(true);
	    }
	}
	this.centerMap();
	this.map.on('pointermove', this.displayTooltipPointerMove);
	this.map.on('singleclick', this.displayTooltipPointerClick);

	if(this.switcher){
	    this.switcher.show();
	}
	if(this.VectLayers[0].getVisible() && this.legendDept.colorScale != null){
	    // Departement visible
	    this.legendDept.show();
	}
	if(this.VectLayers[1].getVisible()  && this.legendCom.colorScale != null){
	    // Communes visible
	    this.legendCom.show();
	}
    };
    this.makeCenterMapTool = function(){
	this._CenterMapTool = new ol.control.CenterMap();
	this.map.addControl(this._CenterMapTool);
    };
    
    this.centerMap = function(){
	if(this.activeTerritory && this.activeTerritory.bbox){
	    var format = new ol.format.WKT();
	    var feature = format.readFeature(this.activeTerritory.bbox);
//	    ,{
//		dataProjection: 'EPSG:3857',
//		featureProjection: 'EPSG:3857'});
	    var polygon = feature.getGeometry();
	    this.map.getView().fit(polygon);
	}
	else{
	    // Center France
	    this.map.getView().setZoom(6);
	    this.map.getView().setCenter([295964.2735202024, 5950103.069783269]);
	}
//	this._layerSwitch.enableOneByGroup();
    };
    this.switchParam = function(e){
	self.setDataIndex(e.target.value);
    };

    this.setDataIndex = function(index, update=true){
	this.parameterIdx = index;
	this.activeTerritory = this.territoriesData[this.parametersList[this.parameterIdx]]
	if(this._download){
	    this._download.setFilename(this.parametersLabel[this.parameterIdx] + '.png');
	}

	// set legend
	this.legenddiv.html('<h3><b>' + this.parametersLabel[this.parameterIdx] + '</b></h3>');

	// transform data
	var datas = [];
	
	for( var mykey in this.activeTerritory.values ) {
	    datas.push({value: this.activeTerritory.values[mykey], unit: this.activeTerritory.unit, geocode: mykey});
	}
	self.legendDept.setDatas(datas);
	self.legendCom.setDatas(datas);
	self.colorScaleDept = self.legendDept.colorScale;
	self.colorScaleCom = self.legendCom.colorScale;
	this.changeDisplayByResLegend();
	if(update){
	    // update features
	    this.updateStyleFeature();
	}

    };


    
    this.changeDisplayByResLegend = function(){
	var layers = [self.VectLayers[0] , self.VectLayers[1]];
	var legends = [self.legendDept, self.legendCom]
	var curRes = self.map.getView().getResolution(); // current resolution
	for(var i=0; i<layers.length; i++){
	    var layer=layers[i];
	    var minRes=layer.getMinResolution();
	    var maxRes=layer.getMaxResolution();

	    if(legends[i].colorScale != null && layer.getVisible() && minRes <= curRes && curRes < maxRes){
		legends[i].show();
	    }
	    else{
		legends[i].hide();
	    }
	}
    }

    this.makeLegend = function(){
	this.legendDept = new ol.control.LegendScaledColor({
	    title: '<h4>Départements</h4>',
	    formatData: this.formatData,
	    extract: this.extractDataDept,
	    target: this.legends,
	});
	this.legendCom = new ol.control.LegendScaledColor({
	    title: '<h4>Communes</h4>',
	    formatData: this.formatData,
	    extract: this.extractDataCom,
	    target: this.legends,
	});
	this.map.addControl(this.legendDept);
	this.map.addControl(this.legendCom);
	this._layerSwitch.on("layer:visibility", function(evt){
	    var nLayer=evt.layer.get("name");
	    if(nLayer == "Commune" || nLayer == "Departement"){
		self.changeDisplayByResLegend();
	    }
	});
	    
	this.map.getView().on('change:resolution', function(evt) {
	    self.changeDisplayByResLegend();
	});
	if(this._download){
	    this._download.on("download:click", function(evt){
		if(self.VectLayers[0].getVisible() && self.legendDept.colorScale != null){
		    self._download.addElmt({'el': self.legendDept.element, 'decH': -5, 'decW': -5, 'style': "<style>.ol-legend-scaledcolor {    clear:both; display: block; bottom: 5em;    right: 0;    text-align: left;    line-height: 18px;    color: #555;}.ol-legend-scaledcolor.legend-title h4{    float:right;margin: 0 0 10px;    color: #777; }.ol-legend-scaledcolor.ol-legend-scaledcolor-elm i{    width: 18px;    height: 18px;    float: left;    margin-right: 8px;    opacity: .7}.ol-legend-scaledcolor.ol-legend-scaledcolor-elm{    float: left;    clear: left;    display: inline-flex;}.ol-legend-scaledcolor.ol-legend-scaledcolor-elm-txt {}.ol-legend-scaledcolor.ol-legend-scaledcolor-info {    padding: 6px 8px;    font: 14px/16px Arial, Helvetica, sans-serif;    background: #fff;    background: rgba(255, 255, 255, .9);    box-shadow: 0 0 15px rgba(0, 0, 0, .2);    border-radius: 5px;    float: right;		       }</style>"});
		    
		}
		if(self.VectLayers[1].getVisible() && self.legendCom.colorScale != null){
		    self._download.addElmt({'el': self.legendCom.element, 'decH': -5, 'decW': -5, 'style': "<style>.ol-legend-scaledcolor {    clear:both; display: block; bottom: 5em;    right: 0;    text-align: left;    line-height: 18px;    color: #555;}.ol-legend-scaledcolor.legend-title h4{    float:right;margin: 0 0 10px;    color: #777; }.ol-legend-scaledcolor.ol-legend-scaledcolor-elm i{    width: 18px;    height: 18px;    float: left;    margin-right: 8px;    opacity: .7}.ol-legend-scaledcolor.ol-legend-scaledcolor-elm{    float: left;    clear: left;    display: inline-flex;}.ol-legend-scaledcolor.ol-legend-scaledcolor-elm-txt {}.ol-legend-scaledcolor.ol-legend-scaledcolor-info {    padding: 6px 8px;    font: 14px/16px Arial, Helvetica, sans-serif;    background: #fff;    background: rgba(255, 255, 255, .9);    box-shadow: 0 0 15px rgba(0, 0, 0, .2);    border-radius: 5px;    float: right;		       }</style>"});
		}
	    });
	}
    }


    this.makeVariableSelector = function(){
	if (this.parametersList.length <= 1){
	    return;
	}
	
	var index= 0;
	var params = [];

	for (var index=0; index<this.parametersList.length; index++) {
	    params.push({value: index, text: '<b>' + this.parametersLabel[index]  + '</b>'});
	}


	this.switcher = new ol.control.StyleSwitcher({
	    onChange: this.switchParam,
	    selectors: params
	});
	this.map.addControl(this.switcher);
	
    };


    this.getTerritoryValue = function(id){
	if(id.substring(0,8) == "BATIMENT"){
	    return 0;
	}
	    
        return this.activeTerritory.values[id];
    };

    this.getFillColor = function(id) {
	if(id.substring(0,6) == "BATOSM"){
	    return "batimentbuy";
	}

        var territoryVal = this.getTerritoryValue(id);
        if( territoryVal === undefined ){
            return null;
        }
        if( territoryVal === 0){
            return "white";
        }
	if(id.substring(0,5) == 'FR992'){
	    return this.colorScaleDept(territoryVal).name();
	}
	else{
	    return this.colorScaleCom(territoryVal).name();
	}
        
    };
    this.getFillColorArray = function(id, alpha) {
	if(id.substring(0,6) == "BATOSM"){
	    return this.BATIMENTBUY_COLOR;
	}
        var territoryVal = this.getTerritoryValue(id);
        if( territoryVal === undefined ){
            return null;
        }
        if( territoryVal === 0){
            return [255,255,255,alpha];
        }
	if(id.substring(0,5) == 'FR992'){
	    var rgb=this.colorScaleDept(territoryVal).rgb();
	}
	else{
	    var rgb=this.colorScaleCom(territoryVal).rgb();
	}
	
	
        rgb.push(alpha);
	return rgb;
    };
    // this.getPopupContent = function(feature) {
    //     var territoryVal = this.getTerritoryValue(feature);
    //     var popupContent = feature.properties.name;
    //     if( territoryVal !== undefined ){
    //         popupContent += " : " + d3.format('.4s')(this.getTerritoryValue(feature)).concat(this.activeTerritory.unit);
    //     }
    //     return popupContent;
    // };
};




var BatResultsOLMap = function(territoriesData, param){
    var self=this;
    ResultsOLMap.call(this, territoriesData);

    this.legendBat = null;
    this.scaleColorBat = null;

    this.param=param
    this._super2MakeMap = this.makeMap;
    this.makeMap = function(mapId){
        this._super2MakeMap(mapId);
	if(this.param.batiments){
	    this.makeLegendBat();
	}
	//TODO call this 2 times...
	if(this.activeTerritory){
	    this.setDataIndex(0);
	}
	if(this.param.batiments){
	    this.changeDisplayByResLegendBat();
	}
	this.popupFunctionByLayer.BatIGN = this.displayBatimentVariable;
	this.clickpopupFunctionByLayer.BatIGN = this.displayAllBatimentVariable;
    };
    
    this.addVectorLayers = function(){
	this.map.addLayer(new ol.layer.Group({
	    'title': 'Calque',
	    layers: this.VectLayers
        }));
    }

    this.changeDisplayByResLegendBat = function(){
	var layers = [self.VectLayers[2]];
	var curRes = self.map.getView().getResolution(); // current resolution
	
	if(self.legendBat.colorScale == null){
	    self.legendBat.hide();
	    return;
	}
	for(var i=0; i<layers.length; i++){
	    var layer=layers[i];
	    if(layer.getVisible()){
		var minRes=layer.getMinResolution();
		var maxRes=layer.getMaxResolution();
		if (minRes < curRes && curRes < maxRes) {
		    self.legendBat.show();
		    return;
		}
	    }
	}
	self.legendBat.hide();
    }
    this.makeLegendBat = function(){
     	this.legendBat = new ol.control.LegendScaledColor({
     	    title: '<h4>Batiments</h4>',
	    formatData: this.formatData,
	    cssClass: 'legend-batiments ol-legend-scaledcolor',
	    target: this.legends,
     	});
     	this.map.addControl(this.legendBat);
	this._layerSwitch.on("layer:visibility", function(evt){
	    var nLayer=evt.layer.get("name");
	    if(nLayer == "Bat" && self.activeTerritory.batiments){
		self.changeDisplayByResLegendBat();
	    }
	});
	this.map.getView().on('change:resolution', function(evt) {
	    if(self.activeTerritory.batiments){
		self.changeDisplayByResLegendBat();
	    }
	});
	if(this._download){
	    this._download.on("download:click", function(evt){
		if(self.VectLayers[2].getVisible() && self.legendBat.colorScale != null){
		    self._download.addElmt({'el': self.legendBat.element, 'decH': -5, 'decW': -5, 'style': "<style>.ol-legend-scaledcolor {    clear:both; display: block; bottom: 5em;    right: 0;    text-align: left;    line-height: 18px;    color: #555;}.ol-legend-scaledcolor.legend-title h4{    float:right;margin: 0 0 10px;    color: #777; }.ol-legend-scaledcolor.ol-legend-scaledcolor-elm i{    width: 18px;    height: 18px;    float: left;    margin-right: 8px;    opacity: .7}.ol-legend-scaledcolor.ol-legend-scaledcolor-elm{    float: left;    clear: left;    display: inline-flex;}.ol-legend-scaledcolor.ol-legend-scaledcolor-elm-txt {}.ol-legend-scaledcolor.ol-legend-scaledcolor-info {    padding: 6px 8px;    font: 14px/16px Arial, Helvetica, sans-serif;    background: #fff;    background: rgba(255, 255, 255, .9);    box-shadow: 0 0 15px rgba(0, 0, 0, .2);    border-radius: 5px;    float: right;		       }</style>"});
		}
	    });
	}

    };
    
    this._superSetDataIndex = this.setDataIndex;
    this.setDataIndex = function(index, update=true){
	var superUpdate = !self.legendBat ||  !this.activeTerritory.batiments;
	this._superSetDataIndex(index, superUpdate);
	if(superUpdate){
	    return;
	}
	// set legend
	//self.legendBat.setTitle('<h4><b>' + this.parametersLabel[this.parameterIdx] + ' (batiment)</b></h4>');
	// transform data
	var datas = [];
	
	for( var mykey in this.activeTerritory.batiments ) {
	    datas.push(this.activeTerritory.batiments[mykey]);
	}
	
	self.legendBat.setDatas(datas);
	self.colorScaleBat = self.legendBat.colorScale;
	this.changeDisplayByResLegendBat();
	if(update){
	    // update features
	    this.updateStyleFeature();
	}
    };

    this.calcEnerBat=function(props){
	return;
    }

    // this.cacheBatiment = {};
    // this.updateCacheBatiment = function (){
    // 	this.cacheBatiment = {};
    // 	this.VectLayers[0].forEachFeature( function(feature){
    // 	    var props = feature.getProperties();
    // 	    self.cacheBatiment.props.id_bat = props;
    // 	    self.calcEnerBat(props);
    // 	});
    // };

    // this.getBatimentData = function(key) {
    // 	var ba = this.cacheBatiment.key;
    // 	if(bat == null){
    // 	    this.updateCacheBatiment();
    // 	    bat = this.cacheBatiment.key;
    // 	}
    // 	return bat;
    // };
    


    this.getTerritoryValue = function(id){
	if(id.substring(0,8) == "BATIMENT"){
	    if(!this.activeTerritory.batiments)
		return "batimentnotcompute";
	    return this.activeTerritory.batiments[id];
	}
	val=this.activeTerritory.values[id];
	if (val === undefined){
	    return null;
	}
        return val;
    };

    this.getFillColor = function(id) {
	
	if(id.substring(0,6) == "BATOSM"){
	    return "batimentbuy";
	}

	var territoryVal = this.getTerritoryValue(id);

	if(territoryVal == "batimentnotcompute"){
	    return "batimentnotcompute";
	}
	if(territoryVal === null){
	    return null;
	}
        if( territoryVal === undefined ){
            return "transparent";
        }
        if( territoryVal === 0){
            return "white";
        }
	if(id.substring(0,8) == "BATIMENT"){
	    return this.colorScaleBat(territoryVal).name();
	}
	
        if(id.substring(0,5) == 'FR992'){
	    return this.colorScaleDept(territoryVal).name();
	}
	else{
	    return this.colorScaleCom(territoryVal).name();
	}

    };
    this.getFillColorArray = function(id, alpha) {
	if(id.substring(0,6) == "BATOSM"){
	    return this.BATIMENTBUY_COLOR;
	}

        var territoryVal = this.getTerritoryValue(id);
	if (territoryVal == "batimentnotcompute"){
	    return this.BATIMENTNOTCOMPUTE_COLOR;
	}
        if( territoryVal === undefined ){
            return [0,0,0,0];
        }
        if( territoryVal === 0){
            return [255,255,255,alpha];
        }
	var rgb=[];
	if(id.substring(0,8) == "BATIMENT"){
	    rgb=this.colorScaleBat(territoryVal).rgb();
	}
	else if(id.substring(0,5) == 'FR992'){
	    rgb=this.colorScaleDept(territoryVal).rgb();
	}
	else{
	    rgb=this.colorScaleCom(territoryVal).rgb();
	}
        rgb.push(alpha);
	return rgb;
    };

    this.displayBatimentVariable = function(feature, layer, all=false){
	var idBat = self.getIdFromFeature(feature);
	if(idBat == null){
	    return '';
	}
	var innerHTML = '<div class="variable-info batiment">';
	innerHTML += '<h3>Batiment</h3>';
	if(this.activeTerritory.batiments){
	    
	    if(all){
		innerHTML += '<ul>'
		for(var index=0;index < self.parametersLabel.length; index++){
		    if(self.territoriesData[self.parametersList[index]].batiments){
			if(self.territoriesData[self.parametersList[index]].batiments[idBat]){
			    innerHTML += '<li>' + self.parametersLabel[index] + ': ';
			    innerHTML += self.formatDisplayVariable(self.territoriesData[self.parametersList[index]].batiments[idBat]);
			    innerHTML += ' ' + self.territoriesData[self.parametersList[index]].unit + '</li>';
			    info=true;
			}
		    }
		}
		innerHTML += '</ul>';
	    }
	    else if(self.activeTerritory.batiments && self.activeTerritory.batiments[idBat]){
		innerHTML += self.parametersLabel[self.parameterIdx] + ': ';
		innerHTML += self.formatDisplayVariable(self.activeTerritory.batiments[idBat]);
		innerHTML += ' ' + self.activeTerritory.unit + '</li>';
		info=true;
	    }
	}
	else{
	    innerHTML += '<p>Vous n\'avez pas activé le rendu des batiments.</p><p>Merci de chocer la case «Rendu batiments» dans la configuration des graphiques.</p>';
	}
	innerHTML += '</div>';
	return innerHTML;
	
    };
    this.displayAllBatimentVariable = function(feature, layer){
	return self.displayBatimentVariable(feature, layer, true);
    };
};
    


var wattstratOL = angular.module('ws.ol', ['ng.django.urls', 'wattstrat']);

wattstratOL.directive('wsOLDynamicMap', function($http, locale){
    var mapId = 'dynamic-map';
    
    function mapContainerTemplate(element, attributes){
        var defaultAttr = {
            mapWidth: '100%',
            mapHeight: '600px' // Height at which France fits totally with default zoom level
        };
        attributes = $.extend({}, defaultAttr, attributes);
        
        var width = attributes.mapWidth;
        var height = attributes.mapHeight;
        return '<div id="' + mapId + '" style="width: ' + width + '; height: ' + height + '"></div>';
    }
    
    
    return {
        restrict: 'E',
        scope: {
            selectedGeocodes: '=',
	    removeFirst: '=',
            getFillColor: '&'
        },
        template: mapContainerTemplate,
        link: function(scope, element, attrs) {
            // var leaflet = new DynamicLeafletMap(scope.getFillColor);
            // leaflet.makeMap(mapId);
            
            // function reloadLeaflet(){
            //     var selectedGeocodes = scope.selectedGeocodes;
            //     var remFirst = scope.removeFirst;
            //     var geoJsonUrl = null;
            //     var params = {};

            //     // TODO allgroups : concat the geocodes of all groups to get a geojson
                
            //     // Custom geocodes
            //     if( selectedGeocodes && ((selectedGeocodes.length > 1 && remFirst == "1") || (selectedGeocodes.length > 0 && remFirst != "1"))){
            //         geoJsonUrl = dynamicGeoJsonUrl;
            //         // Remove the country from the geocodes
	    // 	    var geocodesWithoutCountry=[];
	    // 	    if(remFirst == "1"){
	    // 		geocodesWithoutCountry = selectedGeocodes.slice(1)
	    // 	    }
	    // 	    else{
	    // 		geocodesWithoutCountry = selectedGeocodes;
	    // 	    }
            //         params = {
            //             geocodes: JSON.stringify(geocodesWithoutCountry)
            //         };
            //     }
            //     // No geocodes except the country : just display the whole country
            //     else{
            //         geoJsonUrl = '/static/geo/maps/' + locale.country + '/' + geocodes.country.geocode + '.geojson';
            //     }
            
            //     $http.get(geoJsonUrl, {
            //         params: params,
            //         cache: true
            //     })
            //     .success(function(geoJsonData){
            //         leaflet.setGeoJsonLayer(geoJsonData);
            //         leaflet.renderView();
            //     });
            // }
            
            // // Once geocodes are loaded, we can setup the map
            // geocodes.dataPromise.then(function(){
            //     // First loading
            //     reloadLeaflet();
            //     // Update leaflet on geocodes changes
            //     scope.$watchCollection('selectedGeocodes', reloadLeaflet);
            // });
            
        }
    };
});
