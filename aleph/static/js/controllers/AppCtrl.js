aleph.controller('AppCtrl', ['$scope', '$rootScope', '$location', '$route', '$http', '$uibModal', '$q',
                             'Session', 'Query', 'Alert', 'Metadata',
    function($scope, $rootScope, $location, $route, $http, $uibModal, $q, Session, Query, Alert, Metadata) {

  $scope.session = {logged_in: false};
  $scope.query = Query;
  $scope.routeLoaded = false;
  $scope.routeFailed = false;
  $scope.$route = $route;

  Metadata.get().then(function(context) {
    $scope.metadata = context;
    $scope.session = context.session;
  });

  $rootScope.$on("$routeChangeStart", function (event, next, current) {
    Session.get().then(function(session) {
      if (next.$$route && next.$$route.loginRequired && !session.logged_in) {
        $location.search({});
        $location.path('/');
      }
    });
    $scope.query.state = Query.load();
    $scope.reportLoading(true);
  });

  $rootScope.$on("$routeChangeSuccess", function (event, next, current) {
    $scope.reportLoading(false);
  });

  $rootScope.$on("$routeChangeError", function (event, next, current) {
    $scope.routeFailed = true;
  });

  $rootScope.reportError = function(message) {
    $scope.routeFailed = true;
  };

  $rootScope.reportLoading = function(flag) {
    $scope.routeLoaded = !flag;
    if (flag) {
      $scope.routeFailed = false;
    }
  };

  $scope.editProfile = function($event) {
    $event.stopPropagation();
    var d = $uibModal.open({
        templateUrl: 'profile.html',
        controller: 'ProfileCtrl',
        backdrop: true
    });
  };

  $scope.manageAlerts = function($event) {
    $event.stopPropagation();
    var instance = $uibModal.open({
      templateUrl: 'alerts_manage.html',
      controller: 'AlertsManageCtrl',
      backdrop: true,
      size: 'md',
      resolve: {
        alerts: Alert.index()
      }
    });
  };

}]);
