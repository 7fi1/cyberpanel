from django.urls import path
from . import views, api

urlpatterns = [
    # Main AI Scanner pages
    path('', views.aiScannerHome, name='aiScannerHome'),
    path('setup-payment/', views.setupPayment, name='aiScannerSetupPayment'),
    path('setup-complete/', views.setupComplete, name='aiScannerSetupComplete'),
    path('start-scan/', views.startScan, name='aiScannerStartScan'),
    path('refresh-balance/', views.refreshBalance, name='aiScannerRefreshBalance'),
    path('add-payment-method/', views.addPaymentMethod, name='aiScannerAddPaymentMethod'),
    path('payment-method-complete/', views.paymentMethodComplete, name='aiScannerPaymentMethodComplete'),
    path('callback/', views.scanCallback, name='aiScannerCallback'),
    
    # Scan management
    path('scan-history/', views.getScanHistory, name='aiScannerHistory'),
    path('scan-details/<str:scan_id>/', views.getScanDetails, name='aiScannerDetails'),
    path('platform-monitor-url/<str:scan_id>/', views.getPlatformMonitorUrl, name='aiScannerPlatformMonitorUrl'),
    path('platform-status/<str:scan_id>/', views.getPlatformScanStatus, name='aiScannerPlatformStatus'),
    
    # Note: RESTful API endpoints are in /api/urls.py for external access
    
    # Legacy API endpoints (for backward compatibility)
    path('api/authenticate/', views.aiScannerAuthenticate, name='aiScannerAuthenticate'),
    path('api/list-files/', views.aiScannerListFiles, name='aiScannerListFiles'),
    path('api/get-file/', views.aiScannerGetFile, name='aiScannerGetFile'),
]