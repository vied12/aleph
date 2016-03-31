
aleph.controller('AppCtrl', ['$scope', '$rootScope', '$routeParams', '$window', '$location', '$route', '$http', '$modal', '$q',
                             'Flash', 'Session', 'Query', 'QueryContext', '$sce',
			     function($scope, $rootScope, $routeParams, $window, $location, $route, $http, $modal, $q, Flash, Session, Query, QueryContext) {
  $scope.session = {logged_in: false};
  $scope.query = Query;
  $scope.flash = Flash;
  $scope.sortorder = $scope.query.sort || ["best"];

  $scope.$watch('sortorder', function(){
      $scope.query.state.sort = $scope.sortorder;
      $scope.submitSearch();
      });

  window.scp = $scope;

  source_labels = {
	'sec-edgar': 'US stock exchange filings',
	'edgar-partial-content': 'US stock exchange filings',
	'rigzone': 'Industry news',
	'lse': 'London stock exchange',
	'johannesburg-exchange': 'Johannesburg stock exchange',
	'asx': 'Australian stock exchange',
	'sedar-partial-content': 'Canadian corporate filings',
	'singapore-exchange': 'Singapore stock exchange',
	'openoil-contracts': 'OpenOil contract collection',
    }



  $scope.sourceLabel = function(key){
      if(key in source_labels){
	    return source_labels[key]}
	return key;
    }
				 

				 
				 
  Session.get(function(session) {
    $scope.session = session;
  });

  $rootScope.$on("$routeChangeStart", function (event, next, current) {
    Session.get(function(session) {
      if (next.$$route && next.$$route.loginRequired && !session.logged_in) {
        $location.search({});
        $location.path('/');
      }
    });
    $scope.query.state = Query.load();
  });

  $rootScope.$on('$routeChangeSuccess', function() {
        var output=$location.path()+"?";
        angular.forEach($routeParams,function(value,key){
            output+=key+"="+value+"&";
        })
      output=output.substr(0,output.length-1);
      $window.ga('send', 'pageview', output);
    });

  $scope.suggestEntities = function(prefix) {
    var dfd = $q.defer();
    var opts = {params: {'prefix': prefix}, ignoreLoadingBar: true};
    $http.get('/api/1/entities/_suggest', opts).then(function(res) {
      dfd.resolve(res.data.results);
    });
    return dfd.promise;
  }

  $scope.acceptSuggestion = function($item) {
    $scope.query.state.q = '';
    Query.toggleFilter('entity', $item.id);
  }

  $scope.editProfile = function() {
    var d = $modal.open({
        templateUrl: 'profile.html',
        controller: 'ProfileCtrl',
        backdrop: true
    });
  };

  $scope.submitSearch = function(form) {
    $location.search($scope.query.state);
    if (Query.mode()) {
      $route.reload();
    } else {
      $location.path('/search');
    }
  };

  $scope.emailAlertButton = function(x){
    $http({
      url: '/api/1/alerts',
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      data: JSON.stringify({
	// XXX q is sometimes a string, sometimes an array, dunno why
	// so we have a flaky workaround
	'query': '' + $scope.query.state.q,
	'custom_label': 'Search for ' + $scope.query.state.q})
    }).success(function(data){
      console.log('added email alert');
    })
  }

  $scope.clearSearch = function(form) {
    var mode = Query.mode();
    Query.clear();
    if (mode == 'table') {
      $route.reload();
    } else {
      $location.path('/search');
    }
  };

}]);


aleph.controller('ProfileCtrl', ['$scope', '$location', '$modalInstance', '$http', 'Session',
  function($scope, $location, $modalInstance, $http, Session) {
  $scope.user = {};
  $scope.session = {};

  Session.get(function(session) {
    $scope.user = session.user;
    $scope.session = session;
  });

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.update = function(form) {
    var res = $http.post('/api/1/users/' + $scope.user.id, $scope.user);
    res.success(function(data) {
      $scope.user = data;
      $scope.session.user = data;
      $modalInstance.dismiss('ok');
    });
  };
}]);
