/**
 * Created by michel on 11/05/16.
 */
var blocklyPropClientApp = angular.module('blocklyPropClientApp', []);

blocklyPropClientApp.controller('blocklyPropClientController', ['$scope', '$http', function($scope, $http) {
    $scope['booted'] = false;
    $scope['screen'] = 'boot';

    $scope['authform'] = {};

    $http.get('prelogin.json').success(function(data) {
        $scope['authform']['login'] = data['login'];
        $scope['authform']['identifier'] = data['identifier'];

        $scope['screen'] = 'login';
        $scope['booted'] = true;
    });

    $scope.authenticate = function () {
        $scope['screen'] = 'connecting';
        console.log($scope['authform']['login']);

        $http.post('login.do', $.param($scope['authform']), {'headers' : {'Content-Type': 'application/x-www-form-urlencoded'}})

    };



}]);
