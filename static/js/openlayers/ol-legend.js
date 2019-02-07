(function (root, factory) {
  if(typeof define === "function" && define.amd) {
      define("ol-legend", ["openlayers"], factory);
  } else if(typeof module === "object" && module.exports) {
      module.exports = factory(require("openlayers"));
  } else {
      root.olLegend = factory(root.ol);
  }
}(this, function(ol) {
    ol.control.Legend = function(opt_options) {

        var options = opt_options || {};

	this.cssClass = options.cssClass ?
            options.cssClass : 'ol-legend';

        var innerHTML = options.innerHTML ?
            options.innerHTML : '';

	var innerEls = options.innerEls ?
	    options.innerEls : [];

	this.enable= options.enable ?
	    options.enable : true;

	
        this.hiddenClassName = 'ol-unselectable ol-control ' + this.cssClass;
	
        if (ol.control.LayerSwitcher.isTouchDevice_()) {
            this.hiddenClassName += ' touch';
        }
        this.shownClassName = 'shown';
	this.hideClassName = 'hide';
	

        var element = document.createElement('div');
        element.className = this.hiddenClassName + ' ' + this.hideClassName;

	element.innerHTML = innerHTML;

	innerEls.forEach(function(el){
	    element.appendChild(el);
	});

        ol.control.Control.call(this, {
            element: element,
            target: options.target
        });

    };

    ol.inherits(ol.control.Legend, ol.control.Control);

    /**
     * Show the legend.
     */
    ol.control.Legend.prototype._show = function() {
	if(!this.element){
	    return;
	}
	if (!this.element.classList.contains(this.shownClassName)) {
	    this.element.classList.remove(this.hideClassName);
            this.element.classList.add(this.shownClassName);
        }
    }
    ol.control.Legend.prototype.show = function() {
	if(!this.enable){
	    return;
	}
	this._show();
    };

    /**
     * Hide the legend.
     */
    ol.control.Legend.prototype._hide = function() {
	if(!this.element){
	    return;
	}
        if (this.element.classList.contains(this.shownClassName)) {
	    this.element.classList.add(this.hideClassName);
            this.element.classList.remove(this.shownClassName);
        }
    }
    ol.control.Legend.prototype.hide = function() {
	if(!this.enable){
	    return;
	}
	this._hide();
    };

    /**
     * toogle the legend.
     */
    ol.control.Legend.prototype.toogle = function() {
	if(!this.enable){
	    return;
	}
        if (this.element.classList.contains(this.shownClassName)) {
	    this.element.classList.add(this.hideClassName);
            this.element.classList.remove(this.shownClassName);
        }
	else{
	    this.element.classList.add(this.shownClassName);
	    this.element.classList.remove(this.hideClassName);
	}
    };

    var Legend = ol.control.Legend;
    return Legend;
}));
