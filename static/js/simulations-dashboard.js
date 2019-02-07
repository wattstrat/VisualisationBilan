var angular, djangoUrl;


var simulationsDashboard = angular.module('simulationsDashboard', ['ng.django.urls', 'elif']);


function Simulation(simulation_data, djangoUrl){
    $.extend(this, simulation_data);
    
    this.get_results_url = function(){
	return window.location.href + this.shortid + '/';
    };
    this.get_download_url = function(){
	return window.location.href + this.shortid + '/downloads';
    };
    this.get_basic_download_url = function(){
	return window.location.href + this.shortid + '/basicsdownload/xlsx';
    };

}

simulationsDashboard.controller('DashboardCtrl', function($scope, $window, djangoUrl){
    var simulationDict = {};
    
    $scope.simulations = $.map($window.simulations, function(simulation_data){
        var simulation = new Simulation(simulation_data, djangoUrl);
        simulationDict[simulation.shortid] = simulation;
        return simulation;
    });

    this.updateSimulation = function(updatedSimulation){
        var simulation = simulationDict[updatedSimulation.shortid];
        if(simulation){
            $.extend(simulation, updatedSimulation);
        }
    };	
});


$(document).ready(function(){
    $("a[data-target='#removal'").click(function(event){
        $("#id_simulation").val($(event.target).attr('simulation-id'));
    });
});
