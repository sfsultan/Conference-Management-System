from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils import timezone

from django.db import IntegrityError


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

    # TODO: INCLUDE A TIMEZONE FOR THE CONFERENCES AS THAT IS CRUCIAL
    timezone = models.CharField(max_length=30, blank=False, null=True)

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

class ParticipantManager(models.Manager):
    def participants(self, conference):
        ''' RETURN A LIST OF ALL PARTICIPANTS '''
        return Participant.objects.filter(conference=conference)
    
    def requests(self, conference):
        return ParticipantRequest.objects.filter(conference=conference)
    
    def sent_requests(self, user):
        return ParticipantRequest.objects.filter(user=user)

    def unread_request_count(self, conference):
        return ParticipantRequest.objects.filter(conference=conference, viewed__isnull=True).count()

    def rejected_requests(self, conference):
        return ParticipantRequest.objects.filter(conference=conference, rejected__isnull=False).all()

    def unrejected_requests(self, conference):
        return ParticipantRequest.objects.filter(conference=conference, rejected__isnull=True).all()

    def add_participant(self, conference, user, message):
        request, created = ParticipantRequest.objects.get_or_create( conference=conference, user=user, message=message )
        if created is False:
            raise IntegrityError('Request already sent')
        request.save()
        return request

    def remove_participant(self, conference, user):
        try:
            ParticipantRequest.objects.filter( conference=conference, user=user ).delete()
        except:
            raise IntegrityError('User does not exist') 

class Participant(models.Model):
    conference = models.ForeignKey( Conference, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name="participants")

    objects = ParticipantManager()

    def __str__(self):
        return '%s (%s)' % (self.conference, self.user)

class ParticipantRequest(models.Model):
    conference = models.ForeignKey( Conference, on_delete=models.CASCADE, related_name="participant_requests")
    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name="participants_requests")

    message = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    rejected = models.DateTimeField(blank=True, null=True)
    viewed = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together =['conference', 'user']

    def accept(self):
        Participant.objects.create(Conference=self.conference, user=self.user)
        return True

    def reject(self):
        self.rejected = timezone.now()
        self.save()
        return True

    def cancel(self):
        self.delete()
        return True

    def mark_viewed(self):
        self.viewed = timezone.now() 
        self.save()
        return True

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link = models.CharField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    viewed = models.DateTimeField(null=True)

    def unread_count(self, user):
        return Notification.objects.filter(user=user, viewed__isnull=True).count()

    def mark_viewed(self):
        self.viewed = timezone.now() 
        self.save()
        return True

    def notify(self, user, type, message):
        Notification.objects.create()