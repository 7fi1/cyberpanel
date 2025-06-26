# -*- coding: utf-8 -*-
from .views import VERSION, BUILD

def version_context(request):
    """Add version information to all templates"""
    return {
        'CYBERPANEL_VERSION': VERSION,
        'CYBERPANEL_BUILD': BUILD,
        'CYBERPANEL_FULL_VERSION': f"{VERSION}.{BUILD}"
    }