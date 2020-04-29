from django.shortcuts import render
from django.http import Http404
from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import Error

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.decorators import action


from friendship.models import Friend, Follow, Block
from friendship.exceptions import AlreadyExistsError, AlreadyFriendsError


from .models import User, Conference, Profile, Venue, Agenda
from rest_framework import viewsets
from .serializers import UserSerializer, ConferenceSerializer, ProfileSerializer, VenueSerializer, AgendaSerializer, FriendshipRequestSerializer
from .permissions import IsOwner, IsOwnerOfConference



class UserViewSet(viewsets.ViewSet):

    def list(self, request):
        user = get_object_or_404(User, pk=self.request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileViewSet(viewsets.ViewSet):

    def list(self, request):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def change(self, request):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer = ProfileSerializer(
            profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyConferenceViewSet(viewsets.ViewSet):

    permission_classes = [IsOwner]

    def list(self, request):
        conferences = Conference.objects.filter(user=self.request.user)
        serializer = ConferenceSerializer(conferences, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ConferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        serializer = ConferenceSerializer(conference)
        return Response(serializer.data)

    def update(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        serializer = ConferenceSerializer(conference, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        conference.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def venues(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        venues = Venue.objects.filter(conference=conference)
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_venue(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        serializer = VenueSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(conference=conference)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({'detail': 'Venue already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def agendas(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        agenda = Agenda.objects.filter(conference=conference)
        serializer = AgendaSerializer(agenda, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_agenda(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        serializer = AgendaSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(conference=conference)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({'detail': 'Venue already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OtherConferenceViewSet(viewsets.ViewSet):

    def list(self, request):
        conferences = Conference.objects.exclude(
            user=self.request.user).filter(public=True)

        search = request.query_params.get('search', None)
        if search is not None:
            conferences = conferences.filter(
                Q(name__icontains=search) | Q(description__icontains=search))
        
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        page = paginator.paginate_queryset(conferences, request)

        serializer = ConferenceSerializer(page, many=True)
        return Response(serializer.data)

class VenueViewSet(viewsets.ViewSet):

    permission_classes = [IsOwnerOfConference]

    def retrieve(self, request, pk):
        venue = get_object_or_404(Venue, pk=pk)
        self.check_object_permissions(request, venue)
        serializer = VenueSerializer(venue)
        return Response(serializer.data)

    def update(self, request, pk):
        venue = get_object_or_404(Venue, pk=pk)
        self.check_object_permissions(request, venue)
        serializer = VenueSerializer(venue, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        venue = get_object_or_404(Venue, pk=pk)
        self.check_object_permissions(request, venue)
        venue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AgendaListView(APIView):
    permission_classes = [IsOwner]

    def get_conference(self, pk):
        try:
            conference = Conference.objects.get(pk=pk)
            return conference
        except Conference.DoesNotExist:
            raise Http404

    def get_venue(self, pk):
        try:
            venue = Venue.objects.get(pk=pk)
            return venue
        except Venue.DoesNotExist:
            raise Http404

    def get(self, request, conference_id, format=None):
        conference = self.get_conference(conference_id)
        self.check_object_permissions(request, conference)
        agenda = Agenda.objects.filter(conference=conference)
        serializer = AgendaSerializer(agenda, many=True)
        return Response(serializer.data)

    def post(self, request, conference_id, format=None):
        conference = self.get_conference(conference_id)
        self.check_object_permissions(request, conference)

        serializer = AgendaSerializer(data=request.data)

        if serializer.is_valid():
            venue = self.get_venue(request.data['venue'])
            if venue.conference != conference:
                return Response({'detail': 'Venue does not belong to this conference'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(conference=conference)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgendaDetailView(APIView):
    permission_classes = [IsOwnerOfConference]
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_agenda(self, pk):
        try:
            agenda = Agenda.objects.get(pk=pk)
            return agenda
        except Agenda.DoesNotExist:
            raise Http404

    def get_venue(self, pk):
        try:
            venue = Venue.objects.get(pk=pk)
            return venue
        except Venue.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        agenda = self.get_agenda(pk)
        self.check_object_permissions(request, agenda)
        serializer = AgendaSerializer(agenda)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        agenda = self.get_agenda(pk)
        self.check_object_permissions(request, agenda)
        serializer = AgendaSerializer(agenda, data=request.data)
        if serializer.is_valid():
            venue = self.get_venue(request.data['venue'])
            if venue.conference != agenda.conference:
                return Response({'detail': 'Venue does not belong to this conference'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        agenda = self.get_agenda(pk)
        self.check_object_permissions(request, agenda)
        agenda.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendListView(APIView):

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    

    def get(self, request, format=None):
        friends = Friend.objects.friends(request.user)
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(friends)
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        other_user = self.get_user(request.data['user_id'])
        try:
            friend_obj = Friend.objects.add_friend( request.user, other_user, message=request.data.get('message', '') )
        except ValidationError as e:
            return Response({'detail': e}, status=status.HTTP_400_BAD_REQUEST)
        except AlreadyExistsError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(FriendshipRequestSerializer(friend_obj).data, status=status.HTTP_201_CREATED)




