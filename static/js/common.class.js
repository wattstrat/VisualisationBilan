class AsyncData {
    constructor ($http, dataPromiseLocation=null, dataLocation=null) {
	this._dataPromiseLocation = dataPromiseLocation;
	this._dataLocation = dataLocation;
	this._http = $http;

	this._dataPromise = null;
	this._promiseData = null;
 
    }

    _setDataPromise(data) {
	this._promiseData = data;
    }
    
    get dataPromise() {
	if(this._dataPromiseLocation === null){
	    return Promise.resolve(null);
	}
	var self = this;
	return this._http.get(this._dataPromiseLocation).success(
	    function(data) {
		self._setDataPromise(data);
	    });
    }

    _req(viewValue, exclude){
	return {
	    method: 'POST',
	    url: this._dataLocation,
	    data: { 'typed': viewValue , 'exclude': exclude},
	    contentType: 'application/json; charset=utf-8',
	    dataType: 'text',
	};
    }

    match(viewValue, exclude=null) {
	if(this._dataLocation === null){
	    return [];
	}
	// format viewValue 
    	viewValue = viewValue.replace(/-/g, " ").latinize().toLowerCase();

	// request data from backend
	var req = this._req(viewValue, exclude);

	var matched = this._http(req).then(
	    function successCallback(response) {
		return response.data;
	    },
	    function errorCallback(response) {
	    return [];
	    }
	);
	return matched;	
    }
    static factory($http){
	return new AsyncData($http);
    }
}
AsyncData.factory.$inject = ["$http"];

class Geocodes extends AsyncData {
    constructor ($http, djangoUrl, locale) {
	super($http, "/static/geo/geocodes/" + locale.country + ".country.json", djangoUrl.reverse('simulation:gecodesfilter'))
	this.country = null;
	this.cGeocodes = {};
    }

    _setDataPromise(data) {
	this.country = data;
    }
    isProvinces(geocode){
	geocode = geocode.toLowerCase();
	return ((geocode.length == 7) && (geocode.startsWith('fr991')))
    }
    isCounties(geocode){
	geocode = geocode.toLowerCase();
	return ((geocode.length == 7) && (geocode.startsWith('fr992')))
    };
    isCities(geocode){
	geocode = geocode.toLowerCase();
	return ((geocode.length == 7) && (!geocode.startsWith('fr99')))
    };
    isGroups(geocode){
	geocode = geocode.toLowerCase();
	return geocode.startsWith('group_')
    }

    static factory($http, djangoUrl, locale){
	return new Geocodes($http, djangoUrl, locale);
    }

}
Geocodes.factory.$inject = ["$http", "djangoUrl", "locale"];

class ResultVariables extends AsyncData {
    constructor ($http, djangoUrl) {
	super($http, null, djangoUrl.reverse('simulation:resultvariablesfilter'))
    }
    
    static factory($http, djangoUrl){
	return new ResultVariables($http, djangoUrl);
    }

}
ResultVariables.factory.$inject = ["$http", "djangoUrl"];

class ParameterVariables extends AsyncData {

    constructor ($http, djangoUrl) {
	super($http, null, djangoUrl.reverse('simulation:parametervariablesfilter'))
    }
    
    static factory($http, djangoUrl){
	return new ParameterVariables($http, djangoUrl);
    }

}
ParameterVariables.factory.$inject = ["$http", "djangoUrl"];
