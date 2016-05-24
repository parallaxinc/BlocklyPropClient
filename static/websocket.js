/**
 * Created by Michel on 24-5-2016.
 */

function StreamWebsocket($scope, url) {
    this.$scope = $scope;

    if (WebSocket) {
        // $scope['authform']['message'] = 'Websocket present';

        try {

            var connection = new WebSocket(url);

            connection.onopen = function () {
                connection.send(JSON.stringify({'code': 'connected'}))
            };

            connection.onerror = function (error) {

            };

            connection.onmessage = function (e) {
                console.log("New message: " + e);
            };
        } catch (e) {
            // $scope['authform']['message'] = e.message;
        }
    } else {
        // $scope['authform']['message'] = 'Websockets not available';

    }
  //  $scope.$apply();
}
