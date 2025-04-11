import json
import docker
from django.http import HttpResponse
from .models import DockerSites
from .website import ACLManager
from django.shortcuts import redirect
from plogical.CyberCPLogFileWriter import CyberCPLogFileWriter as logging

def loadLoginPage(request):
    return redirect('/login')

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

def require_login(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            userID = request.session['userID']
            return view_func(request, userID, *args, **kwargs)
        except KeyError:
            return redirect(loadLoginPage)
    return wrapper

@require_login
def startContainer(request, userID):
    try:
        data = json.loads(request.body)
        container_id = data.get('container_id')
        site_name = data.get('name')

        # Verify ownership
        docker_site = DockerSites.objects.get(SiteName=site_name)
        if not ACLManager.checkOwnership(docker_site.admin.domain, userID):
            return HttpResponse(json.dumps({'status': 0, 'error_message': 'Unauthorized access'}))

        # Get and start container
        docker_manager = DockerManager()
        container = docker_manager.get_container(container_id)
        
        if not container:
            return HttpResponse(json.dumps({'status': 0, 'error_message': 'Container not found'}))

        container.start()
        return HttpResponse(json.dumps({'status': 1}))

    except Exception as e:
        return HttpResponse(json.dumps({'status': 0, 'error_message': str(e)}))

@require_login
def stopContainer(request, userID):
    try:
        data = json.loads(request.body)
        container_id = data.get('container_id')
        site_name = data.get('name')

        # Verify ownership
        docker_site = DockerSites.objects.get(SiteName=site_name)
        if not ACLManager.checkOwnership(docker_site.admin.domain, userID):
            return HttpResponse(json.dumps({'status': 0, 'error_message': 'Unauthorized access'}))

        # Get and stop container
        docker_manager = DockerManager()
        container = docker_manager.get_container(container_id)
        
        if not container:
            return HttpResponse(json.dumps({'status': 0, 'error_message': 'Container not found'}))

        container.stop()
        return HttpResponse(json.dumps({'status': 1}))

    except Exception as e:
        return HttpResponse(json.dumps({'status': 0, 'error_message': str(e)}))

@require_login
def restartContainer(request, userID):
    try:
        data = json.loads(request.body)
        container_id = data.get('container_id')
        site_name = data.get('name')

        # Verify ownership
        docker_site = DockerSites.objects.get(SiteName=site_name)
        if not ACLManager.checkOwnership(docker_site.admin.domain, userID):
            return HttpResponse(json.dumps({'status': 0, 'error_message': 'Unauthorized access'}))

        # Get and restart container
        docker_manager = DockerManager()
        container = docker_manager.get_container(container_id)
        
        if not container:
            return HttpResponse(json.dumps({'status': 0, 'error_message': 'Container not found'}))

        container.restart()
        return HttpResponse(json.dumps({'status': 1}))

    except Exception as e:
        return HttpResponse(json.dumps({'status': 0, 'error_message': str(e)})) 