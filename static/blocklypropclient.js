/**
 * Created by michel on 11/05/16.
 */

var blocklyPropClientApp = angular.module('blocklyPropClientApp', []);

blocklyPropClientApp.controller('blocklyPropClientController', ['$scope', '$http', function($scope, $http) {
    $scope['booted'] = false;
    $scope['screen'] = 'boot';

    $scope['authform'] = {};

    $scope['log'] = function(message) {
        $http.post("log.do", $.param({'message': message}), {'headers' : {'Content-Type': 'application/x-www-form-urlencoded'}});
    };

    $scope['disconnect'] = function() {
        console.log("Disconnect");
        $http.post("disconnect.do", $.param({}), {'headers' : {'Content-Type': 'application/x-www-form-urlencoded'}});
    };

    $http.get('prelogin.json').then(function(response) {
        var data = response.data;
        $scope['authform']['login'] = data['login'];
        $scope['authform']['identifier'] = data['identifier'];

        $scope['stream-websocket'] = new StreamWebsocket($scope, data['stream-websocket']);

        $scope['screen'] = 'login';
        $scope['booted'] = true;

        $scope['log']('booted');
    });


    $scope.authenticate = function () {
        $scope['screen'] = 'connecting';
        console.log($scope['authform']['login']);

        $http.post('login.do', $.param($scope['authform']), {'headers' : {'Content-Type': 'application/x-www-form-urlencoded'}})

    };



}]);


