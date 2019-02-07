(function (root, factory) {
  if(typeof define === "function" && define.amd) {
      define(["openlayers", "FileSaver"], factory);
  } else if(typeof module === "object" && module.exports) {
      module.exports = factory(require("openlayers"), require("FileSaver"));
  } else {
      root.Download = factory(root.ol, root.FileSaver);
  }
}(this, function(ol, fs) {
    /**
     * OpenLayers v3/v4 Download Control.
     * See [the examples](./examples) for usage.
     * @constructor
     * @extends {ol.control.Control}
     * @param {Object} opt_options Control options, extends olx.control.ControlOptions adding:
     *                              
     */
    ol.control.Download = function(opt_options) {

        var options = opt_options || {};

	this._elmts = [];
	this._filename = "map.png"
        this.hiddenClassName = 'ol-unselectable ol-control ol-download';

        var element = document.createElement('div');
        element.className = this.hiddenClassName;
	
        var button = document.createElement('button');
	button.className = "btn btn-default";
	var dwl = document.createElement('i');
	dwl.className = "fa fa-download";
	button.appendChild(dwl);
	button.setAttribute('title', "Download PNG");
        element.appendChild(button);

        var self = this;

	button.onclick = function(e) {
	    e = e || window.event;
            e.preventDefault();
	    var bElements = self._elmts.slice();
	    self.dispatchEvent({type: "download:click", download: self});
	    self.getMap().once('postcompose', function(event) {
		var canvas = event.context.canvas;
		self._rasterizeElmts(canvas).then(function(canvasList) {
		    if (navigator.msSaveBlob) {
			navigator.msSaveBlob(canvas.msToBlob(), self._filename);
		    } else {
			canvas.toBlob(function(blob) {
			    // put backup element back
			    self._elmts = bElements
			    saveAs(blob, self._filename);
			});
		    }
		});
	    });
	    self.getMap().renderSync();
	    
        };

        ol.control.Control.call(this, {
            element: element,
            target: options.target
        });

    };

    ol.inherits(ol.control.Download, ol.control.Control);

    ol.control.Download.prototype._rasterizeElmts = function(canvas) {
	var self=this;
	return Promise.all(_.map(this._elmts,function(el) {return self._rasterizeElmt(el, canvas)}));
    };
    ol.control.Download.prototype._rasterizeElmt = function(elmt, canvas) {
        var style = elmt.style || '';
	var elmHTML = elmt.el ? elmt.el.outerHTML : (elmt.html || '');
	var html = style + elmHTML;
	console.log(html);
        var ret = rasterizeHTML.drawHTML(html).then(
            function (renderResult) {
                // Add legend
                var context = canvas.getContext('2d');
		//decalage
		var decH = elmt.decH || 0;
		var decW = elmt.decW || 0;
                var posH = canvas.height-renderResult.image.height+decH;
                var posW = canvas.width-renderResult.image.width + decW;
                context.drawImage(renderResult.image, posW, posH);
                return canvas;
            });
	return ret;
    };

    ol.control.Download.prototype.addElmt = function(elmt) {
	this._elmts.push(elmt);
    };
    ol.control.Download.prototype.setFilename = function(filename) {
	this._filename = filename;
    };

    var Download = ol.control.Download;
    return Download;
}));
