
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

      $scope.show_login_modal = function(){
	  var login_modal = $modal.open({
	      templateUrl: 'user/login_modal.html',
	      backdrop: true,
	      controller: function($scope, $modalInstance){
		  $scope.cancel = function(){
		      $modalInstance.dismiss('cancel');
		  };

		  $scope.handle_login = function(){
		      $modalInstance.close($('#login_modal'));
		  };
	      }

});
	  login_modal.result.then(
	      function(mdl){
		  var email = $(mdl).find('[name=email]').val();
		  var pw =  $(mdl).find('[name=password]').val();
		$http({
		    url: '/api/1/sessions/callback/ooemail',
		    method: 'GET', // XXX
		    params: {
			'email': email,
			'password': pw}
		}).success(function(data){
		    Flash.message('logged in', 'success');		    
		    window.scp.session.logged_in = true;
		}).error(function(data){
		    Flash.message('bad login', 'error');
		    });

},
	      function(){});
	  };
	      


      $scope.show_register_modal = function(){
	  var register_modal = $modal.open({
	      templateUrl: 'user/register_modal.html',
	      backdrop: true,
	      controller: function($scope, $modalInstance){
		  $scope.cancel = function(){
		      $modalInstance.dismiss('cancel');
		  };

		  $scope.handle_register = function(){
		      $modalInstance.close($('#register_modal'));
		  };
	      }

});
	  register_modal.result.then(
	      function(mdl){
		  var email = $(mdl).find('[name=email]').val();
		  var pw1 =  $(mdl).find('[name=password1]').val();
		  var pw2 =  $(mdl).find('[name=password2]').val();
		  console.log(email, pw1, pw2);
		  if(pw1 != pw2){
		      Flash.message('passwords do not match', 'error');
		      return;
		      }
		$http({
		    url: '/api/1/sessions/register/ooemail',
		    method: 'GET', // XXX
		    params: {
			'email': email,
			'pw': pw1}
		}).success(function(data){
		    Flash.message('Registered', 'success');		    
		    window.scp.session.logged_in = true;
		}).error(function(data){
		    Flash.message('bad registration details', 'error');
		    });

},
	      function(){});
	  };
	      


    $scope.emailAlertButton = function(){
	var emailModal = $modal.open({
        templateUrl: 'alert_create_form.html',
        controller: 'AlertCtrl',
        backdrop: true
    });
	emailModal.result.then(
	    function (formdata) {
		postdata = {
		    query: $scope.query.state.q[0],
		    custom_label: formdata['alert_label'],
		    checking_interval: formdata['alert_frequency'],
		    }
		$http({
		    url: '/api/1/alerts',
		    method: 'POST',
		    headers: {'Content-Type': 'application/json'},
		    data: JSON.stringify(postdata)
		}).success(function(data){
		    Flash.message('added email alert', 'success');
		})

	    },
	    function (result) {
	    }
	);

    };



 								 
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
	  console.log('scope update');
    var res = $http.post('/api/1/users/' + $scope.user.id, $scope.user);
    res.success(function(data) {
      $scope.user = data;
      $scope.session.user = data;
      $modalInstance.dismiss('ok');
    });
  };
}]);


aleph.controller('AlertCtrl', ['$scope', '$location', '$modalInstance', '$http', 'Session',
  function($scope, $location, $modalInstance, $http, Session) {
//aleph.controller('AlertCtrl', ['$scope', '$modalInstance',  function($scope, $modalInstance){
    var doodah = $scope;
    $scope.wtf = 'gah';
    
    $scope.cancel = function(){
	$modalInstance.dismiss('cancel');
	};
    $scope.emailAlertSubmit = function(form){
	var formdata = {}
	$.each($('[name=alertForm]').serializeArray(), function(i, field) {
	    formdata[field.name] = field.value;
	});
	$modalInstance.close(formdata);
	};
}]); 
