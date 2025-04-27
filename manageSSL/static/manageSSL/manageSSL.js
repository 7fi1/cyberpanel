/**
 * Created by usman on 9/26/17.
 */


/* Java script code to issue SSL */
app.controller('sslIssueCtrl', function ($scope, $http) {

    $scope.sslIssueCtrl = true;
    $scope.manageSSLLoading = true;
    $scope.issueSSLBtn = true;
    $scope.canNotIssue = true;
    $scope.sslIssued = true;
    $scope.couldNotConnect = true;
    $scope.sslDetails = null;

    $scope.showbtn = function () {
        $scope.issueSSLBtn = false;
        $scope.fetchSSLDetails();
    };

    $scope.fetchSSLDetails = function() {
        if (!$scope.virtualHost) return;
        
        var url = "/manageSSL/getSSLDetails";
        var data = {
            virtualHost: $scope.virtualHost
        };
        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(function(response) {
            if (response.data.status === 1) {
                $scope.sslDetails = response.data;
            } else {
                $scope.sslDetails = null;
                new PNotify({
                    title: 'Error',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }, function(response) {
            $scope.sslDetails = null;
            new PNotify({
                title: 'Error',
                text: 'Could not fetch SSL details',
                type: 'error'
            });
        });
    };

    $scope.issueSSL = function () {
        $scope.manageSSLLoading = false;

        var url = "/manageSSL/issueSSL";
        var data = {
            virtualHost: $scope.virtualHost,
        };
        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(ListInitialDatas, cantLoadInitialDatas);

        function ListInitialDatas(response) {
            if (response.data.SSL == 1) {
                $scope.sslIssueCtrl = true;
                $scope.manageSSLLoading = true;
                $scope.issueSSLBtn = false;
                $scope.canNotIssue = true;
                $scope.sslIssued = false;
                $scope.couldNotConnect = true;
                $scope.sslDomain = $scope.virtualHost;
                $scope.fetchSSLDetails(); // Refresh SSL details after issuing
            } else {
                $scope.sslIssueCtrl = true;
                $scope.manageSSLLoading = true;
                $scope.issueSSLBtn = false;
                $scope.canNotIssue = false;
                $scope.sslIssued = true;
                $scope.couldNotConnect = true;
                $scope.errorMessage = response.data.error_message;
            }
        }

        function cantLoadInitialDatas(response) {
            $scope.sslIssueCtrl = true;
            $scope.manageSSLLoading = true;
            $scope.issueSSLBtn = false;
            $scope.canNotIssue = true;
            $scope.sslIssued = true;
            $scope.couldNotConnect = false;
        }
    };

});
/* Java script code to issue SSL ends here */

/* Java script code to issue SSL V2 */
app.controller('sslIssueCtrlV2', function ($scope, $http) {

    $scope.manageSSLLoading = true;
    $scope.sslDetails = null;

    $scope.showbtn = function () {
        $scope.issueSSLBtn = false;
        $scope.fetchSSLDetails();
    };

    $scope.fetchSSLDetails = function() {
        if (!$scope.virtualHost) return;
        
        var url = "/manageSSL/getSSLDetails";
        var data = {
            virtualHost: $scope.virtualHost
        };
        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(function(response) {
            if (response.data.status === 1) {
                $scope.sslDetails = response.data;
            } else {
                $scope.sslDetails = null;
                new PNotify({
                    title: 'Error',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }, function(response) {
            $scope.sslDetails = null;
            new PNotify({
                title: 'Error',
                text: 'Could not fetch SSL details',
                type: 'error'
            });
        });
    };

    $scope.issueSSL = function () {
        $scope.manageSSLLoading = false;

        var url = "/manageSSL/v2IssueSSL";
        var data = {
            virtualHost: $scope.virtualHost,
        };
        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(ListInitialDatas, cantLoadInitialDatas);

        function ListInitialDatas(response) {
            $scope.manageSSLLoading = true;
            if (response.data.SSL === 1) {
                $scope.sslStatus = 'Issued.';
                $scope.sslLogs = response.data.sslLogs;
                $scope.fetchSSLDetails(); // Refresh SSL details after issuing
            } else {
                $scope.sslStatus = 'Failed.';
                $scope.sslLogs = response.data.sslLogs;
            }
        }

        function cantLoadInitialDatas(response) {
            $scope.sslIssueCtrl = true;
            $scope.manageSSLLoading = true;
            $scope.issueSSLBtn = false;
            $scope.canNotIssue = true;
            $scope.sslIssued = true;
            $scope.couldNotConnect = false;
        }
    };
});
/* Java script code to issue SSL V2 ends here */


/* Java script code to issue SSL for hostname */
app.controller('sslIssueForHostNameCtrl', function ($scope, $http) {

    $scope.sslIssueCtrl = true;
    $scope.manageSSLLoading = true;
    $scope.issueSSLBtn = true;
    $scope.canNotIssue = true;
    $scope.sslIssued = true;
    $scope.couldNotConnect = true;

    $scope.showbtn = function () {
        $scope.issueSSLBtn = false;
    };


    $scope.issueSSL = function () {
        $scope.manageSSLLoading = false;

        var url = "/manageSSL/obtainHostNameSSL";


        var data = {
            virtualHost: $scope.virtualHost,
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(ListInitialDatas, cantLoadInitialDatas);


        function ListInitialDatas(response) {


            if (response.data.SSL == 1) {

                $scope.sslIssueCtrl = true;
                $scope.manageSSLLoading = true;
                $scope.issueSSLBtn = false;
                $scope.canNotIssue = true;
                $scope.sslIssued = false;
                $scope.couldNotConnect = true;

                $scope.sslDomain = $scope.virtualHost;


            } else {
                $scope.sslIssueCtrl = true;
                $scope.manageSSLLoading = true;
                $scope.issueSSLBtn = false;
                $scope.canNotIssue = false;
                $scope.sslIssued = true;
                $scope.couldNotConnect = true;
                $scope.errorMessage = response.data.error_message;

            }


        }

        function cantLoadInitialDatas(response) {
            $scope.sslIssueCtrl = true;
            $scope.manageSSLLoading = true;
            $scope.issueSSLBtn = false;
            $scope.canNotIssue = true;
            $scope.sslIssued = true;
            $scope.couldNotConnect = false;

        }


    };

});
/* Java script code to issue SSL for hostname */


/* Java script code to issue SSL for MailServer */
app.controller('sslIssueForMailServer', function ($scope, $http) {

    $scope.sslIssueCtrl = true;
    $scope.manageSSLLoading = true;
    $scope.issueSSLBtn = true;
    $scope.canNotIssue = true;
    $scope.sslIssued = true;
    $scope.couldNotConnect = true;

    $scope.showbtn = function () {
        $scope.issueSSLBtn = false;
    };


    $scope.issueSSL = function () {

        $scope.manageSSLLoading = false;

        var url = "/manageSSL/obtainMailServerSSL";


        var data = {
            virtualHost: $scope.virtualHost,
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(ListInitialDatas, cantLoadInitialDatas);


        function ListInitialDatas(response) {


            if (response.data.SSL === 1) {

                $scope.sslIssueCtrl = true;
                $scope.manageSSLLoading = true;
                $scope.issueSSLBtn = false;
                $scope.canNotIssue = true;
                $scope.sslIssued = false;
                $scope.couldNotConnect = true;

                $scope.sslDomain = $scope.virtualHost;


            } else {
                $scope.sslIssueCtrl = true;
                $scope.manageSSLLoading = true;
                $scope.issueSSLBtn = false;
                $scope.canNotIssue = false;
                $scope.sslIssued = true;
                $scope.couldNotConnect = true;
                $scope.errorMessage = response.data.error_message;

            }


        }

        function cantLoadInitialDatas(response) {
            $scope.sslIssueCtrl = true;
            $scope.manageSSLLoading = true;
            $scope.issueSSLBtn = false;
            $scope.canNotIssue = true;
            $scope.sslIssued = true;
            $scope.couldNotConnect = false;

        }


    };

});
/* Java script code to issue SSL for MailServer */