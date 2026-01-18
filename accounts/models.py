from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'STUDENT'),
        ('educator', 'EDUCATOR')
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type', 'username']
    
    def __str__(self):
        return f"{self.email} ({self.user_type})"
    
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Student_profile")
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    # Enrollment tracked via core.Enrollment model
    
    def __str__(self):
        return f"Student: {self.user.email}"

class EducatorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='educator_profile')
    bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return f"Educator: {self.user.email}"