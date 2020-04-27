from django.shortcuts import render
from django.http import Http404
from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import get_object_or_404


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings


from friendship.models import Friend, Follow, Block


from .models import User, Conference, Profile, Venue, Agenda
from rest_framework import viewsets
from .serializers import UserSerializer, ConferenceSerializer, ProfileSerializer, VenueSerializer, AgendaSerializer,  FriendRequestSerializer
from .permissions import IsOwner, IsOwnerOfConference


class UserView(APIView):

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        user = self.get_user(self.request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):

    def get_profile(self, pk):
        try:
            return Profile.objects.get(user=pk)
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        profile = self.get_profile(self.request.user.id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, format=None):
        profile = self.get_profile(request.user.id)
        serializer = ProfileSerializer(
            profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyConferenceListView(APIView):

    def get(self, request, format=None):
        conferences = Conference.objects.filter(user=self.request.user)
        serializer = ConferenceSerializer(conferences, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ConferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyConferenceDetailView(APIView):
    permission_classes = [IsOwner]
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_conference(self, pk):
        try:
            conference = Conference.objects.get(pk=pk)
            return conference
        except Conference.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        conference = self.get_conference(pk)
        self.check_object_permissions(request, conference)
        serializer = ConferenceSerializer(conference)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        conference = self.get_conference(pk)
        serializer = ConferenceSerializer(conference, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        conference = self.get_conference(pk)
        conference.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OtherConferenceListView(APIView):

    def get(self, request, format=None):
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


class VenueListView(APIView):
    permission_classes = [IsOwner]

    def get_conference(self, pk):
        try:
            conference = Conference.objects.get(pk=pk)
            return conference
        except Conference.DoesNotExist:
            raise Http404

    def get(self, request, conference_id, format=None):
        conference = self.get_conference(conference_id)
        self.check_object_permissions(request, conference)
        venues = Venue.objects.filter(conference=conference)
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data)

    def post(self, request, conference_id, format=None):
        conference = self.get_conference(conference_id)
        self.check_object_permissions(request, conference)
        serializer = VenueSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(conference=conference)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({'detail': 'Venue already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VenueDetailView(APIView):
    permission_classes = [IsOwner]
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_venue(self, pk):
        try:
            venue = Venue.objects.get(pk=pk)
            return venue
        except Venue.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        venue = self.get_venue(pk)
        self.check_object_permissions(request, venue)
        serializer = VenueSerializer(venue)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        venue = self.get_venue(pk)
        self.check_object_permissions(request, venue)
        serializer = VenueSerializer(venue, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        venue = self.get_venue(pk)
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


class ConnectionListView(APIView):

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    

    def get(self, request, format=None):
        o
        connections = Connection.objects.filter(Q(user=request.user) | Q(connected_user=request.user))
        serializer = ConnectionSerializer(connections, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            other_user = self.get_user(request)
            friend_obj = Friend.objects.add_friend( request.user, get_object_or_404(get_user_model(), pk=request.data['user_id']),
            message=request.data.get('message', '')
        )
            # serializer.save()
            return Response(FriendRequestSerializer(friend_obj).data, status=status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
