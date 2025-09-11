# -*- coding: utf-8 -*-
import json
import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from plogical.httpProc import httpProc
from .models import TestPluginSettings, TestPluginLog


@login_required
def plugin_home(request):
    """Main plugin page with inline integration"""
    try:
        # Get or create plugin settings
        settings, created = TestPluginSettings.objects.get_or_create(
            user=request.user,
            defaults={'plugin_enabled': True}
        )
        
        # Get recent logs
        recent_logs = TestPluginLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
        
        context = {
            'settings': settings,
            'recent_logs': recent_logs,
            'plugin_enabled': settings.plugin_enabled,
        }
        
        # Log page visit
        TestPluginLog.objects.create(
            user=request.user,
            action='page_visit',
            message='Visited plugin home page'
        )
        
        proc = httpProc(request, 'testPlugin/plugin_home.html', context, 'admin')
        return proc.render()
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})


@login_required
@require_http_methods(["POST"])
def test_button(request):
    """Handle test button click and show popup message"""
    try:
        settings, created = TestPluginSettings.objects.get_or_create(
            user=request.user,
            defaults={'plugin_enabled': True}
        )
        
        if not settings.plugin_enabled:
            return JsonResponse({
                'status': 0, 
                'error_message': 'Plugin is disabled. Please enable it first.'
            })
        
        # Increment test count
        settings.test_count += 1
        settings.save()
        
        # Create log entry
        TestPluginLog.objects.create(
            user=request.user,
            action='test_button_click',
            message=f'Test button clicked (count: {settings.test_count})'
        )
        
        # Prepare popup message
        popup_message = {
            'type': 'success',
            'title': 'Test Successful!',
            'message': f'{settings.custom_message} (Clicked {settings.test_count} times)',
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return JsonResponse({
            'status': 1,
            'popup_message': popup_message,
            'test_count': settings.test_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})


@login_required
@require_http_methods(["POST"])
def toggle_plugin(request):
    """Toggle plugin enable/disable state"""
    try:
        settings, created = TestPluginSettings.objects.get_or_create(
            user=request.user,
            defaults={'plugin_enabled': True}
        )
        
        # Toggle the state
        settings.plugin_enabled = not settings.plugin_enabled
        settings.save()
        
        # Log the action
        action = 'enabled' if settings.plugin_enabled else 'disabled'
        TestPluginLog.objects.create(
            user=request.user,
            action='plugin_toggle',
            message=f'Plugin {action}'
        )
        
        return JsonResponse({
            'status': 1,
            'enabled': settings.plugin_enabled,
            'message': f'Plugin {action} successfully'
        })
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})


@login_required
def plugin_settings(request):
    """Plugin settings page"""
    try:
        settings, created = TestPluginSettings.objects.get_or_create(
            user=request.user,
            defaults={'plugin_enabled': True}
        )
        
        context = {
            'settings': settings,
        }
        
        proc = httpProc(request, 'testPlugin/plugin_settings.html', context, 'admin')
        return proc.render()
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})


@login_required
@require_http_methods(["POST"])
def update_settings(request):
    """Update plugin settings"""
    try:
        settings, created = TestPluginSettings.objects.get_or_create(
            user=request.user,
            defaults={'plugin_enabled': True}
        )
        
        data = json.loads(request.body)
        custom_message = data.get('custom_message', settings.custom_message)
        
        settings.custom_message = custom_message
        settings.save()
        
        # Log the action
        TestPluginLog.objects.create(
            user=request.user,
            action='settings_update',
            message=f'Settings updated: custom_message="{custom_message}"'
        )
        
        return JsonResponse({
            'status': 1,
            'message': 'Settings updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})


@login_required
@require_http_methods(["POST"])
def install_plugin(request):
    """Install plugin (placeholder for future implementation)"""
    try:
        # Log the action
        TestPluginLog.objects.create(
            user=request.user,
            action='plugin_install',
            message='Plugin installation requested'
        )
        
        return JsonResponse({
            'status': 1,
            'message': 'Plugin installation completed successfully'
        })
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})


@login_required
@require_http_methods(["POST"])
def uninstall_plugin(request):
    """Uninstall plugin (placeholder for future implementation)"""
    try:
        # Log the action
        TestPluginLog.objects.create(
            user=request.user,
            action='plugin_uninstall',
            message='Plugin uninstallation requested'
        )
        
        return JsonResponse({
            'status': 1,
            'message': 'Plugin uninstallation completed successfully'
        })
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})


@login_required
def plugin_logs(request):
    """View plugin logs"""
    try:
        logs = TestPluginLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
        
        context = {
            'logs': logs,
        }
        
        proc = httpProc(request, 'testPlugin/plugin_logs.html', context, 'admin')
        return proc.render()
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})


@login_required
def plugin_docs(request):
    """View plugin documentation"""
    try:
        context = {}
        
        proc = httpProc(request, 'testPlugin/plugin_docs.html', context, 'admin')
        return proc.render()
        
    except Exception as e:
        return JsonResponse({'status': 0, 'error_message': str(e)})
