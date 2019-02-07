/*
 * Depends: + chroma.js
 *          + openlayers
 *          + ol.control.Legend
 */
(function (root, factory) {
  if(typeof define === "function" && define.amd) {
      define("ol-legend-scaledcolor", ["openlayers", "chroma", "ol-legend"], factory);
  } else if(typeof module === "object" && module.exports) {
      module.exports = factory(require("openlayers"), require("chroma"), require("ol-legend-scaledcolor"));
  } else {
      root.olLegendScaledColor = factory(root.ol, root.chroma, root.olLegend);
  }
}(this, function(ol, chroma, olLegend) {
    ol.control.LegendScaledColor = function(opt_options) {

        var options = opt_options || {};

	this.cssClass = options.cssClass ?
            options.cssClass : 'ol-legend-scaledcolor';

	var htmlTitle = options.title ?
            options.title : 'Légende';

	this.datas = options.datas ?
            options.datas : [];

	this.extract = options.extract ?
            options.extract : function(data){
		return data;
	    };

	this.formatData = options.formatData ?
            options.formatData : function(data, datas){
		return data;
	    };
	

	this.colorScaleConfig = options.colorScaleConfig ?
	    options.colorScaleConfig : {
		startColor: '#FFCC00',
		endColor: '#990000',
		steps: 10,
		colorSpace: 'lab'
	    };
	
	this.colorScale = null;
	
	// Title element
	this.title = document.createElement('div');
	this.title.className = this.cssClass + ' legend-title';
	this.title.innerHTML = htmlTitle;

	
	var innerEls = this.renderLegend();

        ol.control.Legend.call(this, {
            target: options.target,
	    cssClass: this.cssClass,
	    innerEls: innerEls,
        });

    };

    ol.inherits(ol.control.LegendScaledColor, ol.control.Legend);

    /**
     * Change title
     */
    ol.control.LegendScaledColor.prototype.setTitle = function(title) {
	if(title){
	    this.title.innerHTML = title;
	}
    };
    
    ol.control.LegendScaledColor.prototype.renderLegend = function() {
	var innerEls = []
	innerEls.push(this.title);
	this.makeColorScale(innerEls);
	return innerEls;
    };
    

    /**
     * Reset datas
     */
    ol.control.LegendScaledColor.prototype.setDatas = function(datas) {
	this.datas = datas
	this.removeLegendElements();
	var innerEls = this.renderLegend();
	var elParent = this.element;
	innerEls.forEach(function(el){
	    elParent.appendChild(el);
	});
    };

    /**
     * Remove all element of the legend
     */
    ol.control.LegendScaledColor.prototype.removeLegendElements = function() {
	while (this.element.firstChild) {
	    this.element.removeChild(this.element.firstChild);
	}
    };
    
    /**
     * Make element for the color scale
     */
    
    ol.control.LegendScaledColor.prototype.makeColorScale = function(innerElsP){
        var c = this.colorScaleConfig;
        var vals = [];

	this.colorScale = null;
        for( var indData=0; indData < this.datas.length; indData++ ) {
	    var val = this.extract(this.datas[indData]);
            if(val != null && val != undefined  && val>0){
		vals.push(val);
	    }
        }
	var steps = c.steps;

	if(vals.length == 0){
	    // Alway hide
	    this._hide();
	    return [];
	}
	else{
	    this.show();
	}
        if(vals.length < c.steps){
	    steps = vals.length;
	}
        var datalimits = chroma.limits(vals, 'q', steps);
        this.colorScale = chroma.scale([c.startColor,c.endColor]).classes(datalimits).mode(c.colorSpace);
	var innerEls = this.makeLegendElements(datalimits);
	if(innerElsP) {
	    innerElsP.push(innerEls);
	    return innerElsP;
	}
	return [innerEls];
    };

    ol.control.LegendScaledColor.prototype.makeLegendElements = function(datalimits){
        var div = document.createElement('div');
        div.className = this.cssClass + "-info " + this.cssClass;
	var from, to;
        for (var i = 0; i < datalimits.length-1; i++) {
            from = datalimits[i];
            to = datalimits[i + 1];
                
            if( to ){
                if(from == 0){
		    from += 1;
		}
		var el = document.createElement('div');
		el.className = this.cssClass + "-elm " + this.cssClass;
		var innerHTML = '<i style="background:' + this.colorScale(from) + '"></i>';
		innerHTML += ' <div class="'+ this.cssClass + "-elm-txt " + this.cssClass +'"> '
		innerHTML += this.formatData(from, this.datas);
		innerHTML += '&nbsp;&ndash;&nbsp;';
		innerHTML += this.formatData(to, this.datas);
		innerHTML += '</div>';
		el.innerHTML = innerHTML;
		div.appendChild(el);
	    }
	}
	return div;
    };
    
    var LegendScaledColor = ol.control.LegendScaledColor;
    return LegendScaledColor;
}));
