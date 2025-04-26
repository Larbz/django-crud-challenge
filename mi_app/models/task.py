from django.db import models
from .project import Project

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
