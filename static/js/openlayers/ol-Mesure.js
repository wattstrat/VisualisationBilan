(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define(["openlayers"], factory);
  } else if(typeof module === "object" && module.exports) {
    module.exports = factory(require("openlayers"));
  } else {
    root.Mesure = factory(root.ol);
  }
}(this, function(ol) {
    ol.control.Mesure = function(opt_options) {
	var self = this;
        var options = opt_options || {};

	var tipLabel = options.tipLabel ?
            options.tipLabel : 'Mesure';

        this.hiddenClassName = 'ol-unselectable ol-control mesure';
        if (ol.control.LayerSwitcher.isTouchDevice_()) {
            this.hiddenClassName += ' touch';
        }
        this.shownClassName = 'shown';

        var element = document.createElement('div');
        element.className = this.hiddenClassName;

        var button = document.createElement('button');
        button.setAttribute('title', tipLabel);
        element.appendChild(button);



	/**
	 * Currently drawn feature.
	 * @type {ol.Feature}
	 */
	this.sketch = null;

	this.interaction = null;


        /**
	 * The help tooltip element.
	 * @type {Element}
	 */
	this.helpTooltipElement = null;


        /**
	 * Overlay to show the help messages.
	 * @type {ol.Overlay}
	 */
	this.helpTooltip = null;


        /**
	 * The measure tooltip element.
	 * @type {Element}
	 */
	this.measureTooltipElement = null;


        /**
	 * Overlay to show the measurement.
	 * @type {ol.Overlay}
	 */
	this.measureTooltip = null;


        /**
	 * Message to show when the user is drawing a polygon.
	 * @type {string}
	 */
	this.continuePolygonMsg = 'Click to continue drawing the polygon';


        /**
	 * Message to show when the user is drawing a line.
	 * @type {string}
	 */
	this.continueLineMsg = 'Click to continue drawing the line';


	this.sourceMesure = new ol.source.Vector();

	this.layerMesure = new ol.layer.Vector({
	    source: this.sourceMesure,
	    title: 'Mesure',
	    style: new ol.style.Style({
		fill: new ol.style.Fill({
		    color: 'rgba(255, 255, 255, 0.2)'
		}),
		stroke: new ol.style.Stroke({
		    color: '#ffcc33',
		    width: 2
		}),
		image: new ol.style.Circle({
		    radius: 7,
		    fill: new ol.style.Fill({
			color: '#ffcc33'
		    })
		})
	    })
	});


        /**
	 * Handle pointer move.
	 * @param {ol.MapBrowserEvent} evt The event.
	 */
	this.pointerMoveHandler = function(evt) {
	    if (evt.dragging) {
		return;
	    }
	    if(!self.helpTooltipElement){
		return;
	    }
	    /** @type {string} */
	    var helpMsg = 'Click to start drawing';

	    if (self.sketch) {
		var geom = (self.sketch.getGeometry());
		if (geom instanceof ol.geom.Polygon) {
		    helpMsg = self.continuePolygonMsg;
		} else if (geom instanceof ol.geom.LineString) {
		    helpMsg = self.continueLineMsg;
		}
	    }
	    
	    self.helpTooltipElement.innerHTML = helpMsg;
	    self.helpTooltip.setPosition(evt.coordinate);

	    self.helpTooltipElement.classList.remove('hidden');
	};

	/**
	 * Creates a new help tooltip
	 */
	var createHelpTooltip = function () {
	    if (self.helpTooltipElement) {
		self.helpTooltipElement.parentNode.removeChild(self.helpTooltipElement);
	    }
	    self.helpTooltipElement = document.createElement('div');
	    self.helpTooltipElement.className = 'mesure-tooltip hidden';
	    self.helpTooltip = new ol.Overlay({
		element: self.helpTooltipElement,
		offset: [15, 0],
		positioning: 'center-left'
	    });
	    self.getMap().addOverlay(self.helpTooltip);
	}


        /**
	 * Creates a new measure tooltip
	 */
	var createMeasureTooltip = function () {
	    if (self.measureTooltipElement) {
		self.measureTooltipElement.parentNode.removeChild(self.measureTooltipElement);
	    }
	    self.measureTooltipElement = document.createElement('div');
	    self.measureTooltipElement.className = 'mesure-tooltip tooltip-measure';
	    self.measureTooltip = new ol.Overlay({
		element: self.measureTooltipElement,
		offset: [0, -15],
		positioning: 'bottom-center'
	    });
	    self.getMap().addOverlay(self.measureTooltip);
	}

	/**
	 * Format length output.
	 * @param {ol.geom.LineString} line The line.
	 * @return {string} The formatted length.
	 */
	var formatLength = function(line) {
	    var length = ol.Sphere.getLength(line);
	    var output;
	    if (length > 100) {
		output = (Math.round(length / 1000 * 100) / 100) +
		    ' ' + 'km';
	    } else {
		output = (Math.round(length * 100) / 100) +
		    ' ' + 'm';
	    }
	    return output;
	};
	
	/**
	 * Format area output.
	 * @param {ol.geom.Polygon} polygon The polygon.
	 * @return {string} Formatted area.
	 */
	var formatArea = function(polygon) {
	    var area = ol.Sphere.getArea(polygon);
	    var output;
	    if (area > 10000) {
		output = (Math.round(area / 1000000 * 100) / 100) +
		    ' ' + 'km<sup>2</sup>';
	    } else {
		output = (Math.round(area * 100) / 100) +
		    ' ' + 'm<sup>2</sup>';
	    }
	    return output;
	};

	this.addInteraction = function(){
	    var type = null;
	    if (self.selector.value == 'area'){
		type = 'Polygon';
	    }
	    else if (self.selector.value == 'length'){
		type = 'LineString';
	    }
	    if (type == null)
		return;
	    self.interaction = new ol.interaction.Draw({
		source: self.sourceMesure,
		type: /** @type {ol.geom.GeometryType} */ (type),
		style: new ol.style.Style({
		    fill: new ol.style.Fill({
			color: 'rgba(255, 255, 255, 0.2)'
		    }),
		    stroke: new ol.style.Stroke({
			color: 'rgba(0, 0, 0, 0.5)',
			lineDash: [10, 10],
			width: 2
		    }),
		    image: new ol.style.Circle({
			radius: 5,
			stroke: new ol.style.Stroke({
			    color: 'rgba(0, 0, 0, 0.7)'
			}),
			fill: new ol.style.Fill({
			    color: 'rgba(255, 255, 255, 0.2)'
			})
		    })
		})
	    });
	    self.getMap().addInteraction(self.interaction);
	    
	    createMeasureTooltip();
	    createHelpTooltip();

	    var listener;
	    self.interaction.on('drawstart',
		    function(evt) {
			// set sketch
			self.sketch = evt.feature;

			/** @type {ol.Coordinate|undefined} */
			var tooltipCoord = evt.coordinate;

			listener = self.sketch.getGeometry().on('change', function(evt) {
			    var geom = evt.target;
			    var output;
			    if (geom instanceof ol.geom.Polygon) {
				output = formatArea(geom);
				tooltipCoord = geom.getInteriorPoint().getCoordinates();
			    } else if (geom instanceof ol.geom.LineString) {
				output = formatLength(geom);
				tooltipCoord = geom.getLastCoordinate();
			    }
			    self.measureTooltipElement.innerHTML = output;
			    self.measureTooltip.setPosition(tooltipCoord);
			});
		    }, self);

	    self.interaction.on('drawend',
		    function() {
			self.measureTooltipElement.className = 'mesure-tooltip tooltip-static';
			self.measureTooltip.setOffset([0, -7]);
			// unset sketch
			self.sketch = null;
			// unset tooltip so that a new one can be created
			self.measureTooltipElement = null;
			createMeasureTooltip();
			ol.Observable.unByKey(listener);
		    }, self);
	};

	this.createPanel = function(element) {
	    var opts = [{val:"none", text: "Aucune mesure"},{val: "length", text: "Longueur"}, {val:"area", text: "Aire"}];
            this.panel = document.createElement('div');
            this.panel.className = 'mesure-panel';
	    element.appendChild(this.panel);
	    this.selector = document.createElement('select');
	    this.panel.appendChild(this.selector);
	    this.selector.addEventListener('change', function(){
		self.getMap().removeInteraction(self.interaction);
		self.addInteraction();
		self.hidePanel();
	    });
	    
	    
	    opts.forEach(function(data) {
		var opt=document.createElement('option');
		opt.value=data.val;
		opt.innerHTML = data.text;
		self.selector.appendChild(opt);
	    });
	};
	


        button.onclick = function(e) {
            e = e || window.event;
            self.showPanel();
            e.preventDefault();
        };

        
	
	this.createPanel(element);
        element.appendChild(this.panel);
	this.panel.onmouseout = function(e) {
            e = e || window.event;
            if (!self.panel.contains(e.toElement || e.relatedTarget)) {
                self.hidePanel();
            }
        };

        ol.control.Control.call(this, {
            element: element,
            target: options.target
        });
	
    };

    ol.inherits(ol.control.Mesure, ol.control.Control);

    ol.control.Mesure.prototype.setMap = function(map) {
	ol.control.Control.prototype.setMap.call(this, map);
	map.addLayer(this.layerMesure);
	map.on('pointermove', this.pointerMoveHandler);

	var self=this;

	map.getViewport().addEventListener('mouseout', function() {
	    if(self.helpTooltipElement){
		self.helpTooltipElement.classList.add('hidden');
	    }
	});

	};
    /**
     * Show the layer panel.
     */
    ol.control.Mesure.prototype.showPanel = function() {
        if (!this.element.classList.contains(this.shownClassName)) {
            this.element.classList.add(this.shownClassName);
        }
    };

    /**
     * Hide the layer panel.
     */
    ol.control.Mesure.prototype.hidePanel = function() {
        if (this.element.classList.contains(this.shownClassName)) {
            this.element.classList.remove(this.shownClassName);
        }
    };
    
    /**
     * @private
     * @desc Determine if the current browser supports touch events. Adapted from
     * https://gist.github.com/chrismbarr/4107472
     */
    ol.control.Mesure.isTouchDevice_ = function() {
        try {
            document.createEvent("TouchEvent");
            return true;
        } catch(e) {
            return false;
        }
    };

    var Mesure = ol.control.Mesure;
    return Mesure;
}));
