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
        self.container = container
        self.base_url = f"http://{host}:{port}"
        self.client = requests.Session()
    
    def get_workflows(self):
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
    
    def toggle_workflow_active(self, workflow_id, active):
        try:
            response = self.client.patch(f"{self.base_url}/rest/workflows/{workflow_id}/activate",
                                        json={"active": active})
            if response.status_code in [200, 201]:
                return True
            return False
        except Exception as e:
            logging.writeToFile(f"Error toggling workflow status: {str(e)}")
            return False
    
    def get_credentials(self):
        try:
            response = self.client.get(f"{self.base_url}/rest/credentials")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.writeToFile(f"Error fetching credentials: {str(e)}")
            return None
    
    def create_backup(self, include_credentials=True, include_executions=False):
        try:
            response = self.client.post(f"{self.base_url}/rest/export",
                                       json={
                                           "includeCredentials": include_credentials,
                                           "includeExecutions": include_executions
                                       })
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.writeToFile(f"Error creating backup: {str(e)}")
            return None
    
    def restore_backup(self, backup_data):
        try:
            response = self.client.post(f"{self.base_url}/rest/import",
                                       json=backup_data)
            if response.status_code in [200, 201]:
                return True
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
            
            # Toggle workflow status
            success = n8n_api.toggle_workflow_active(workflow_id, active)
            
            if success:
                return HttpResponse(json.dumps({
                    'status': 1,
                    'message': f"Workflow {'activated' if active else 'deactivated'} successfully"
                }))
            else:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Failed to update workflow status'
                }))
        
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': 'Invalid request method'
        }))
    except Exception as e:
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
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        })) 