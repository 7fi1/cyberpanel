app.controller('DockerContainerManager', function ($scope, $http) {
    $scope.cyberpanelLoading = true;
    $scope.conatinerview = true;
    $scope.ContainerList = [];
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
                $scope.cyberpanelLoading = true;
                var finalData = JSON.parse(response.data.data[1]);
                $scope.ContainerList = finalData;
                $("#listFail").hide();
            } else {
                $("#listFail").fadeIn();
                $scope.errorMessage = response.data.error_message;
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

                        // N8N Stats
                        $scope.ContainerList[i].n8nStats = containerInfo.n8nStats || {
                            dbConnected: null,
                            activeWorkflows: 0,
                            queuedExecutions: 0,
                            lastExecution: null
                        };

                        // Load backups
                        $scope.refreshBackups($scope.ContainerList[i].id);
                        break;
                    }
                }
            }
        }

        function cantLoadInitialData(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            new PNotify({
                title: 'Operation Failed!',
                text: response.data.error_message || 'Could not connect to server',
                type: 'error'
            });
        }
    };

    $scope.createBackup = function(containerId) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();

        var url = "/docker/createBackup";
        var data = {
            'name': $('#sitename').html(),
            'id': containerId
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(function(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();

            if (response.data.status === 1) {
                // Refresh backups list
                $scope.refreshBackups(containerId);
                new PNotify({
                    title: 'Success!',
                    text: 'Backup created successfully.',
                    type: 'success'
                });
            } else {
                new PNotify({
                    title: 'Error!',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }, function(error) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            new PNotify({
                title: 'Error!',
                text: 'Could not connect to server.',
                type: 'error'
            });
        });
    };

    $scope.refreshBackups = function(containerId) {
        var url = "/docker/listBackups";
        var data = {
            'name': $('#sitename').html(),
            'id': containerId
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(function(response) {
            if (response.data.status === 1) {
                // Find the container and update its backups
                for (var i = 0; i < $scope.ContainerList.length; i++) {
                    if ($scope.ContainerList[i].id === containerId) {
                        $scope.ContainerList[i].backups = response.data.backups;
                        break;
                    }
                }
            }
        });
    };

    $scope.restoreBackup = function(containerId, backupId) {
        if (!confirm("Are you sure you want to restore this backup? The container will be stopped during restoration.")) {
            return;
        }

        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();

        var url = "/docker/restoreBackup";
        var data = {
            'name': $('#sitename').html(),
            'id': containerId,
            'backup_id': backupId
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(function(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();

            if (response.data.status === 1) {
                new PNotify({
                    title: 'Success!',
                    text: 'Backup restored successfully.',
                    type: 'success'
                });
                // Refresh container info
                $scope.Lunchcontainer(containerId);
            } else {
                new PNotify({
                    title: 'Error!',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }, function(error) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            new PNotify({
                title: 'Error!',
                text: 'Could not connect to server.',
                type: 'error'
            });
        });
    };

    $scope.deleteBackup = function(containerId, backupId) {
        if (!confirm("Are you sure you want to delete this backup?")) {
            return;
        }

        var url = "/docker/deleteBackup";
        var data = {
            'name': $('#sitename').html(),
            'id': containerId,
            'backup_id': backupId
        };

        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };

        $http.post(url, data, config).then(function(response) {
            if (response.data.status === 1) {
                new PNotify({
                    title: 'Success!',
                    text: 'Backup deleted successfully.',
                    type: 'success'
                });
                // Refresh backups list
                $scope.refreshBackups(containerId);
            } else {
                new PNotify({
                    title: 'Error!',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }, function(error) {
            new PNotify({
                title: 'Error!',
                text: 'Could not connect to server.',
                type: 'error'
            });
        });
    };

    $scope.downloadBackup = function(containerId, backupId) {
        window.location.href = "/docker/downloadBackup?name=" + encodeURIComponent($('#sitename').html()) + 
                             "&id=" + encodeURIComponent(containerId) + 
                             "&backup_id=" + encodeURIComponent(backupId);
    };

    $scope.openN8NEditor = function(container) {
        // Find the N8N port from the container's port bindings
        var n8nPort = null;
        if (container.ports) {
            for (var port in container.ports) {
                if (container.ports[port] && container.ports[port].length > 0) {
                    n8nPort = container.ports[port][0].HostPort;
                    break;
                }
            }
        }

        if (n8nPort) {
            window.open("http://localhost:" + n8nPort, "_blank");
        } else {
            new PNotify({
                title: 'Error!',
                text: 'Could not find N8N port configuration.',
                type: 'error'
            });
        }
    };

    $scope.getcontainerlog = function (containerid) {
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

        $http.post(url, data, config).then(function(response) {
            if (response.data.status === 1) {
                // Find the container and update its logs
                for (var i = 0; i < $scope.ContainerList.length; i++) {
                    if ($scope.ContainerList[i].id === containerid) {
                        $scope.ContainerList[i].logs = response.data.data[1];
                        break;
                    }
                }
            }
        });
    };
}); 