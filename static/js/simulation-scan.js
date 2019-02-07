var angular;

var simulationAssessment = angular.module('simulationScan', [ 'ui.bootstrap', 'wattstrat', 'ws.leaflet'])
.factory('userinfoUrl', function(djangoUrl){
    return djangoUrl.reverse('accounts:userinfo');
});

/***************/
/* Controllers */
/***************/

simulationAssessment.controller('ScanCtrl', function($scope, geocodes, userinfo){
    $scope.geocodes = geocodes;
    $scope.selectedGeocodes = [];
    $scope.selectedGeocode = null;
    $scope.userinfo = userinfo;

    $scope.addGeocode = function(geocodes){

	if(geocodes.hasOwnProperty('includes')){
	    geocodes.includes.forEach(function(geocode){
		if($scope.selectedGeocodes.indexOf(geocode.geocode) < 0) {
		    $scope.selectedGeocodes.push(geocode.geocode);
		    $scope.geocodes.cGeocodes[geocode.geocode] = geocode;
		}
	    });
	}
	else{
	    if($scope.selectedGeocodes.indexOf(geocodes.geocode) < 0) {
		$scope.selectedGeocodes.push(geocodes.geocode);
		$scope.geocodes.cGeocodes[geocodes.geocode] = geocodes;
	    }
	}
    };

    $scope.removeGeocode = function(geocode){
        $scope.selectedGeocodes.splice($scope.selectedGeocodes.indexOf(geocode), 1);
    };
    
    $scope.csvGeocodes = function(){
        return $scope.selectedGeocodes.join(',');
    };
    
});
