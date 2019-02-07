/* 
 * Depends: + Spin.js
 *          + ModalPopup.js
 */

(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define(["openlayers"], factory);
  } else if(typeof module === "object" && module.exports) {
    module.exports = factory(require("openlayers"));
  } else {
    root.LocationSearch = factory(root.ol);
  }
}(this, function(ol) {
ol.control.LocationSearch = function(opt){
    // Recherche d'adresse (nominatim)
    var options = opt || {};

    this.searchURL = options.searchURL ?
	options.searchURL : "https://nominatim.openstreetmap.org/";
    
    this.fromProj= options.searchProjection ?
	options.searchProjection : "EPSG:4326";

    this.searchParam = options.searchParam ?
	options.searchParam : function(searchQuery) {
	    return { format: "json", limit: 10, addressdetails:1, q: searchQuery};
	};
    this.filterData = options.filter ?
	options.filter : function(data) {
	    return true;
	};
    
    this.parseDatas = options.parseDatas ?
	option.parseDatas : function(datas){
	    return datas;
	};
    
    this.hiddenClassName = 'ol-unselectable ol-control location-search';
    if (ol.control.LayerSwitcher.isTouchDevice_()) {
        this.hiddenClassName += ' touch';
    }
    this.shownClassName = 'shown';

    // div that hold all LocationSearch Control
    var element = document.createElement('div');
    var txtSearch = document.createElement("input");
    txtSearch.type = "text";
    txtSearch.placeholder = "Entrez une adresse";
    
    var btnSearch = document.createElement('button');
    btnSearch.innerHTML = 'go';

    // show a spinning wheel icon
    var spinOpts = {
	lines: 13 // The number of lines to draw
	, scale: 1 // Scales overall size of the spinner
	, corners: 1 // Corner roundness (0..1)
	, color: '#000' // #rgb or #rrggbb or array of colors
	, opacity: 0.25 // Opacity of the lines
	, rotate: 0 // The rotation offset
	, direction: 1 // 1: clockwise, -1: counterclockwise
	, speed: 1 // Rounds per second
	, trail: 60 // Afterglow percentage
	, fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
	, zIndex: 2e9 // The z-index (defaults to 2000000000)
	, className: 'spinner' // The CSS class to assign to the spinner
	, top: '50%' // Top position relative to parent
	, left: '50%' // Left position relative to parent
	, shadow: false // Whether to render a shadow
	, hwaccel: false // Whether to use hardware acceleration
	, position: 'absolute' // Element positioning
    }
    var spinner = new Spinner(spinOpts).spin(element);
    spinner.stop()
    
    var self = this;
    var CenterBBOX = function(bbox, fromProj){
	var extent = [parseFloat(bbox[2]),parseFloat(bbox[0]),parseFloat(bbox[3]),parseFloat(bbox[1])]
	var view = self.getMap().getView();
	var currentProjection = view.getProjection().getCode();
	view.fit(ol.proj.transformExtent(extent, fromProj, currentProjection), {duration: 1000, maxZoom:19})
    }
    var search = function(e) {
	if(txtSearch.value.length==0){
	    return;
	}
	
	// URL config for nominatim
	
	// create a DOM to select good address
	var createPopupSelection = function(datas){
	    var options=document.createElement('div');
	    var counter = 0;
	    datas.forEach(function(data) {
		var opt=document.createElement('div');
		var inp=document.createElement('input');
		opt.appendChild(inp);
		inp.type = 'radio';
		inp.id = 'locationsearch-opt-' + counter++;
		inp.name = 'location-search';
		inp.value=data.display_name;
		inp.onclick = function(){
		    CenterBBOX(data.boundingbox, self.fromProj);
		};
		var label=document.createElement('label');
		opt.appendChild(label);
		label.setAttribute("for", inp.id);
		label.innerHTML = data.display_name;
		options.appendChild(opt);
		
		
	    });
	    return options;
	}
	
	spinner.spin(element);
	var jqxhr = $.get(self.searchURL , self.searchParam(txtSearch.value))
	    .done(function(data) {
		datas = self.parseDatas(data);
		fDatas = [];
		datas.forEach(function(data) {
		if(self.filterData(data))
		    fDatas.push(data);
		});
		    
		if(fDatas.length>1){
		    // more than 1 result
		    // handle Fullscreen mode
		    var fullScreenOff = document.getElementsByClassName("ol-full-screen-true");
		    if (fullScreenOff.length > 0){
			// should be juste One...
			// disable fullscreen
			fullScreenOff[0].click();
		    }
		    var optionsSel = createPopupSelection(fDatas);
		    app.ModalPopup("Choix de l'adresse", optionsSel);
		}
		else if(fDatas.length == 1){
		    // juste one
		    CenterBBOX(fDatas[0].boundingbox, self.fromProj);
		}
		else{
		    // no results
		    var noData=document.createElement('p');
		    noData.innerHTML = "Pas d'adresse trouvée";
		    app.ModalPopup("Erreur", noData);
		}
	    })
	    .fail(function() {
		// error in request
		var errorReq=document.createElement('p');
		errorReq.innerHTML = "Une erreur s'est produite lors de la requête.<br />Merci de réessayer plus tard.";
		app.ModalPopup("Erreur", errorReq);
	    })
	    .always(function() {
		// always disable spinning wheel
		spinner.stop()
	    });
    };

    var searchOnEnter = function(event){
    	if (event.which === 13) {
    	    search(event);
    	}
    };

    btnSearch.addEventListener('click', search, false);
    btnSearch.addEventListener('touchstart', search, false);
    txtSearch.addEventListener('keyup', searchOnEnter, false);
    
    element.className = this.hiddenClassName;    
    element.appendChild(txtSearch);
    element.appendChild(btnSearch);
    
    ol.control.Control.call(this, {
	element: element,
	target: options.target
    });
    
};
 
    ol.inherits(ol.control.LocationSearch, ol.control.Control);

    var LocationSearch = ol.control.LocationSearch;
    return LocationSearch;

}));
