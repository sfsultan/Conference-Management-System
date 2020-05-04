from django.urls import include, path

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from . import views

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('', include(router.urls)),
    path('auth/', include('djoser.urls.jwt')),

    path('user/', views.UserRetrieveCreateView.as_view()),

    path('profile/', views.ProfileRetrieveUpdateView.as_view()),

    path('myconferences/', views.MyConferenceListCreateView.as_view()),
    path('myconferences/<int:pk>/', views.MyConferenceRetrieveUpdateDeleteView.as_view()),

    path('otherconferences/', views.OtherConferenceListView.as_view()),

    path('venues/for/<int:conference_id>/', views.VenueListCreateView.as_view()),
    path('venues/<int:pk>/', views.VenueRetrieveUpdateDeleteView.as_view()),

    path('agendas/for/<int:conference_id>/', views.AgendaListCreateView.as_view()),
    path('agendas/<int:pk>/', views.AgendaRetrieveUpdateDelete.as_view()),

    # path('friends/', views.FriendListView.as_view()),

]
router = DefaultRouter()
router.register(r'friends', views.FriendViewSet, basename='friends')
router.register(r'friendrequests', views.FriendshipRequestViewSet, basename='friendrequests')
router.register(r'participants', views.ParticipantViewSet, basename='participants')
router.register(r'participantrequests', views.ParticipantsRequestViewSet, basename='participantrequests')
urlpatterns += router.urls

# urlpatterns = format_suffix_patterns(urlpatterns)
