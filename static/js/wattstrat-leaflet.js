var angular, L;

/** Base class for ResultsLeafletMap & DynamicLeafletMap **/
var BaseLeafletMap = function(){
    this.map = null;
    this.geoJson = null;
    this.geoJsonData = null;
    
    var DEFAULT_FILL_COLOR = '#aaa'; // Default fillColor when no color is set through this.getFillColor

    this.baseFeatureStyle = {
        weight: 0.5,
        opacity: 1,
        color: 'white',
        dashArray: '',
        fillColor: DEFAULT_FILL_COLOR, 
        fillOpacity: 0.5
    };
    this.highlightedFeatureStyle = {
        weight: 5,
        color: '#666',
        dashArray: '',
        fillColor: DEFAULT_FILL_COLOR,
        fillOpacity: 0.7
    };

    this.makeMap = function(mapId){
        // Create the map object
        this.map = L.map(mapId, {
            center: [47, 2],
            zoom: 6,
            fadeAnimation: false,
	    preferCanvas: true,
	    renderer: L.canvas(),
        });

        // Load the background tiles
        this.addTileLayer();
    };

    this.renderView = function(){
        this.map.invalidateSize();
        this.map.fitBounds(this.geoJson.getBounds());
    };

    this.addTileLayer = function(){
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri',
        }).addTo(this.map);
    };

    this.setGeoJsonLayer = function(geoJsonData){
        if( this.geoJson ){
            this.map.removeLayer(this.geoJson);
        }
    
        this.geoJsonData = geoJsonData;
        this.geoJson = L.geoJson(geoJsonData, {
            style: angular.bind(this, this.getFeatureStyle),
            onEachFeature: angular.bind(this, this.onEachFeature),
        }).addTo(this.map);
    };

    this.extendFeatureStyle = function(feature, baseStyle) {
        var fillColor = this.getFillColor(feature) || DEFAULT_FILL_COLOR;
        return $.extend({}, baseStyle, {
            fillColor:  fillColor
        });
    };
    
    this.getFeatureStyle = function(feature) {
        return this.extendFeatureStyle(feature, this.baseFeatureStyle);
    };
    
    this.getHighlightedFeatureStyle = function(feature) {
        return this.extendFeatureStyle(feature, this.highlightedFeatureStyle);
    };
    

    this.getFillColor = function(feature) {
        throw "getFillColor not implemented";
    };

    this.onEachFeature = function(feature, layer) {
        layer.bindPopup(this.getPopupContent(feature));

        layer.on({
            mouseover: angular.bind(this, this.highlightFeature),
            mouseout: angular.bind(this, this.resetHighlight)
        });
    };
    
    this.getPopupContent = function(feature) {
        return feature.properties.name;
    };

    this.highlightFeature = function(event) {
        var layer = event.target;
        layer.setStyle(this.getHighlightedFeatureStyle(layer.feature));
        if (!L.Browser.ie && !L.Browser.opera) {
            layer.bringToFront();
        }
        layer.openPopup();
    };

    this.resetHighlight = function(event) {
        var layer = event.target;
        this.geoJson.resetStyle(layer);
        // It happens that the layer has no closePopup function, I've got no idea why.
        try{
            layer.closePopup();
        }
        catch(TypeError){
            // Whatever, it still works
        }
    };
};

var DynamicLeafletMap = function(getFillColorCallback){
    BaseLeafletMap.call(this);
    
    this.getFillColorCallback = getFillColorCallback;
    
    this.getFillColor = function(feature) {
        if( !this.getFillColorCallback){
            return null;
        }
        return this.getFillColorCallback({'geocode': feature.properties.geocode});
    };
};

var wattstratLeaflet = angular.module('ws.leaflet', ['ng.django.urls', 'wattstrat'])
.factory('dynamicGeoJsonUrl', function(djangoUrl){
    return djangoUrl.reverse('simulation:dynamic_geojson');
});

wattstratLeaflet.directive('wsDynamicMap', function($http, dynamicGeoJsonUrl, locale, geocodes){
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
            var leaflet = new DynamicLeafletMap(scope.getFillColor);
            leaflet.makeMap(mapId);
            
            function reloadLeaflet(){
                var selectedGeocodes = scope.selectedGeocodes;
                var remFirst = scope.removeFirst;
                var geoJsonUrl = null;
                var params = {};

                // TODO allgroups : concat the geocodes of all groups to get a geojson
                
                // Custom geocodes
                if( selectedGeocodes && ((selectedGeocodes.length > 1 && remFirst == "1") || (selectedGeocodes.length > 0 && remFirst != "1"))){
                    geoJsonUrl = dynamicGeoJsonUrl;
                    // Remove the country from the geocodes
		    var geocodesWithoutCountry=[];
		    if(remFirst == "1"){
			geocodesWithoutCountry = selectedGeocodes.slice(1)
		    }
		    else{
			geocodesWithoutCountry = selectedGeocodes;
		    }
                    params = {
                        geocodes: JSON.stringify(geocodesWithoutCountry)
                    };
                }
                // No geocodes except the country : just display the whole country
                else{
                    geoJsonUrl = '/static/geo/maps/' + locale.country + '/' + geocodes.country.geocode + '.geojson';
                }
            
                $http.get(geoJsonUrl, {
                    params: params,
                    cache: true
                })
                .success(function(geoJsonData){
                    leaflet.setGeoJsonLayer(geoJsonData);
                    leaflet.renderView();
                });
            }
            
            // Once geocodes are loaded, we can setup the map
            geocodes.dataPromise.then(function(){
                // First loading
                reloadLeaflet();
                // Update leaflet on geocodes changes
                scope.$watchCollection('selectedGeocodes', reloadLeaflet);
            });
            
        } 
    };
});
