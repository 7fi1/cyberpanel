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
            
            # Set up n8n base URL
            host_ip = request.get_host().split(':')[0]
            
            # Try different authentication methods
            # Method 1: Try direct access to REST API (in some setups, this works without auth)
            direct_api_url = f"http://{host_ip}:{n8n_port}/rest"
            
            # Method 2: Try API v1 with various auth methods
            api_v1_url = f"http://{host_ip}:{n8n_port}/api/v1"
            
            # Extract authentication info from environment variables
            environment_vars = container_info.get('Config', {}).get('Env', [])
            
            # Initialize default headers
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Variables for auth info
            n8n_basic_auth_user = None
            n8n_basic_auth_password = None
            n8n_api_key = None
            n8n_jwt_auth = None
            
            # Extract auth information from environment variables
            for env_var in environment_vars:
                if env_var.startswith('N8N_API_KEY='):
                    n8n_api_key = env_var.split('=', 1)[1]
                elif env_var.startswith('N8N_BASIC_AUTH_USER='):
                    n8n_basic_auth_user = env_var.split('=', 1)[1]
                elif env_var.startswith('N8N_BASIC_AUTH_PASSWORD='):
                    n8n_basic_auth_password = env_var.split('=', 1)[1]
                elif env_var.startswith('N8N_JWT_AUTH_ACTIVE=') and 'true' in env_var.lower():
                    n8n_jwt_auth = True
                elif env_var.startswith('N8N_AUTH_ACTIVE=') and 'true' not in env_var.lower():
                    # If auth is explicitly disabled, we can use direct access
                    pass
            
            # Log the authentication methods available
            logging.writeToFile(f"N8N auth methods - API Key: {n8n_api_key is not None}, Basic Auth: {n8n_basic_auth_user is not None}, JWT: {n8n_jwt_auth is not None}")
            
            # Handle different operations
            if operation == 'create_backup':
                try:
                    # Get backup options from request
                    backup_options = data.get('options', {})
                    include_credentials = backup_options.get('includeCredentials', True)
                    include_executions = backup_options.get('includeExecutions', False)
                    
                    # Initialize the backup data dictionary
                    backup_data = {}
                    
                    # Try to fetch workflows using different authentication methods
                    workflows_response = None
                    auth = None
                    
                    # Try direct access first
                    try:
                        logging.writeToFile(f"Trying direct access to n8n REST API")
                        workflows_response = requests.get(f"{direct_api_url}/workflows", headers=headers, timeout=5)
                        if workflows_response.status_code == 200:
                            logging.writeToFile(f"Direct REST API access successful")
                            api_url = direct_api_url
                    except Exception as e:
                        logging.writeToFile(f"Direct REST API access failed: {str(e)}")
                    
                    # If direct access failed, try with API key
                    if not workflows_response or workflows_response.status_code != 200:
                        if n8n_api_key:
                            try:
                                logging.writeToFile(f"Trying API key authentication")
                                api_headers = headers.copy()
                                api_headers['X-N8N-API-KEY'] = n8n_api_key
                                workflows_response = requests.get(f"{api_v1_url}/workflows", headers=api_headers, timeout=5)
                                if workflows_response.status_code == 200:
                                    logging.writeToFile(f"API key authentication successful")
                                    api_url = api_v1_url
                                    headers = api_headers
                            except Exception as e:
                                logging.writeToFile(f"API key authentication failed: {str(e)}")
                    
                    # If API key failed, try basic auth
                    if not workflows_response or workflows_response.status_code != 200:
                        if n8n_basic_auth_user and n8n_basic_auth_password:
                            try:
                                logging.writeToFile(f"Trying basic authentication")
                                auth = (n8n_basic_auth_user, n8n_basic_auth_password)
                                workflows_response = requests.get(f"{api_v1_url}/workflows", headers=headers, auth=auth, timeout=5)
                                if workflows_response.status_code == 200:
                                    logging.writeToFile(f"Basic authentication successful")
                                    api_url = api_v1_url
                            except Exception as e:
                                logging.writeToFile(f"Basic authentication failed: {str(e)}")
                    
                    # If all authentication methods failed
                    if not workflows_response or workflows_response.status_code != 200:
                        # Last resort: try without any authentication at the Admin UI port
                        try:
                            logging.writeToFile(f"Trying Admin UI direct access")
                            admin_url = f"http://{host_ip}:{n8n_port}"
                            workflows_response = requests.get(f"{admin_url}/rest/workflows", headers=headers, timeout=5)
                            if workflows_response.status_code == 200:
                                logging.writeToFile(f"Admin UI direct access successful")
                                api_url = f"{admin_url}/rest"
                        except Exception as e:
                            logging.writeToFile(f"Admin UI direct access failed: {str(e)}")
                    
                    # Check if any method succeeded
                    if not workflows_response or workflows_response.status_code != 200:
                        error_message = "Failed to authenticate with n8n API. Please check the container logs for more information."
                        if workflows_response:
                            error_message = f"Authentication failed: {workflows_response.text}"
                        logging.writeToFile(f"All authentication methods failed: {error_message}")
                        return HttpResponse(json.dumps({
                            'status': 0,
                            'error_message': error_message
                        }))
                    
                    # If we made it here, one of the authentication methods worked
                    backup_data['workflows'] = workflows_response.json()
                    
                    # Get credentials if requested
                    if include_credentials:
                        try:
                            if auth:
                                credentials_response = requests.get(f"{api_url}/credentials", headers=headers, auth=auth, timeout=5)
                            else:
                                credentials_response = requests.get(f"{api_url}/credentials", headers=headers, timeout=5)
                            
                            if credentials_response.status_code == 200:
                                backup_data['credentials'] = credentials_response.json()
                            else:
                                logging.writeToFile(f"Failed to fetch n8n credentials: {credentials_response.status_code} - {credentials_response.text}")
                        except Exception as e:
                            logging.writeToFile(f"Error fetching credentials: {str(e)}")
                    
                    # Get execution data if requested
                    if include_executions:
                        try:
                            if auth:
                                executions_response = requests.get(f"{api_url}/executions", headers=headers, auth=auth, timeout=5)
                            else:
                                executions_response = requests.get(f"{api_url}/executions", headers=headers, timeout=5)
                            
                            if executions_response.status_code == 200:
                                backup_data['executions'] = executions_response.json()
                            else:
                                logging.writeToFile(f"Failed to fetch n8n executions: {executions_response.status_code} - {executions_response.text}")
                        except Exception as e:
                            logging.writeToFile(f"Error fetching executions: {str(e)}")
                    
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
                # Similar approach for restore operation...
                # Will implement the same authentication handling for restore operation
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': 'Restore operation temporarily unavailable while we update authentication methods'
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