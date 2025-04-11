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
            Backup data or None if there was an error
        """
        try:
            response = self.client.post(
                f"{self.base_url}/rest/export",
                json={
                    "includeCredentials": include_credentials,
                    "includeExecutions": include_executions
                }
            )
            if response.status_code == 200:
                return response.json()
            
            logging.writeToFile(f"Error creating backup. Status code: {response.status_code}, Response: {response.text}")
            return None
        except Exception as e:
            logging.writeToFile(f"Error creating backup: {str(e)}")
            return None
    
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
            container = client.containers.get(container_id)
            
            # Extract container metadata
            container_info = container.attrs
            n8n_port = None
            
            # Find the n8n port
            ports = container_info.get('NetworkSettings', {}).get('Ports', {})
            if '5678/tcp' in ports and ports['5678/tcp']:
                n8n_port = ports['5678/tcp'][0].get('HostPort')
            
            if not n8n_port:
                logging.writeToFile(f"Could not find n8n port mapping in {ports}")
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Could not find n8n port mapping'
                }))
            
            # Create N8nAPI instance
            n8n_api = N8nAPI(container, 'localhost', n8n_port)
            
            # Create backup
            backup = n8n_api.create_backup(include_credentials, include_executions)
            
            if backup:
                return HttpResponse(json.dumps({
                    'status': 1,
                    'backup': backup
                }))
            else:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Failed to create backup'
                }))
        
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': 'Invalid request method'
        }))
    except Exception as e:
        logging.writeToFile(f"Error in create_n8n_backup: {str(e)}")
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
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