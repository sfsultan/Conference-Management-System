from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    """auth/login-related fields"""
    pass


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")

    full_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)


class Conference(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conference")

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True, null=True)
    acronym = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(max_length=300, blank=True, null=True)
    email_conference = models.EmailField(max_length=50, blank=True, null=True)
    email_chair = models.EmailField(max_length=50, blank=True, null=True)
    # IS IT VISIBLE TO THE PUBLIC WHEN SEARCHED
    public = models.BooleanField(default=True)

    starts = models.DateTimeField(null=True)
    ends = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Venue(models.Model):
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="venue")

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True, null=True)

    @property
    def user(self):
        return self.conference.user

    def __str__(self):
        return '%s (%s)' % (self.name, self.conference.name)

    class Meta:
        unique_together = ['conference', 'name']


class Agenda(models.Model):
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="agenda")
    venue = models.ForeignKey(
        Venue, on_delete=models.CASCADE, related_name="agenda")

    title = models.CharField(max_length=200)
    abstract = models.TextField(max_length=1000, blank=True, null=True)
    presenter = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    keywords = models.CharField(max_length=100)

    starts = models.DateTimeField(blank=True, null=True)
    ends = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '%s (%s)' % (self.title, self.presenter)


