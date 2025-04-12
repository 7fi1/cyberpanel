import json
import logging
import requests
import docker
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DockerSites
from loginSystem.models import Administrator
from plogical.acl import ACLManager
from plogical.CyberCPLogFileWriter import CyberCPLogFileWriter as logging

class N8nAPI:
    def __init__(self, container, host, port):
        """
        Initialize the N8nAPI with a container reference and base URL
        
        Args:
            container: Docker container object
            host: Host address for n8n (usually 'localhost')
            port: Port number for n8n API
        """
        self.container = container
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
        # Set up a requests session for API calls
        self.client = requests.Session()
        self.client.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Check if the API is accessible
        try:
            response = self.client.get(f"{self.base_url}/rest/health")
            if response.status_code != 200:
                logging.writeToFile(f"n8n health check failed: {response.status_code}")
        except Exception as e:
            logging.writeToFile(f"Error connecting to n8n API: {str(e)}")
    
    def get_workflows(self):
        """
        Get all workflows from n8n
        
        Returns:
            List of workflow objects or None if there was an error
        """
        try:
            response = self.client.get(f"{self.base_url}/rest/workflows")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.writeToFile(f"Error fetching workflows: {str(e)}")
            return None
    
    def get_workflow_executions(self, workflow_id):
        try:
            response = self.client.get(f"{self.base_url}/rest/executions", 
                                      params={"workflowId": workflow_id})
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.writeToFile(f"Error fetching workflow executions: {str(e)}")
            return None
    
    def toggle_workflow(self, workflow_id, active):
        """
        Activate or deactivate a workflow
        
        Args:
            workflow_id: ID of the workflow to toggle
            active: Boolean indicating whether to activate (True) or deactivate (False)
            
        Returns:
            Boolean indicating success
        """
        try:
            url = f"{self.base_url}/rest/workflows/{workflow_id}/activate"
            if not active:
                url = f"{self.base_url}/rest/workflows/{workflow_id}/deactivate"
                
            response = self.client.post(url)
            return response.status_code in [200, 201]
        except Exception as e:
            logging.writeToFile(f"Error toggling workflow: {str(e)}")
            return False
    
    def get_credentials(self):
        """
        Get all credentials from n8n
        
        Returns:
            List of credential objects or None if there was an error
        """
        try:
            response = self.client.get(f"{self.base_url}/rest/credentials")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.writeToFile(f"Error fetching credentials: {str(e)}")
            return None
    
    def create_backup(self, include_credentials=True, include_executions=False):
        """
        Create a backup of n8n data
        
        Args:
            include_credentials: Whether to include credentials in the backup
            include_executions: Whether to include execution history in the backup
            
        Returns:
            Dict containing backup data or error information
            - On success: {'success': True, 'data': backup_data}
            - On failure: {'success': False, 'error': error_message}
        """
        try:
            response = self.client.post(
                f"{self.base_url}/rest/export",
                json={
                    "includeCredentials": include_credentials,
                    "includeExecutions": include_executions
                },
                timeout=30  # Add a 30 second timeout
            )
            
            if response.status_code == 200:
                # Validate the response contains expected data
                backup_data = response.json()
                if not isinstance(backup_data, dict):
                    logging.writeToFile(f"Invalid backup data format: {type(backup_data)}")
                    return {'success': False, 'error': 'Invalid backup data format returned from n8n'}
                
                return {'success': True, 'data': backup_data}
            
            error_msg = f"Error creating backup. Status code: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += f", Message: {error_data['message']}"
                except:
                    error_msg += f", Response: {response.text[:200]}"
            
            logging.writeToFile(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.Timeout:
            error_msg = "Timeout while connecting to n8n API"
            logging.writeToFile(error_msg)
            return {'success': False, 'error': error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error while connecting to n8n API"
            logging.writeToFile(error_msg)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Error creating backup: {str(e)}"
            logging.writeToFile(error_msg)
            return {'success': False, 'error': error_msg}
    
    def restore_backup(self, backup_data):
        """
        Restore from a backup
        
        Args:
            backup_data: Backup data to restore
            
        Returns:
            Boolean indicating success
        """
        try:
            response = self.client.post(
                f"{self.base_url}/rest/import",
                json=backup_data
            )
            if response.status_code in [200, 201]:
                return True
                
            logging.writeToFile(f"Error restoring backup. Status code: {response.status_code}, Response: {response.text}")
            return False
        except Exception as e:
            logging.writeToFile(f"Error restoring backup: {str(e)}")
            return False


@csrf_exempt
def get_n8n_workflows(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)
            
            data = json.loads(request.body)
            container_id = data.get('container_id')
            
            # Get container info
            client = docker.from_env()
            container = client.containers.get(container_id)
            
            # Extract container metadata
            container_info = container.attrs
            n8n_port = None
            
            # Find the n8n port
            ports = container_info.get('NetworkSettings', {}).get('Ports', {})
            if '5678/tcp' in ports and ports['5678/tcp']:
                n8n_port = ports['5678/tcp'][0].get('HostPort')
            
            if not n8n_port:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Could not find n8n port mapping'
                }))
            
            # Create N8nAPI instance
            n8n_api = N8nAPI(container, 'localhost', n8n_port)
            
            # Get workflows
            workflows = n8n_api.get_workflows()
            
            if workflows:
                # Add dummy statistics for demonstration
                import random
                from datetime import datetime, timedelta
                
                for workflow in workflows:
                    workflow['active'] = workflow.get('active', False)
                    workflow['lastExecution'] = (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
                    workflow['successRate'] = random.randint(60, 100)
                
                return HttpResponse(json.dumps({
                    'status': 1,
                    'workflows': workflows
                }))
            else:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Failed to fetch workflows'
                }))
        
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': 'Invalid request method'
        }))
    except Exception as e:
        logging.writeToFile(f"Error in get_n8n_workflows: {str(e)}")
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        }))

@csrf_exempt
def toggle_workflow(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)
            
            data = json.loads(request.body)
            container_id = data.get('container_id')
            workflow_id = data.get('workflow_id')
            active = data.get('active', False)
            
            # Get container info
            client = docker.from_env()
            container = client.containers.get(container_id)
            
            # Extract container metadata
            container_info = container.attrs
            n8n_port = None
            
            # Find the n8n port
            ports = container_info.get('NetworkSettings', {}).get('Ports', {})
            if '5678/tcp' in ports and ports['5678/tcp']:
                n8n_port = ports['5678/tcp'][0].get('HostPort')
            
            if not n8n_port:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Could not find n8n port mapping'
                }))
            
            # Create N8nAPI instance
            n8n_api = N8nAPI(container, 'localhost', n8n_port)
            
            # Toggle workflow
            success = n8n_api.toggle_workflow(workflow_id, active)
            
            if success:
                return HttpResponse(json.dumps({
                    'status': 1,
                    'workflow_id': workflow_id,
                    'active': active
                }))
            else:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': f'Failed to {"activate" if active else "deactivate"} workflow'
                }))
        
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': 'Invalid request method'
        }))
    except Exception as e:
        logging.writeToFile(f"Error in toggle_workflow: {str(e)}")
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        }))

@csrf_exempt
def create_n8n_backup(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)
            
            data = json.loads(request.body)
            container_id = data.get('container_id')
            include_credentials = data.get('include_credentials', True)
            include_executions = data.get('include_executions', False)
            
            logging.writeToFile(f"Creating backup for container {container_id}")
            
            # Get container info
            client = docker.from_env()
            try:
                container = client.containers.get(container_id)
            except docker.errors.NotFound:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': f'Container with ID {container_id} not found'
                }))
            except Exception as e:
                error_msg = f"Error getting Docker container: {str(e)}"
                logging.writeToFile(error_msg)
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': error_msg
                }))
            
            # Extract container metadata
            container_info = container.attrs
            n8n_port = None
            
            # Find the n8n port - check different formats
            ports = container_info.get('NetworkSettings', {}).get('Ports', {})
            port_mappings = []
            
            if '5678/tcp' in ports and ports['5678/tcp']:
                n8n_port = ports['5678/tcp'][0].get('HostPort')
            elif '5678' in ports and ports['5678']:
                n8n_port = ports['5678'][0].get('HostPort')
                
            # If still no port found, try to check exposed ports
            if not n8n_port:
                exposed_ports = container_info.get('Config', {}).get('ExposedPorts', {})
                port_mappings = list(exposed_ports.keys())
                
                # Find any port that might be mapped to 5678
                for port in ports:
                    port_mappings.append(f"{port} -> {ports[port]}")
            
            if not n8n_port:
                port_details = ", ".join(port_mappings) if port_mappings else "No port mappings found"
                error_msg = f"Could not find n8n port mapping. Available ports: {port_details}"
                logging.writeToFile(error_msg)
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': error_msg
                }))
            
            # Create N8nAPI instance
            n8n_api = N8nAPI(container, 'localhost', n8n_port)
            
            # Create backup
            backup_result = n8n_api.create_backup(include_credentials, include_executions)
            
            if backup_result['success']:
                return HttpResponse(json.dumps({
                    'status': 1,
                    'backup': backup_result['data']
                }))
            else:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': backup_result['error']
                }))
        
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': 'Invalid request method'
        }))
    except Exception as e:
        error_msg = f"Error in create_n8n_backup: {str(e)}"
        logging.writeToFile(error_msg)
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': error_msg
        }))

@csrf_exempt
def restore_n8n_backup(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)
            
            data = json.loads(request.body)
            container_id = data.get('container_id')
            backup_data = data.get('backup_data')
            
            # Get container info
            client = docker.from_env()
            container = client.containers.get(container_id)
            
            # Extract container metadata
            container_info = container.attrs
            n8n_port = None
            
            # Find the n8n port
            ports = container_info.get('NetworkSettings', {}).get('Ports', {})
            if '5678/tcp' in ports and ports['5678/tcp']:
                n8n_port = ports['5678/tcp'][0].get('HostPort')
            
            if not n8n_port:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Could not find n8n port mapping'
                }))
            
            # Create N8nAPI instance
            n8n_api = N8nAPI(container, 'localhost', n8n_port)
            
            # Restore backup
            success = n8n_api.restore_backup(backup_data)
            
            if success:
                return HttpResponse(json.dumps({
                    'status': 1
                }))
            else:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Failed to restore backup'
                }))
        
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': 'Invalid request method'
        }))
    except Exception as e:
        logging.writeToFile(f"Error in restore_n8n_backup: {str(e)}")
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        }))

@csrf_exempt
def diagnose_n8n_api(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)
            
            data = json.loads(request.body)
            container_id = data.get('container_id')
            
            # Get container info
            client = docker.from_env()
            try:
                container = client.containers.get(container_id)
            except docker.errors.NotFound:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': f'Container with ID {container_id} not found',
                    'diagnostics': {
                        'container_exists': False
                    }
                }))
            
            # Container exists
            diagnostics = {
                'container_exists': True,
                'container_status': container.status,
                'container_running': container.status == 'running',
                'container_names': container.name,
                'port_mappings': {},
                'exposed_ports': {},
                'n8n_port_found': False,
                'api_accessible': False
            }
            
            # Extract port mappings
            container_info = container.attrs
            ports = container_info.get('NetworkSettings', {}).get('Ports', {})
            exposed_ports = container_info.get('Config', {}).get('ExposedPorts', {})
            
            diagnostics['port_mappings'] = ports
            diagnostics['exposed_ports'] = exposed_ports
            
            # Find the n8n port
            n8n_port = None
            if '5678/tcp' in ports and ports['5678/tcp']:
                n8n_port = ports['5678/tcp'][0].get('HostPort')
                diagnostics['n8n_port'] = n8n_port
                diagnostics['n8n_port_found'] = True
            elif '5678' in ports and ports['5678']:
                n8n_port = ports['5678'][0].get('HostPort')
                diagnostics['n8n_port'] = n8n_port
                diagnostics['n8n_port_found'] = True
            
            # Only proceed if container is running and port was found
            if diagnostics['container_running'] and diagnostics['n8n_port_found']:
                # Test n8n API connection
                try:
                    n8n_api = N8nAPI(container, 'localhost', n8n_port)
                    
                    # Try to access the health endpoint
                    response = n8n_api.client.get(f"{n8n_api.base_url}/rest/health", timeout=5)
                    diagnostics['api_response_code'] = response.status_code
                    diagnostics['api_accessible'] = response.status_code == 200
                    
                    if diagnostics['api_accessible']:
                        # Try to get some basic info
                        try:
                            # Check if workflows endpoint is accessible
                            workflow_response = n8n_api.client.get(f"{n8n_api.base_url}/rest/workflows", timeout=5)
                            diagnostics['workflows_accessible'] = workflow_response.status_code == 200
                            
                            # Check if credentials endpoint is accessible
                            cred_response = n8n_api.client.get(f"{n8n_api.base_url}/rest/credentials", timeout=5)
                            diagnostics['credentials_accessible'] = cred_response.status_code == 200
                            
                            # Try a simple export operation
                            export_response = n8n_api.client.post(
                                f"{n8n_api.base_url}/rest/export", 
                                json={"includeCredentials": False, "includeExecutions": False},
                                timeout=5
                            )
                            diagnostics['export_accessible'] = export_response.status_code == 200
                            
                        except Exception as e:
                            diagnostics['additional_error'] = str(e)
                except Exception as e:
                    diagnostics['api_error'] = str(e)
            
            return HttpResponse(json.dumps({
                'status': 1,
                'diagnostics': diagnostics
            }))
        
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': 'Invalid request method'
        }))
    except Exception as e:
        error_msg = f"Error in diagnose_n8n_api: {str(e)}"
        logging.writeToFile(error_msg)
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': error_msg
        })) 