from .models import User, Profile, Conference, Venue, Agenda, ParticipantRequest, Notification
from rest_framework import serializers

from friendship.models import FriendshipRequest, Friend

class ProfileSerializer(serializers.ModelSerializer):
    # user = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name="user-detail")
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name', 'city', 'organization', 'bio']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']
        ordering = ['username']


class VenueSerializer(serializers.ModelSerializer):
    # conference = serializers.HyperlinkedRelatedField(many=False, queryset=Conference.objects.all(), view_name="conference-detail")
    conference = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Venue
        fields = ['id', 'conference', 'name', 'description' ]


class ConferenceSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    agenda = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')

    class Meta:
        model = Conference
        fields = ['id', 'user', 'venue', 'agenda', 'name', 'description', 'acronym', 'website', 'email_conference', 'email_chair', 'public', 'starts', 'ends']
        order_by = ['acronym']


class AgendaSerializer(serializers.ModelSerializer):
    conference = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    venue = serializers.PrimaryKeyRelatedField(many=False, queryset=Venue.objects.all())

    class Meta:
        model = Agenda
        fields = ['id', 'title', 'abstract', 'author', 'presenter', 'keywords', 'starts', 'ends', 'keywords', 'conference', 'venue']
        ordering = ['id']


class FriendshipRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendshipRequest
        fields = ('id', 'from_user', 'to_user', 'message', 'created', 'rejected', 'viewed')


class ParticipantRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParticipantRequest
        fields = ('id', 'conference', 'user', 'message', 'created', 'rejected', 'viewed')

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('id', 'user', 'message', 'created', 'viewed')