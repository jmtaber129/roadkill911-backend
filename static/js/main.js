var app = angular.module('roadkillApp', [
  'ngRoute'
]);

/**
 * Configure the Routes
 */
app.config(['$routeProvider', function ($routeProvider) {
  $routeProvider
    // Home
    .when("/", {templateUrl: "partials/home.html", controller: "PageCtrl"})
    // Pages
    .when("/register", 
      {
        templateUrl: "partials/register.html", 
        controller: "RegisterCtrl",
        resolve: {
          'roadkillApi': (roadkillService) => {
            return roadkillService.getApi();
          }
        }
      })
    .when("/view_report/:report_id", 
      {
        templateUrl: "partials/view_report.html", 
        controller: "ReportCtrl", 
        resolve: {
          'roadkillApi': (roadkillService) => {
            return roadkillService.getApi();
          }
        }
      })
    // else 404
    .otherwise("/404", {templateUrl: "partials/404.html", controller: "PageCtrl"});
}]);

app.controller('PageCtrl', ['$scope', function($scope) {
  $scope.foo = 'foo';
}]);

app.controller('RegisterCtrl', ['$scope', 'roadkillApi', function ($scope, roadkillApi) {
  $scope.submitted=false;
  $scope.submit = () => {
    $scope.submitted = false;
    roadkillApi.create_control_group({
      name: $scope.name,
      email: $scope.email,
      latitude: $scope.lat,
      longitude: $scope.lng,
      radius: $scope.radius,
      reporting_criteria: $scope.reporting_criteria,
    }).execute(resp => {
      $scope.$apply(() => {
        $scope.submitted = true;
      })
      console.log(resp);
    })
    //console.log($scope.name);
    //console.log($scope.email);
    //console.log($scope.reporting_criteria);
  }

  var map;
  $scope.lat = 33;
  $scope.lng = -101;
  $scope.radius = 10;
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 34.397, lng: -101.644},
    zoom: 6
  });
  var input = document.getElementById('pac-input');
  var searchBox = new google.maps.places.SearchBox(input);
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

  map.addListener('bounds_changed', function() {
    searchBox.setBounds(map.getBounds());
  });

  var marker;
  var circle;

  makeMarker = (pos) => {
    if (marker) {
      marker.setMap(null);
      circle.setMap(null);
    }
    marker = new google.maps.Marker({
      position: pos,
      map: map,
      draggable: true,
    });
    circle = new google.maps.Circle({
      map: map,
      radius: $scope.radius * 1609.3,    // 10 miles in metres
      fillColor: '#AA0000'
    });
    circle.bindTo('center', marker, 'position');
    
    marker.addListener('drag', () => {
      $scope.$apply(() => {
        $scope.lat = marker.position.lat();
        $scope.lng = marker.position.lng();
      })
    });
  }

  makeMarker({lat: $scope.lat, lng: $scope.lng});

  $scope.updateRadius = () => {
    if (marker) {
      circle.setRadius($scope.radius * 1609.3);
    }
  }

  map.addListener('click', (e) => {
    makeMarker(e.latLng);

    $scope.$apply(() => {
      $scope.lat = marker.position.lat();
      $scope.lng = marker.position.lng();
    });
    marker.addListener('drag', () => {
      $scope.$apply(() => {
        $scope.lat = marker.position.lat();
        $scope.lng = marker.position.lng();
      });
    });
  });
  // Listen for the event fired when the user selects a prediction and retrieve
  // more details for that place.
  searchBox.addListener('places_changed', function() {
    var places = searchBox.getPlaces();

    if (places.length == 0) {
      return;
    }

    // For each place, get the icon, name and location.
    var bounds = new google.maps.LatLngBounds();
    places.forEach(function(place) {
      if (!place.geometry) {
        console.log("Returned place contains no geometry");
        return;
      }

      // Create a marker for each place.
      makeMarker(place.geometry.location);

      if (place.geometry.viewport) {
        // Only geocodes have viewport.
        bounds.union(place.geometry.viewport);
      } else {
        bounds.extend(place.geometry.location);
      }
      $scope.$apply(() => {
        $scope.lat = place.geometry.location.lat();
        $scope.lng = place.geometry.location.lng();
      })

    });
    map.fitBounds(bounds);
  });
}]);

app.controller('ReportCtrl', ['$scope','$routeParams','roadkillApi', function ($scope, $routeParams, roadkillApi) {
  $scope.report_id = $routeParams.report_id;
  roadkillApi.roadkill({report_id: $routeParams.report_id}).execute((resp) => {
    console.log(resp);
    $scope.$apply(() => {
      $scope.report = resp;
    })
    
    var map = new google.maps.Map(document.getElementById('map'), {
      center: {lat: resp.latitude, lng: resp.longitude},
      zoom: 13
    }); 
    marker = new google.maps.Marker({
      position: {lat: resp.latitude, lng: resp.longitude},
      map: map,
    });
  });
}]);

app.factory('roadkillService', function() {
  return {
    getApi: () => {
      return new Promise((resolve) => {
        callback = () => {
          const api = gapi.client.roadkill;
          resolve(api);
        };
        gapi.client.load('roadkill', 'v1', callback, '//' + window.location.host + '/_ah/api');
      });
    }
  }
});

