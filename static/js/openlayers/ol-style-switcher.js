(function (root, factory) {
  if(typeof define === "function" && define.amd) {
      define("ol-style-switcher", ["openlayers"], factory);
  } else if(typeof module === "object" && module.exports) {
      module.exports = factory(require("openlayers"));
  } else {
      root.olStyleSwitcher = factory(root.ol);
  }
}(this, function(ol) {
    ol.control.StyleSwitcher = function(opt_options) {

        var options = opt_options || {};

	this.cssClass = options.cssClass ?
            options.cssClass : 'ol-style-switcher';

        this.updateElement = options.updateElement ?
            options.updateElement : function() {return;};

	this.optSelector = options.selectors ?
	    options.selectors : [];

        this.hiddenClassName = 'ol-unselectable ol-control ' + this.cssClass;
	
        if (ol.control.LayerSwitcher.isTouchDevice_()) {
            this.hiddenClassName += ' touch';
        }
        this.shownClassName = 'shown';
	this.hideClassName = 'hide';

	var element = document.createElement('div');
        element.className = this.hiddenClassName + ' ' + this.hideClassName;

	this.sel = document.createElement('select');
	element.appendChild(this.sel);

	this.makeSelection();

	if(options.onChange){
	    this.sel.addEventListener('change', options.onChange);
	}
	
        ol.control.Control.call(this, {
            element: element,
            target: options.target
        });

    };

    ol.inherits(ol.control.StyleSwitcher, ol.control.Control);

    /**
     * Show the legend.
     */
    ol.control.StyleSwitcher.prototype.show = function() {
        if (!this.element.classList.contains(this.shownClassName)) {
	    this.element.classList.remove(this.hideClassName);
            this.element.classList.add(this.shownClassName);
        }
    };

    /**
     * Hide the legend.
     */
    ol.control.StyleSwitcher.prototype.hide = function() {
        if (this.element.classList.contains(this.shownClassName)) {
	    this.element.classList.add(this.hideClassName);
            this.element.classList.remove(this.shownClassName);
        }
    };

    /**
     * toogle the legend.
     */
    ol.control.StyleSwitcher.prototype.toogle = function() {
        if (this.element.classList.contains(this.shownClassName)) {
	    this.element.classList.add(this.hideClassName);
            this.element.classList.remove(this.shownClassName);
        }
	else{
	    this.element.classList.add(this.shownClassName);
	    this.element.classList.remove(this.hideClassName);
	}
    };
    ol.control.StyleSwitcher.prototype.makeSelection = function() {
	if(this.optSelector.length < 1){
	    return;
	}
	for(var ind = 0; ind < this.optSelector.length; ind++){
            var optionElement = document.createElement("option");
            optionElement.innerHTML = this.optSelector[ind].text;
	    optionElement.value = this.optSelector[ind].value;
	    this.updateElement(optionElement, this.optSelector[ind], ind, this.optSelector);
	    this.sel.appendChild(optionElement);
	}
    };
    
    ol.control.StyleSwitcher.prototype.clearSelection = function() {
	while(this.sel.firstChild){
	    this.sel.removeChild(this.sel.firstChild);
	}
    };

    ol.control.StyleSwitcher.prototype.setSelectors = function(selectors) {
	this.optSelector=selectors;
	this.clearSelection();
	this.makeSelection();
    }

    var StyleSwitcher = ol.control.StyleSwitcher;
    return StyleSwitcher;
}));
