from .models import User, Profile, Conference, Venue, Agenda
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    # user = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name="user-detail")
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name', 'city', 'organization', 'bio']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'profile']
        ordering = ['username']


class ConferenceSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    venue = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    agenda = serializers.SlugRelatedField(many=True, read_only=True, slug_field='title')

    class Meta:
        model = Conference
        fields = ['id', 'user', 'venue', 'agenda', 'name', 'description', 'acronym', 'website', 'email_conference', 'email_chair', 'public', 'starts', 'ends']
        order_by = ['acronym']



class VenueSerializer(serializers.HyperlinkedModelSerializer):
    # conference = serializers.HyperlinkedRelatedField(many=False, queryset=Conference.objects.all(), view_name="conference-detail")
    conference = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Venue
        fields = ['id', 'conference', 'name', 'description' ]
        





class AgendaSerializer(serializers.HyperlinkedModelSerializer):
    conference = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    venue = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Agenda
        fields = ['title', 'abstract', 'author', 'presenter', 'keywords', 'starts', 'ends', 'keywords', 'conference', 'venue']
        ordering = ['id']


