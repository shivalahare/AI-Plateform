from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Tool(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('deprecated', 'Deprecated')
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tools')
    icon = models.ImageField(upload_to='tool_icons/', blank=True)
    model_name = models.CharField(max_length=100)
    input_format = models.JSONField(help_text="JSON schema for input format")
    output_format = models.JSONField(help_text="JSON schema for output format")
    max_tokens = models.IntegerField(default=2048)
    cost_per_token = models.DecimalField(max_digits=10, decimal_places=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ToolUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    input_data = models.JSONField()
    output_data = models.JSONField()
    tokens_used = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.tool.name} - {self.created_at}"
