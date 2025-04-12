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
            
            # Handle different operations
            if operation == 'create_backup':
                # For now, just return mock data to test UI functionality
                backup_options = data.get('options', {})
                include_credentials = backup_options.get('includeCredentials', True)
                include_executions = backup_options.get('includeExecutions', False)
                
                # In a real implementation, you would call the n8n API to create a backup
                # For now, simulate a successful backup
                
                return HttpResponse(json.dumps({
                    'status': 1,
                    'message': 'Backup simulation successful. In a production environment, this would download a backup file.',
                    # In real implementation, you would provide a download URL
                    # 'download_url': '/path/to/download/backup.json'
                }))
                
            elif operation == 'restore_backup':
                # For now, just return mock data to test UI functionality
                backup_data = data.get('backup_data')
                
                # In a real implementation, you would call the n8n API to restore from backup
                # For now, simulate a successful restore
                
                return HttpResponse(json.dumps({
                    'status': 1,
                    'message': 'Restore simulation successful.'
                }))
                
            else:
                return HttpResponse(json.dumps({
                    'status': 0,
                    'error_message': f'Unknown operation: {operation}'
                }))

        return HttpResponse('Not allowed')
    except Exception as e:
        return HttpResponse(json.dumps({
            'status': 0,
            'error_message': str(e)
        })) 