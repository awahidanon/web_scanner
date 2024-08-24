# scanner/models.py

from django.db import models

class ScanResult(models.Model):
    url = models.URLField()
    scan_date = models.DateTimeField(auto_now_add=True)
    result = models.TextField()
    parsed_result = models.TextField(blank=True, null=True)  # New field for parsed results
    vulnerabilities = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Scan for {self.url} on {self.scan_date}"
