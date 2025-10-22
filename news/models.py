from django.db import models
from django.utils import timezone

# Create your models here.
class Headline(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('business', 'Business'),
        ('national', 'National'),
        ('sports', 'Sports'),
        ('world', 'World'),
        ('politics', 'Politics'),
        ('technology', 'Technology'),
        ('startup', 'Startup'),
        ('entertainment', 'Entertainment'),
        ('miscellaneous', 'Miscellaneous'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
    ]

    LEANING_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
        ('center', 'Center'),
    ]

    # Core fields
    title = models.CharField(max_length=500)
    content = models.TextField()
    img = models.URLField(max_length=1000, null=True, blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)

    # Category & Language
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', db_index=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en', db_index=True)

    # Metadata
    leaning = models.CharField(max_length=10, choices=LEANING_CHOICES, default='center')
    date = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'language']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Headline'
        verbose_name_plural = 'Headlines'

    def __str__(self):
        return f"{self.title[:50]}... ({self.category} - {self.language})"