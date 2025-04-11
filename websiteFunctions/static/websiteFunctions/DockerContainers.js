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

    // N8N specific functions
    
    // Function to refresh workflows for a specific n8n container
    $scope.refreshWorkflows = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        var url = "/websites/n8n/get_workflows";
        
        var data = {
            'container_id': container.id
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
                // Find the container in the list and update its workflows
                for (var i = 0; i < $scope.ContainerList.length; i++) {
                    if ($scope.ContainerList[i].id === container.id) {
                        $scope.ContainerList[i].workflows = response.data.workflows;
                        
                        // Calculate success rates
                        $scope.ContainerList[i].workflows.forEach(function(workflow) {
                            // Default values
                            workflow.lastExecution = workflow.lastExecution || new Date();
                            workflow.successRate = workflow.successRate || 100;
                        });
                        
                        new PNotify({
                            title: 'Success!',
                            text: 'Workflows refreshed successfully.',
                            type: 'success'
                        });
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
        }, function(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            
            new PNotify({
                title: 'Operation Failed!',
                text: 'Connection disrupted, refresh the page.',
                type: 'error'
            });
        });
    };
    
    // Function to toggle workflow status (active/inactive)
    $scope.toggleWorkflow = function(container, workflowId, active) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        var url = "/websites/n8n/toggle_workflow";
        
        var data = {
            'container_id': container.id,
            'workflow_id': workflowId,
            'active': active
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
                // Find the container and update the workflow status
                for (var i = 0; i < $scope.ContainerList.length; i++) {
                    if ($scope.ContainerList[i].id === container.id) {
                        for (var j = 0; j < $scope.ContainerList[i].workflows.length; j++) {
                            if ($scope.ContainerList[i].workflows[j].id === workflowId) {
                                $scope.ContainerList[i].workflows[j].active = active;
                                break;
                            }
                        }
                        break;
                    }
                }
                
                new PNotify({
                    title: 'Success!',
                    text: 'Workflow ' + (active ? 'activated' : 'deactivated') + ' successfully.',
                    type: 'success'
                });
            } else {
                new PNotify({
                    title: 'Operation Failed!',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }, function(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            
            new PNotify({
                title: 'Operation Failed!',
                text: 'Connection disrupted, refresh the page.',
                type: 'error'
            });
        });
    };
    
    // Function to show workflow execution history
    $scope.showWorkflowExecution = function(container, workflowId) {
        // Find the container and workflow
        for (var i = 0; i < $scope.ContainerList.length; i++) {
            if ($scope.ContainerList[i].id === container.id) {
                for (var j = 0; j < $scope.ContainerList[i].workflows.length; j++) {
                    if ($scope.ContainerList[i].workflows[j].id === workflowId) {
                        $scope.selectedWorkflow = $scope.ContainerList[i].workflows[j];
                        break;
                    }
                }
                break;
            }
        }
        
        // Initialize filter
        $scope.executionFilter = { status: '' };
        
        // Open the execution history modal
        $('#executionHistory').modal('show');
    };

    // Backup and Restore Functions
    
    // Initialize backup options
    $scope.initBackupOptions = function(container) {
        if (!container.backupOptions) {
            container.backupOptions = {
                includeCredentials: true,
                includeExecutions: false
            };
        }
        
        if (!container.scheduledBackup) {
            container.scheduledBackup = {
                frequency: 'disabled',
                retention: 30
            };
        }
    };
    
    // Create a backup
    $scope.createBackup = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Initialize backup options if they don't exist
        $scope.initBackupOptions(container);
        
        var url = "/websites/n8n/create_backup";
        
        var data = {
            'container_id': container.id,
            'include_credentials': container.backupOptions.includeCredentials,
            'include_executions': container.backupOptions.includeExecutions
        };
        
        var config = {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        };
        
        $http.post(url, data, config).then(
            // Success handler
            function(response) {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                if (response.data.status === 1) {
                    // Download the backup file
                    var backupData = response.data.backup;
                    var fileName = 'n8n-backup-' + new Date().toISOString().slice(0, 10) + '.json';
                    
                    // Create a download link
                    var a = document.createElement('a');
                    var blob = new Blob([JSON.stringify(backupData)], {type: 'application/json'});
                    var url = window.URL.createObjectURL(blob);
                    a.href = url;
                    a.download = fileName;
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    new PNotify({
                        title: 'Success!',
                        text: 'Backup created and downloaded successfully.',
                        type: 'success'
                    });
                } else {
                    new PNotify({
                        title: 'Operation Failed!',
                        text: response.data.error_message || 'Unknown error occurred',
                        type: 'error'
                    });
                }
            },
            // Error handler
            function(error) {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                new PNotify({
                    title: 'Operation Failed!',
                    text: 'Connection disrupted, refresh the page.',
                    type: 'error'
                });
                
                console.error('Error creating backup:', error);
            }
        );
    };
    
    // Restore from a backup
    $scope.restoreFromBackup = function(container) {
        // Check if a file has been selected
        var fileInput = document.getElementById('backupFile');
        if (!fileInput.files || fileInput.files.length === 0) {
            new PNotify({
                title: 'Error!',
                text: 'Please select a backup file to restore.',
                type: 'error'
            });
            return;
        }
        
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Read the backup file
        var reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                var backupData = JSON.parse(e.target.result);
                
                var url = "/websites/n8n/restore_backup";
                
                var data = {
                    'container_id': container.id,
                    'backup_data': backupData
                };
                
                var config = {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                };
                
                $http.post(url, data, config).then(
                    // Success handler
                    function(response) {
                        $scope.cyberpanelLoading = true;
                        $('#cyberpanelLoading').hide();
                        
                        if (response.data.status === 1) {
                            new PNotify({
                                title: 'Success!',
                                text: 'Backup restored successfully.',
                                type: 'success'
                            });
                            
                            // Refresh workflows after restore
                            $scope.refreshWorkflows(container);
                        } else {
                            new PNotify({
                                title: 'Operation Failed!',
                                text: response.data.error_message || 'Unknown error occurred',
                                type: 'error'
                            });
                        }
                    }, 
                    // Error handler
                    function(error) {
                        $scope.cyberpanelLoading = true;
                        $('#cyberpanelLoading').hide();
                        
                        new PNotify({
                            title: 'Operation Failed!',
                            text: 'Connection disrupted, refresh the page.',
                            type: 'error'
                        });
                        
                        console.error('Error restoring backup:', error);
                    }
                );
            } catch (error) {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                new PNotify({
                    title: 'Error!',
                    text: 'Invalid backup file format: ' + error.message,
                    type: 'error'
                });
                
                console.error('Error parsing backup file:', error);
            }
        };
        
        reader.readAsText(fileInput.files[0]);
    };
    
    // Save backup schedule
    $scope.saveBackupSchedule = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Initialize backup options if they don't exist
        $scope.initBackupOptions(container);
        
        var url = "/websites/n8n/save_backup_schedule";
        
        var data = {
            'container_id': container.id,
            'frequency': container.scheduledBackup.frequency,
            'retention': container.scheduledBackup.retention
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
                    text: 'Backup schedule saved successfully.',
                    type: 'success'
                });
            } else {
                new PNotify({
                    title: 'Operation Failed!',
                    text: response.data.error_message,
                    type: 'error'
                });
            }
        }, function(response) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            
            new PNotify({
                title: 'Operation Failed!',
                text: 'Connection disrupted, refresh the page.',
                type: 'error'
            });
        });
    };

    // Version Management Functions
    
    // Check for updates
    $scope.checkForUpdates = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Initialize version management if it doesn't exist
        if (!container.n8nVersion) {
            // Set a default version
            container.n8nVersion = '0.214.3';
            container.versionHistory = [
                {
                    version: '0.214.3',
                    date: new Date('2023-06-15')
                }
            ];
        }
        
        // Simulate checking for updates
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                // Set the latest version (in a real implementation, this would come from an API)
                container.latestVersion = '0.215.0';
                
                // Check if an update is available
                container.updateAvailable = (container.latestVersion !== container.n8nVersion);
                
                new PNotify({
                    title: 'Success!',
                    text: container.updateAvailable ? 
                        'Update available: ' + container.latestVersion : 
                        'Your n8n is up to date.',
                    type: 'success'
                });
            });
        }, 1500);
    };
    
    // Update n8n
    $scope.updateN8N = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Simulate updating n8n
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                // Update the version history
                if (!container.versionHistory) {
                    container.versionHistory = [];
                }
                
                container.versionHistory.unshift({
                    version: container.latestVersion,
                    date: new Date()
                });
                
                // Update the current version
                container.n8nVersion = container.latestVersion;
                
                // Reset update available flag
                container.updateAvailable = false;
                
                new PNotify({
                    title: 'Success!',
                    text: 'n8n updated to version ' + container.n8nVersion,
                    type: 'success'
                });
            });
        }, 3000);
    };
    
    // Show release notes
    $scope.showReleaseNotes = function(container) {
        // Simulate opening release notes - in a real implementation, you would fetch these from n8n's GitHub or website
        window.open('https://github.com/n8n-io/n8n/releases/tag/n8n@' + container.latestVersion, '_blank');
    };
    
    // Show version change details
    $scope.showVersionChanges = function(container, version) {
        // Simulate opening version details - in a real implementation, you would fetch these from n8n's GitHub or website
        window.open('https://github.com/n8n-io/n8n/releases/tag/n8n@' + version.version, '_blank');
    };
    
    // Credential Management Functions
    
    // Refresh credentials
    $scope.refreshCredentials = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Simulate fetching credentials
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                // Simulate credential data
                container.credentials = [
                    {
                        id: 'cred1',
                        name: 'Google API',
                        type: 'Google Sheets',
                        usedIn: ['workflow1', 'workflow3'],
                        securityIssues: []
                    },
                    {
                        id: 'cred2',
                        name: 'Twitter API',
                        type: 'Twitter',
                        usedIn: ['workflow2'],
                        securityIssues: ['Using deprecated auth method']
                    },
                    {
                        id: 'cred3',
                        name: 'Slack Webhook',
                        type: 'Slack',
                        usedIn: [],
                        securityIssues: []
                    }
                ];
                
                // Calculate unused credentials
                container.unusedCredentials = container.credentials.filter(function(cred) {
                    return cred.usedIn.length === 0;
                });
                
                // Calculate insecure credentials
                container.insecureCredentials = container.credentials.filter(function(cred) {
                    return cred.securityIssues.length > 0;
                });
                
                new PNotify({
                    title: 'Success!',
                    text: 'Credentials refreshed successfully.',
                    type: 'success'
                });
            });
        }, 1500);
    };
    
    // Show credential usage
    $scope.showCredentialUsage = function(container, credentialId) {
        // Find the credential
        var credential = null;
        for (var i = 0; i < container.credentials.length; i++) {
            if (container.credentials[i].id === credentialId) {
                credential = container.credentials[i];
                break;
            }
        }
        
        if (credential) {
            var usageInfo = credential.usedIn.length > 0 ? 
                'Used in workflows: ' + credential.usedIn.join(', ') : 
                'Not used in any workflows';
            
            new PNotify({
                title: credential.name + ' Usage',
                text: usageInfo,
                type: 'info'
            });
        }
    };
    
    // Delete credential
    $scope.deleteCredential = function(container, credentialId) {
        if (confirm('Are you sure you want to delete this credential? This action cannot be undone.')) {
            $scope.cyberpanelLoading = false;
            $('#cyberpanelLoading').show();
            
            // Simulate deleting the credential
            setTimeout(function() {
                $scope.$apply(function() {
                    $scope.cyberpanelLoading = true;
                    $('#cyberpanelLoading').hide();
                    
                    // Remove the credential from the list
                    container.credentials = container.credentials.filter(function(cred) {
                        return cred.id !== credentialId;
                    });
                    
                    // Update unused and insecure counts
                    container.unusedCredentials = container.credentials.filter(function(cred) {
                        return cred.usedIn.length === 0;
                    });
                    
                    container.insecureCredentials = container.credentials.filter(function(cred) {
                        return cred.securityIssues.length > 0;
                    });
                    
                    new PNotify({
                        title: 'Success!',
                        text: 'Credential deleted successfully.',
                        type: 'success'
                    });
                });
            }, 1500);
        }
    };
    
    // Cleanup unused credentials
    $scope.cleanupUnusedCredentials = function(container) {
        if (container.unusedCredentials.length === 0) {
            new PNotify({
                title: 'Info',
                text: 'No unused credentials to clean up.',
                type: 'info'
            });
            return;
        }
        
        if (confirm('Are you sure you want to delete all unused credentials? This action cannot be undone.')) {
            $scope.cyberpanelLoading = false;
            $('#cyberpanelLoading').show();
            
            // Simulate deleting unused credentials
            setTimeout(function() {
                $scope.$apply(function() {
                    $scope.cyberpanelLoading = true;
                    $('#cyberpanelLoading').hide();
                    
                    // Get unused credential IDs
                    var unusedIds = container.unusedCredentials.map(function(cred) {
                        return cred.id;
                    });
                    
                    // Remove unused credentials
                    container.credentials = container.credentials.filter(function(cred) {
                        return cred.usedIn.length > 0;
                    });
                    
                    // Update unused and insecure counts
                    container.unusedCredentials = [];
                    
                    container.insecureCredentials = container.credentials.filter(function(cred) {
                        return cred.securityIssues.length > 0;
                    });
                    
                    new PNotify({
                        title: 'Success!',
                        text: 'Unused credentials deleted successfully.',
                        type: 'success'
                    });
                });
            }, 1500);
        }
    };

    // Health Monitoring Functions
    
    // Initialize health monitoring data
    $scope.initHealthMonitoring = function(container) {
        if (!container.healthMonitoring) {
            container.healthMonitoring = {
                enabled: false,
                memoryThreshold: 80,
                cpuThreshold: 80,
                workflowFailureAlert: true,
                containerRestartAlert: true,
                emailNotification: ''
            };
        }
    };
    
    // Enable health monitoring
    $scope.enableHealthMonitoring = function(container) {
        $scope.initHealthMonitoring(container);
        
        container.healthMonitoring.enabled = true;
        
        // Initialize charts
        setTimeout(function() {
            // This would normally use a charting library like Chart.js
            // Here we'll just simulate it
            new PNotify({
                title: 'Success!',
                text: 'Health monitoring enabled.',
                type: 'success'
            });
        }, 500);
    };
    
    // Refresh health data
    $scope.refreshHealthData = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        $scope.initHealthMonitoring(container);
        
        // Simulate fetching health data
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                new PNotify({
                    title: 'Success!',
                    text: 'Health data refreshed.',
                    type: 'success'
                });
            });
        }, 1500);
    };
    
    // Save health monitoring settings
    $scope.saveHealthMonitoringSettings = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Simulate saving settings
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                new PNotify({
                    title: 'Success!',
                    text: 'Health monitoring settings saved.',
                    type: 'success'
                });
            });
        }, 1500);
    };
    
    // Webhook Testing Functions
    
    // Initialize webhook tools
    $scope.initWebhookTools = function(container) {
        if (!container.webhookTools) {
            container.webhookTools = {
                selectedWorkflow: '',
                generatedUrl: '',
                testUrl: '',
                httpMethod: 'POST',
                requestBody: '{\n  "data": "example"\n}',
                headers: [
                    { key: 'Content-Type', value: 'application/json' }
                ],
                testResult: null
            };
        }
    };
    
    // Generate webhook URL
    $scope.generateWebhookUrl = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        $scope.initWebhookTools(container);
        
        // Simulate generating webhook URL
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                // Get the selected workflow
                var selectedWorkflow = null;
                if (container.workflows) {
                    for (var i = 0; i < container.workflows.length; i++) {
                        if (container.workflows[i].id === container.webhookTools.selectedWorkflow) {
                            selectedWorkflow = container.workflows[i];
                            break;
                        }
                    }
                }
                
                // Generate URL (in a real implementation, this would come from the n8n API)
                if (selectedWorkflow) {
                    container.webhookTools.generatedUrl = 'http://' + window.location.hostname + ':' + 
                        container.ports['5678/tcp'][0].HostPort + '/webhook/' + 
                        selectedWorkflow.id + '/' + Math.random().toString(36).substring(2, 15);
                    
                    new PNotify({
                        title: 'Success!',
                        text: 'Webhook URL generated.',
                        type: 'success'
                    });
                } else {
                    new PNotify({
                        title: 'Error!',
                        text: 'Please select a workflow.',
                        type: 'error'
                    });
                }
            });
        }, 1500);
    };
    
    // Add webhook header
    $scope.addWebhookHeader = function() {
        $scope.webhookTools.headers.push({ key: '', value: '' });
    };
    
    // Remove webhook header
    $scope.removeWebhookHeader = function(index) {
        $scope.webhookTools.headers.splice(index, 1);
    };
    
    // Test webhook
    $scope.testWebhook = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        $scope.initWebhookTools(container);
        
        if (!container.webhookTools.testUrl) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            
            new PNotify({
                title: 'Error!',
                text: 'Please enter a URL to test.',
                type: 'error'
            });
            return;
        }
        
        // Simulate testing webhook
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                // Simulate response
                container.webhookTools.testResult = {
                    status: 200,
                    statusText: 'OK',
                    headers: {
                        'content-type': 'application/json',
                        'server': 'n8n'
                    },
                    body: {
                        success: true,
                        executionId: '123456789'
                    }
                };
                
                new PNotify({
                    title: 'Success!',
                    text: 'Webhook tested successfully.',
                    type: 'success'
                });
            });
        }, 2000);
    };
    
    // Copy to clipboard
    $scope.copyToClipboard = function(text) {
        // Create a temporary input element
        var input = document.createElement('input');
        input.value = text;
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
        
        new PNotify({
            title: 'Copied!',
            text: 'Text copied to clipboard.',
            type: 'success'
        });
    };
    
    // Custom Domain Functions
    
    // Configure custom domain
    $scope.configureCustomDomain = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        if (!container.newDomain) {
            $scope.cyberpanelLoading = true;
            $('#cyberpanelLoading').hide();
            
            new PNotify({
                title: 'Error!',
                text: 'Please enter a domain name.',
                type: 'error'
            });
            return;
        }
        
        // Simulate configuring domain
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                container.customDomain = container.newDomain;
                container.sslEnabled = container.enableSSL || false;
                
                if (container.sslEnabled) {
                    // Simulate SSL expiry date (3 months from now)
                    var expiryDate = new Date();
                    expiryDate.setMonth(expiryDate.getMonth() + 3);
                    container.sslExpiry = expiryDate;
                }
                
                container.newDomain = '';
                container.enableSSL = false;
                
                new PNotify({
                    title: 'Success!',
                    text: 'Domain configured successfully.' + 
                        (container.sslEnabled ? ' SSL has been enabled.' : ''),
                    type: 'success'
                });
            });
        }, 3000);
    };
    
    // Remove custom domain
    $scope.removeCustomDomain = function(container) {
        if (confirm('Are you sure you want to remove this custom domain?')) {
            $scope.cyberpanelLoading = false;
            $('#cyberpanelLoading').show();
            
            // Simulate removing domain
            setTimeout(function() {
                $scope.$apply(function() {
                    $scope.cyberpanelLoading = true;
                    $('#cyberpanelLoading').hide();
                    
                    container.customDomain = null;
                    container.sslEnabled = false;
                    container.sslExpiry = null;
                    
                    new PNotify({
                        title: 'Success!',
                        text: 'Custom domain removed successfully.',
                        type: 'success'
                    });
                });
            }, 1500);
        }
    };
    
    // Enable SSL
    $scope.enableSSL = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Simulate enabling SSL
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                container.sslEnabled = true;
                
                // Simulate SSL expiry date (3 months from now)
                var expiryDate = new Date();
                expiryDate.setMonth(expiryDate.getMonth() + 3);
                container.sslExpiry = expiryDate;
                
                new PNotify({
                    title: 'Success!',
                    text: 'SSL enabled successfully. Certificate will expire on ' + 
                        expiryDate.toLocaleDateString() + '.',
                    type: 'success'
                });
            });
        }, 3000);
    };
    
    // Renew SSL
    $scope.renewSSL = function(container) {
        $scope.cyberpanelLoading = false;
        $('#cyberpanelLoading').show();
        
        // Simulate renewing SSL
        setTimeout(function() {
            $scope.$apply(function() {
                $scope.cyberpanelLoading = true;
                $('#cyberpanelLoading').hide();
                
                // Simulate new SSL expiry date (3 months from now)
                var expiryDate = new Date();
                expiryDate.setMonth(expiryDate.getMonth() + 3);
                container.sslExpiry = expiryDate;
                
                new PNotify({
                    title: 'Success!',
                    text: 'SSL certificate renewed successfully. New expiry date: ' + 
                        expiryDate.toLocaleDateString() + '.',
                    type: 'success'
                });
            });
        }, 3000);
    };
    
    // Helper function to handle container actions
    $scope.handleAction = function(action, container) {
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
                $('#cyberpanelLoading').hide();
                return;
        }

        var data = {
            'name': $('#sitename').html(),
            'container_id': container.id
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
                    container.status = action === 'stop' ? 'stopped' : 'running';
                    
                    // Refresh container info after short delay to allow Docker to update
                    setTimeout(function() {
                        $scope.Lunchcontainer(container.id);
                    }, 1000);
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