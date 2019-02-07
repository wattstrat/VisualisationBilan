(function (root, factory) {
  if(typeof define === "function" && define.amd) {
      define(["openlayers"], factory);
  } else if(typeof module === "object" && module.exports) {
      module.exports = factory(require("openlayers"));
  } else {
      root.CenterMap = factory(root.ol, root.FileSaver);
  }
}(this, function(ol) {
    /**
     * OpenLayers v3/v4 CenterMap Control.
     * See [the examples](./examples) for usage.
     * @constructor
     * @extends {ol.control.Control}
     * @param {Object} opt_options Control options, extends olx.control.ControlOptions adding:
     *                              
     */
    ol.control.CenterMap = function(opt_options) {

        var options = opt_options || {};

        this.hiddenClassName = 'ol-unselectable ol-control ol-centermap';

        var element = document.createElement('div');
        element.className = this.hiddenClassName;
	
        var button = document.createElement('button');
	button.className = "btn btn-default";
	var center = document.createElement('i');
	center.className = "fa fa-thumb-tack";
	button.appendChild(center);
	button.setAttribute('title', "Center Map");
        element.appendChild(button);

        var self = this;

	button.onclick = function(e) {
	    e = e || window.event;
            e.preventDefault();
	    self.getMap().WSR.centerMap();
	    return false;
        };

        ol.control.Control.call(this, {
            element: element,
            target: options.target
        });

    };

    ol.inherits(ol.control.CenterMap, ol.control.Control);

    var CenterMap = ol.control.CenterMap;
    return CenterMap;
}));
