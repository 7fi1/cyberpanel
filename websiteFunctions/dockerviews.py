import json
import docker
from django.http import HttpResponse
from .models import DockerSites
from loginSystem.models import Administrator
from plogical.acl import ACLManager
from django.shortcuts import redirect
from loginSystem.views import loadLoginPage
from django.views.decorators.csrf import csrf_exempt
from plogical.CyberCPLogFileWriter import CyberCPLogFileWriter as logging
import datetime
import requests

def require_login(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            userID = request.session['userID']
            return view_func(request, *args, **kwargs)
        except KeyError:
            return redirect(loadLoginPage)
    return wrapper

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def get_container(self, container_id):
        try:
            return self.client.containers.get(container_id)
        except docker.errors.NotFound:
            return None
        except Exception as e:
            logging.writeToFile(f"Error getting container {container_id}: {str(e)}")
            return None

@csrf_exempt
@require_login
def startContainer(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)

            data = json.loads(request.body)
            container_id = data.get('container_id')
            site_name = data.get('name')

            # Verify Docker site ownership
            try:
                docker_site = DockerSites.objects.get(SiteName=site_name)
                if currentACL['admin'] != 1 and docker_site.admin != admin and docker_site.admin.owner != admin.pk:
                    return HttpResponse(json.dumps({
                        'status': 0,
                        'error_message': 'Not authorized to access this container'
                    }))
            except DockerSites.DoesNotExist:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Docker site not found'
                }))

            docker_manager = DockerManager()
            container = docker_manager.get_container(container_id)
            
            if not container:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Container not found'
                }))

            container.start()
            return HttpResponse(json.dumps({'status': 1}))

        return HttpResponse('Not allowed')
    except Exception as e:
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        }))

@csrf_exempt
@require_login
def stopContainer(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)

            data = json.loads(request.body)
            container_id = data.get('container_id')
            site_name = data.get('name')

            # Verify Docker site ownership
            try:
                docker_site = DockerSites.objects.get(SiteName=site_name)
                if currentACL['admin'] != 1 and docker_site.admin != admin and docker_site.admin.owner != admin.pk:
                    return HttpResponse(json.dumps({
                        'status': 0,
                        'error_message': 'Not authorized to access this container'
                    }))
            except DockerSites.DoesNotExist:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Docker site not found'
                }))

            docker_manager = DockerManager()
            container = docker_manager.get_container(container_id)
            
            if not container:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Container not found'
                }))

            container.stop()
            return HttpResponse(json.dumps({'status': 1}))

        return HttpResponse('Not allowed')
    except Exception as e:
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        }))

@csrf_exempt
@require_login
def restartContainer(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)

            data = json.loads(request.body)
            container_id = data.get('container_id')
            site_name = data.get('name')

            # Verify Docker site ownership
            try:
                docker_site = DockerSites.objects.get(SiteName=site_name)
                if currentACL['admin'] != 1 and docker_site.admin != admin and docker_site.admin.owner != admin.pk:
                    return HttpResponse(json.dumps({
                        'status': 0,
                        'error_message': 'Not authorized to access this container'
                    }))
            except DockerSites.DoesNotExist:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Docker site not found'
                }))

            docker_manager = DockerManager()
            container = docker_manager.get_container(container_id)
            
            if not container:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Container not found'
                }))

            container.restart()
            return HttpResponse(json.dumps({'status': 1}))

        return HttpResponse('Not allowed')
    except Exception as e:
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        }))

@csrf_exempt
@require_login
def n8n_container_operation(request):
    try:
        if request.method == 'POST':
            userID = request.session['userID']
            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)

            data = json.loads(request.body)
            container_id = data.get('container_id')
            operation = data.get('operation')
            
            # Get the container
            docker_manager = DockerManager()
            container = docker_manager.get_container(container_id)
            
            if not container:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Container not found'
                }))
            
            # Determine the port where n8n is running
            container_info = container.attrs
            port_bindings = container_info.get('HostConfig', {}).get('PortBindings', {})
            n8n_port = None
            
            for container_port, host_ports in port_bindings.items():
                if container_port.startswith('5678'):
                    n8n_port = host_ports[0]['HostPort']
                    break
            
            if not n8n_port:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Could not determine n8n port'
                }))
            
            # Extract the n8n API key from environment variables
            n8n_api_key = None
            environment_vars = container_info.get('Config', {}).get('Env', [])
            
            for env_var in environment_vars:
                if env_var.startswith('N8N_API_KEY='):
                    n8n_api_key = env_var.split('=', 1)[1]
                    break
            
            # If API key not found in environment variables, check if it's set to a default value
            if not n8n_api_key:
                n8n_api_key = 'n8n_api_123abc456def789'  # A common default, can be customized
                logging.writeToFile(f"No N8N_API_KEY found in container environment, using default")
            
            # Set up n8n API URL and headers
            host_ip = request.get_host().split(':')[0]
            n8n_base_url = f"http://{host_ip}:{n8n_port}/api/v1"
            
            headers = {
                'X-N8N-API-KEY': n8n_api_key,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Handle different operations
            if operation == 'create_backup':
                try:
                    # Get backup options from request
                    backup_options = data.get('options', {})
                    include_credentials = backup_options.get('includeCredentials', True)
                    include_executions = backup_options.get('includeExecutions', False)
                    
                    # Initialize the backup data dictionary
                    backup_data = {}
                    
                    # Fetch workflows with API key authentication
                    workflows_response = requests.get(
                        f"{n8n_base_url}/workflows", 
                        headers=headers
                    )
                    
                    if workflows_response.status_code == 200:
                        backup_data['workflows'] = workflows_response.json()
                    else:
                        error_message = workflows_response.text
                        logging.writeToFile(f"Failed to fetch n8n workflows: {workflows_response.status_code} - {error_message}")
                        return HttpResponse(json.dumps({
                            'status': 0,
                            'error_message': f'Failed to fetch workflows: {error_message}'
                        }))
                    
                    # Get credentials if requested
                    if include_credentials:
                        credentials_response = requests.get(
                            f"{n8n_base_url}/credentials", 
                            headers=headers
                        )
                        
                        if credentials_response.status_code == 200:
                            backup_data['credentials'] = credentials_response.json()
                        else:
                            error_message = credentials_response.text
                            logging.writeToFile(f"Failed to fetch n8n credentials: {credentials_response.status_code} - {error_message}")
                            # Don't fail the whole backup just because credentials failed
                    
                    # Get execution data if requested
                    if include_executions:
                        executions_response = requests.get(
                            f"{n8n_base_url}/executions", 
                            headers=headers
                        )
                        
                        if executions_response.status_code == 200:
                            backup_data['executions'] = executions_response.json()
                        else:
                            error_message = executions_response.text
                            logging.writeToFile(f"Failed to fetch n8n executions: {executions_response.status_code} - {error_message}")
                            # Don't fail the whole backup just because executions failed
                    
                    # Include metadata
                    backup_data['metadata'] = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'container_id': container_id,
                        'container_name': container.name,
                        'include_credentials': include_credentials,
                        'include_executions': include_executions
                    }
                    
                    # Create a response with the backup data
                    return HttpResponse(json.dumps({
                        'status': 1,
                        'message': 'Backup created successfully',
                        'backup': backup_data,
                        'filename': f'n8n-backup-{container.name}-{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
                    }))
                    
                except Exception as e:
                    logging.writeToFile(f"Error creating n8n backup: {str(e)}")
                    return HttpResponse(json.dumps({
                        'status': 0,
                        'error_message': f'Error creating backup: {str(e)}'
                    }))
                
            elif operation == 'restore_backup':
                try:
                    # Get backup data from request
                    backup_data = data.get('backup_data')
                    
                    if not backup_data:
                        return HttpResponse(json.dumps({
                            'status': 0,
                            'error_message': 'No backup data provided'
                        }))
                    
                    # Restore workflows
                    if 'workflows' in backup_data:
                        # First, get the list of existing workflows to avoid duplicates
                        existing_workflows_response = requests.get(
                            f"{n8n_base_url}/workflows", 
                            headers=headers
                        )
                        
                        if existing_workflows_response.status_code != 200:
                            error_message = existing_workflows_response.text
                            logging.writeToFile(f"Failed to fetch existing workflows: {existing_workflows_response.status_code} - {error_message}")
                            return HttpResponse(json.dumps({
                                'status': 0,
                                'error_message': f'Failed to fetch existing workflows: {error_message}'
                            }))
                        
                        existing_workflows = existing_workflows_response.json()
                        existing_workflow_names = {wf['name']: wf['id'] for wf in existing_workflows}
                        
                        # Now restore each workflow
                        for workflow in backup_data['workflows']:
                            # Remove ID from the backup data to create a new workflow
                            if 'id' in workflow:
                                workflow_id = workflow.pop('id')
                            
                            # Check if workflow with the same name already exists
                            if workflow['name'] in existing_workflow_names:
                                # Update existing workflow
                                update_response = requests.put(
                                    f"{n8n_base_url}/workflows/{existing_workflow_names[workflow['name']]}",
                                    headers=headers,
                                    json=workflow
                                )
                                
                                if update_response.status_code not in [200, 201]:
                                    error_message = update_response.text
                                    logging.writeToFile(f"Failed to update workflow: {update_response.status_code} - {error_message}")
                            else:
                                # Create new workflow
                                create_response = requests.post(
                                    f"{n8n_base_url}/workflows",
                                    headers=headers,
                                    json=workflow
                                )
                                
                                if create_response.status_code not in [200, 201]:
                                    error_message = create_response.text
                                    logging.writeToFile(f"Failed to create workflow: {create_response.status_code} - {error_message}")
                    
                    # Restore credentials if included in backup
                    if 'credentials' in backup_data:
                        # First, get existing credentials to avoid duplicates
                        existing_creds_response = requests.get(
                            f"{n8n_base_url}/credentials", 
                            headers=headers
                        )
                        
                        if existing_creds_response.status_code == 200:
                            existing_creds = existing_creds_response.json()
                            existing_cred_names = {cred['name']: cred['id'] for cred in existing_creds}
                            
                            # Now restore each credential
                            for credential in backup_data['credentials']:
                                # Remove ID from the backup data to create a new credential
                                if 'id' in credential:
                                    credential_id = credential.pop('id')
                                
                                # Check if credential with the same name already exists
                                if credential['name'] in existing_cred_names:
                                    # Update existing credential
                                    update_response = requests.put(
                                        f"{n8n_base_url}/credentials/{existing_cred_names[credential['name']]}",
                                        headers=headers,
                                        json=credential
                                    )
                                    
                                    if update_response.status_code not in [200, 201]:
                                        error_message = update_response.text
                                        logging.writeToFile(f"Failed to update credential: {update_response.status_code} - {error_message}")
                                else:
                                    # Create new credential
                                    create_response = requests.post(
                                        f"{n8n_base_url}/credentials",
                                        headers=headers,
                                        json=credential
                                    )
                                    
                                    if create_response.status_code not in [200, 201]:
                                        error_message = create_response.text
                                        logging.writeToFile(f"Failed to create credential: {create_response.status_code} - {error_message}")
                        else:
                            error_message = existing_creds_response.text
                            logging.writeToFile(f"Failed to fetch existing credentials: {existing_creds_response.status_code} - {error_message}")
                    
                    return HttpResponse(json.dumps({
                        'status': 1,
                        'message': 'Backup restored successfully'
                    }))
                
                except Exception as e:
                    logging.writeToFile(f"Error restoring n8n backup: {str(e)}")
                    return HttpResponse(json.dumps({
                        'status': 0,
                        'error_message': f'Error restoring backup: {str(e)}'
                    }))
                
            else:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': f'Unknown operation: {operation}'
                }))

        return HttpResponse('Not allowed')
    except Exception as e:
        logging.writeToFile(f"Error in n8n_container_operation: {str(e)}")
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        })) 