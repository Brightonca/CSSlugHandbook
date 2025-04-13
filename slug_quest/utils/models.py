from django.db import models

# Create your models here.
class UploadedPDF(models.Model):
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Professor(models.Model):
    name = models.CharField(max_length=255)
    university = models.CharField(max_length=255)
    rating = models.CharField(max_length=10)
    difficulty = models.CharField(max_length=10)
    take_again = models.CharField(max_length=10)
    tags = models.JSONField(default=list)

    def __str__(self):
        return f"{self.name} ({self.university})"