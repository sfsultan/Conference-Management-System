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


from .models import User, Conference, Profile, Venue, Agenda, ParticipantRequest, Participant
from rest_framework import viewsets
from .serializers import UserSerializer, ConferenceSerializer, ProfileSerializer
from .serializers import VenueSerializer, AgendaSerializer, FriendshipRequestSerializer
from .serializers import ParticipantRequestSerializer
from .permissions import IsOwner, IsOwnerOfConference

class UserRetrieveCreateView(APIView):
    def get(self, request):
        user = get_object_or_404(User, pk=self.request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileRetrieveUpdateView(APIView):

    def get(self, request):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer = ProfileSerializer(
            profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyConferenceListCreateView(APIView):

    def get(self, request):
        conferences = Conference.objects.filter(user=self.request.user)
        serializer = ConferenceSerializer(conferences, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyConferenceRetrieveUpdateDeleteView(APIView):
    permission_classes = [IsOwner]

    def get(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        serializer = ConferenceSerializer(conference)
        return Response(serializer.data)

    def put(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        serializer = ConferenceSerializer(conference, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        conference.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OtherConferenceListView(APIView):

    def get(self, request):
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

class VenueListCreateView(APIView):
    permission_classes = [IsOwner]

    def get(self, request, conference_id):
        conference = get_object_or_404(Conference, pk=conference_id)
        self.check_object_permissions(request, conference)
        venues = Venue.objects.filter(conference=conference)
        serializer = VenueSerializer(venues, many=True)
        return Response(serializer.data)

    def post(self, request, conference_id):
        conference = get_object_or_404(Conference, pk=conference_id)
        self.check_object_permissions(request, conference)
        serializer = VenueSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(conference=conference)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({'detail': 'Venue already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VenueRetrieveUpdateDeleteView(APIView):

    permission_classes = [IsOwnerOfConference]

    def get(self, request, pk):
        venue = get_object_or_404(Venue, pk=pk)
        self.check_object_permissions(request, venue)
        serializer = VenueSerializer(venue)
        return Response(serializer.data)

    def put(self, request, pk):
        venue = get_object_or_404(Venue, pk=pk)
        self.check_object_permissions(request, venue)
        serializer = VenueSerializer(venue, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        venue = get_object_or_404(Venue, pk=pk)
        self.check_object_permissions(request, venue)
        venue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AgendaListCreateView(APIView):
    permission_classes = [IsOwner]

    def get(self, request, conference_id):
        conference = get_object_or_404(Conference, pk=conference_id)
        self.check_object_permissions(request, conference)
        agenda = Agenda.objects.filter(conference=conference)
        serializer = AgendaSerializer(agenda, many=True)
        return Response(serializer.data)

    def post(self, request, conference_id):
        conference = get_object_or_404(Conference, pk=conference_id)
        self.check_object_permissions(request, conference)
        serializer = AgendaSerializer(data=request.data)

        if serializer.is_valid():
            venue = get_object_or_404(Venue, pk=request.data['venue'])
            if venue.conference != conference:
                return Response({'detail': 'Venue does not belong to this conference'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                serializer.save(conference=conference)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({'detail': 'Venue already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AgendaRetrieveUpdateDelete(APIView):

    permission_classes = [IsOwnerOfConference]

    def get(self, request, pk):
        agenda = get_object_or_404(Agenda, pk=pk)
        self.check_object_permissions(request, agenda)
        serializer = AgendaSerializer(agenda)
        return Response(serializer.data)

    def put(self, request, pk):
        agenda = get_object_or_404(Agenda, pk=pk)
        self.check_object_permissions(request, agenda)
        serializer = AgendaSerializer(agenda, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        agenda = get_object_or_404(Agenda, pk=pk)
        self.check_object_permissions(request, agenda)
        agenda.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ParticipantsRequestViewSet(viewsets.ViewSet):
    """
    ViewSet for ParticipantRequest model
    """

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        participant_request = get_object_or_404(ParticipantRequest, pk=pk, user=request.user)
        participant_request.accept()
        return Response( ParticipantRequestSerializer(participant_request).data, status.HTTP_201_CREATED )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        participant_request = get_object_or_404(ParticipantRequest, pk=pk, to_user=request.user)
        participant_request.reject()
        return Response( ParticipantRequestSerializer(participant_request).data, status.HTTP_201_CREATED )

class ParticipantViewSet(viewsets.ViewSet):

    permission_classes = [IsOwner]

    @action(detail=True, methods=['get'])
    def approved(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        participants = Participant.objects.participants(conference=conference)
        serializer = UserSerializer(participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def requests(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        participant_requests = Participant.objects.unrejected_requests(conference=conference)
        return Response(ParticipantRequestSerializer(participant_requests, many=True).data)

    @action(detail=True, methods=['get'])
    def sent_requests(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        participant_requests = Participant.objects.sent_requests(user=request.user)
        return Response(ParticipantRequestSerializer(participant_requests, many=True).data)

    @action(detail=True, methods=['get'])
    def rejected_requests(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        self.check_object_permissions(request, conference)
        participant_requests = Participant.objects.rejected_requests(conference=conference)
        return Response(ParticipantRequestSerializer(participant_requests, many=True).data)

    @action(detail=True, methods=['post'])
    def send_request(self, request, pk):
        '''
        POST data:
        - conference_id
        - 
        '''

        conference = get_object_or_404(Conference, pk=pk)
        if conference.user == request.user:
            return Response({'detail': 'Cannot send a request to a conference you created'}, status=status.HTTP_400_BAD_REQUEST)
            

        try:
            participant_obj = Participant.objects.add_participant( conference, request.user, message=request.data.get('message', '') )
        except IntegrityError as e:
            return Response({'detail': 'Request already sent'} , status.HTTP_201_CREATED )

        return Response( ParticipantRequestSerializer(participant_obj).data, status.HTTP_201_CREATED )

    def destroy(self, request, pk=None):
        """
        Deletes a friend relationship
        The user id specified in the URL will be removed from the current user's friends
        """

        user_friend = get_object_or_404(User, pk=pk)

        if Friend.objects.remove_friend(request.user, user_friend):
            message = 'deleted'
            status_code = status.HTTP_204_NO_CONTENT
        else:
            message = 'not deleted'
            status_code = status.HTTP_304_NOT_MODIFIED

        return Response(
            {"message": message},
            status=status_code
        )


class FriendViewSet(viewsets.ViewSet):

    def list(self, request):
        friends = Friend.objects.friends(request.user)
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def requests(self, request):
        friend_requests = Friend.objects.unrejected_requests(user=request.user)
        return Response(FriendshipRequestSerializer(friend_requests, many=True).data)

    @action(detail=False)
    def sent_requests(self, request):
        friend_requests = Friend.objects.sent_requests(user=request.user)
        return Response(FriendshipRequestSerializer(friend_requests, many=True).data)

    @action(detail=False)
    def rejected_requests(self, request):
        friend_requests = Friend.objects.rejected_requests(user=request.user)
        return Response(FriendshipRequestSerializer(friend_requests, many=True).data)

    def create(self, request):
        """
        Creates a friend request
        POST data:
        - user_id
        - message
        """

        try:
            friend_obj = Friend.objects.add_friend( request.user, get_object_or_404(User, pk=request.data['user_id']), message=request.data.get('message', '') )
        except AlreadyExistsError as e:
            return Response({'detail': str(e)} , status.HTTP_201_CREATED )


        return Response( FriendshipRequestSerializer(friend_obj).data, status.HTTP_201_CREATED )

    def destroy(self, request, pk=None):
        """
        Deletes a friend relationship
        The user id specified in the URL will be removed from the current user's friends
        """

        user_friend = get_object_or_404(User, pk=pk)

        if Friend.objects.remove_friend(request.user, user_friend):
            message = 'deleted'
            status_code = status.HTTP_204_NO_CONTENT
        else:
            message = 'not deleted'
            status_code = status.HTTP_304_NOT_MODIFIED

        return Response(
            {"message": message},
            status=status_code
        )

class FriendshipRequestViewSet(viewsets.ViewSet):
    """
    ViewSet for FriendshipRequest model
    """

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friendship_request = get_object_or_404(FriendshipRequest, pk=pk, to_user=request.user)
        friendship_request.accept()
        return Response( FriendshipRequestSerializer(friendship_request).data, status.HTTP_201_CREATED )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        friendship_request = get_object_or_404(FriendshipRequest, pk=pk, to_user=request.user)
        friendship_request.reject()
        return Response( FriendshipRequestSerializer(friendship_request).data, status.HTTP_201_CREATED )
