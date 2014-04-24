'use strict';

angular.module('words', [
    'ngRoute',
    'ngResource',
    'words.filters',
    'words.services',
    'words.directives',
    'words.controllers'
]).config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('somepathhere', {
            templateUrl: 'partial/somepartial',
            controller: 'controller name here'
        });
        $routeProvider.otherwise({
            redirectTo: '/'
        });
    }]);