app.controller('ListDockersitecontainer', function ($scope, $http) {
    $scope.cyberPanelLoading = true;
    $scope.conatinerview = true;
    $('#cyberpanelLoading').hide();

    // Format bytes to human readable
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    $scope.getcontainer = function () {
        $('#cyberpanelLoading').show();
        url = "/docker/getDockersiteList";

        var data = {'name': $('#sitename').html()};
        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(ListInitialData, cantLoadInitialData);

        function ListInitialData(response) {
            $('#cyberpanelLoading').hide();
            if (response.data.status === 1) {
                $scope.cyberPanelLoading = true;
                var finalData = JSON.parse(response.data.data[1]);
                $scope.ContainerList = finalData;
                $("#listFail").hide();
            } else {
                $("#listFail").fadeIn();
                $scope.errorMessage = response.data.error_message;
            }
        }

        function cantLoadInitialData(response) {
            $scope.cyberPanelLoading = true;
            $('#cyberpanelLoading').hide();
            new PNotify({
                title: 'Operation Failed!',
                text: 'Connection disrupted, refresh the page.',
                type: 'error'
            });
        }
    };

    $scope.Lunchcontainer = function (containerid) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        var url = "/docker/getContainerAppinfo";

        var data = {
            'name': $('#sitename').html(),
            'id': containerid
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(ListInitialData, cantLoadInitialData);

        function ListInitialData(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();

            if (response.data.status === 1) {
                var containerInfo = response.data.data[1];
                
                // Find the container in the list and update its information
                for (var i = 0; i < $scope.ContainerList.length; i++) {
                    if ($scope.ContainerList[i].id === containerid) {
                        // Basic Information
                        $scope.ContainerList[i].status = containerInfo.status;
                        $scope.ContainerList[i].created = new Date(containerInfo.created);
                        $scope.ContainerList[i].uptime = containerInfo.uptime;

                        // Resource Usage
                        var memoryBytes = containerInfo.memory_usage;
                        $scope.ContainerList[i].memoryUsage = formatBytes(memoryBytes);
                        $scope.ContainerList[i].memoryUsagePercent = (memoryBytes / (1024 * 1024 * 1024)) * 100; // Assuming 1GB limit
                        $scope.ContainerList[i].cpuUsagePercent = (containerInfo.cpu_usage / 10000000000) * 100; // Normalize to percentage

                        // Network & Ports
                        $scope.ContainerList[i].ports = containerInfo.ports;

                        // Volumes
                        $scope.ContainerList[i].volumes = containerInfo.volumes;

                        // Environment Variables
                        $scope.ContainerList[i].environment = containerInfo.environment;
                        break;
                    }
                }

                // Get container logs
                $scope.getcontainerlog(containerid);
            } else {
                new PNotify({
                    title: 'Operation Failed!',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }

        function cantLoadInitialData(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            new PNotify({
                title: 'Operation Failed!',
                text: 'Connection disrupted, refresh the page.',
                type: 'error'
            });
        }
    };

    $scope.getcontainerlog = function (containerid) {
        $scope.cyberpanelLoading = false;
        var url = "/docker/getContainerApplog";

        var data = {
            'name': $('#sitename').html(),
            'id': containerid
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(ListInitialData, cantLoadInitialData);

        function ListInitialData(response) {
            $scope.cyberpanelLoading = true;
            $scope.conatinerview = false;
            $('#cyberpanelLoading').hide();
            
            if (response.data.status === 1) {
                // Find the container in the list and update its logs
                for (var i = 0; i < $scope.ContainerList.length; i++) {
                    if ($scope.ContainerList[i].id === containerid) {
                        $scope.ContainerList[i].logs = response.data.data[1];
                        break;
                    }
                }
            } else {
                new PNotify({
                    title: 'Operation Failed!',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }

        function cantLoadInitialData(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            $scope.conatinerview = false;
            new PNotify({
                title: 'Operation Failed!',
                text: 'Connection disrupted, refresh the page.',
                type: 'error'
            });
        }
    };

    // Auto-refresh container info every 30 seconds
    var refreshInterval;
    $scope.$watch('conatinerview', function(newValue, oldValue) {
        if (newValue === false) {  // When container view is shown
            refreshInterval = setInterval(function() {
                if ($scope.cid) {
                    $scope.Lunchcontainer($scope.cid);
                }
            }, 30000);  // 30 seconds
        } else {  // When container view is hidden
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        }
    });

    // Clean up on controller destruction
    $scope.$on('$destroy', function() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
    });

    // Initialize
    $scope.getcontainer();

    // Keep your existing functions
    $scope.recreateappcontainer = function() { /* ... */ };
    $scope.refreshStatus = function() { /* ... */ };
    $scope.restarthStatus = function() { /* ... */ };
    $scope.StopContainerAPP = function() { /* ... */ };
    $scope.cAction = function(action) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        var url = "/docker/";
        switch(action) {
            case 'start':
                url += "startContainer";
                break;
            case 'stop':
                url += "stopContainer";
                break;
            case 'restart':
                url += "restartContainer";
                break;
            default:
                console.error("Unknown action:", action);
                return;
        }

        var data = {
            'name': $('#sitename').html(),
            'container_id': $scope.selectedContainer.id
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(
            function(response) {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();

                if (response.data.status === 1) {
                    new PNotify({
                        title: 'Success!',
                        text: 'Container ' + action + ' successful.',
                        type: 'success'
                    });
                    
                    // Update container status after action
                    $scope.selectedContainer.status = action === 'stop' ? 'stopped' : 'running';
                    
                    // Refresh container info
                    $scope.Lunchcontainer($scope.selectedContainer.id);
                } else {
                    new PNotify({
                        title: 'Operation Failed!',
                        text: response.data.error_message || 'An unknown error occurred.',
                        type: 'error'
                    });
                }
            },
            function(error) {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                new PNotify({
                    title: 'Operation Failed!',
                    text: 'Connection disrupted or server error occurred.',
                    type: 'error'
                });
                
                console.error("Error during container action:", error);
            }
        );
    };

    // Update the container selection when actions are triggered
    $scope.setSelectedContainer = function(container) {
        $scope.selectedContainer = container;
    };

    // Update the button click handlers to set selected container
    $scope.handleAction = function(action, container) {
        $scope.setSelectedContainer(container);
        $scope.cAction(action);
    };

    $scope.openSettings = function(container) {
        $scope.selectedContainer = container;
        $('#settings').modal('show');
    };

    $scope.saveSettings = function() {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        var url = "/docker/updateContainerSettings";
        var data = {
            'name': $('#sitename').html(),
            'id': $scope.selectedContainer.id,
            'memoryLimit': $scope.selectedContainer.memoryLimit,
            'startOnReboot': $scope.selectedContainer.startOnReboot
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(ListInitialData, cantLoadInitialData);

        function ListInitialData(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();

            if (response.data.status === 1) {
                new PNotify({
                    title: 'Success!',
                    text: 'Container settings updated successfully.',
                    type: 'success'
                });
                $('#settings').modal('hide');
                // Refresh container info after update
                $scope.Lunchcontainer($scope.selectedContainer.id);
            } else {
                new PNotify({
                    title: 'Operation Failed!',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }

        function cantLoadInitialData(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            new PNotify({
                title: 'Operation Failed!',
                text: 'Connection disrupted, refresh the page.',
                type: 'error'
            });
        }
    };

    // Add location service to the controller for the n8n URL
    $scope.location = window.location;
});