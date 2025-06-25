from django.db import models
from loginSystem.models import Administrator
import json

# Import the status update model
from .status_models import ScanStatusUpdate


class AIScannerSettings(models.Model):
    """Store AI scanner configuration and API keys for administrators"""
    admin = models.OneToOneField(Administrator, on_delete=models.CASCADE, related_name='ai_scanner_settings')
    api_key = models.CharField(max_length=255, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    is_payment_configured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_scanner_settings'

    def __str__(self):
        return f"AI Scanner Settings for {self.admin.userName}"


class ScanHistory(models.Model):
    """Store scan history and results"""
    SCAN_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    SCAN_TYPE_CHOICES = [
        ('full', 'Full Scan'),
        ('quick', 'Quick Scan'),
        ('custom', 'Custom Scan'),
    ]

    admin = models.ForeignKey(Administrator, on_delete=models.CASCADE, related_name='scan_history')
    scan_id = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=255)
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES, default='full')
    status = models.CharField(max_length=20, choices=SCAN_STATUS_CHOICES, default='pending')
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    files_scanned = models.IntegerField(default=0)
    issues_found = models.IntegerField(default=0)
    findings_json = models.TextField(blank=True, null=True)  # Store JSON findings
    summary_json = models.TextField(blank=True, null=True)  # Store JSON summary
    error_message = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_scanner_history'
        ordering = ['-started_at']

    def __str__(self):
        return f"Scan {self.scan_id} - {self.domain} ({self.status})"

    @property
    def findings(self):
        """Parse findings JSON"""
        if self.findings_json:
            try:
                return json.loads(self.findings_json)
            except json.JSONDecodeError:
                return []
        return []

    @property
    def summary(self):
        """Parse summary JSON"""
        if self.summary_json:
            try:
                return json.loads(self.summary_json)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_findings(self, findings_list):
        """Set findings from list/dict"""
        self.findings_json = json.dumps(findings_list)

    def set_summary(self, summary_dict):
        """Set summary from dict"""
        self.summary_json = json.dumps(summary_dict)


class FileAccessToken(models.Model):
    """Temporary tokens for file access during scans"""
    token = models.CharField(max_length=100, unique=True)
    scan_history = models.ForeignKey(ScanHistory, on_delete=models.CASCADE, related_name='access_tokens')
    domain = models.CharField(max_length=255)
    wp_path = models.CharField(max_length=500)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'ai_scanner_file_tokens'

    def __str__(self):
        return f"Access token {self.token} for {self.domain}"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
