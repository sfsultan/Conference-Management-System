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

    # path('user/', views.UserView.as_view()),

    # path('profile/', views.ProfileView.as_view()),

    # path('my-conferences/', views.MyConferenceListView.as_view()),
    # path('my-conferences/<int:pk>/', views.MyConferenceDetailView.as_view()),

    # path('other-conferences/', views.OtherConferenceListView.as_view()),

    # path('venues/for/<int:conference_id>/', views.VenueListView.as_view()),
    # path('venues/<int:pk>/', views.VenueDetailView.as_view()),

    # path('agenda/for/<int:conference_id>/', views.AgendaListView.as_view()),
    # path('agenda/<int:pk>/', views.AgendaDetailView.as_view()),

    # path('friends/', views.FriendListView.as_view()),

    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
router = DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'my_conferences', views.MyConferenceViewSet, basename='my-conferences')
router.register(r'other_conferences', views.OtherConferenceViewSet, basename='other-conferences')
router.register(r'venues', views.VenueViewSet, basename='venues')
router.register(r'agendas', views.AgendaViewSet, basename='agendas')
router.register(r'friends', views.FriendViewSet, basename='friends')
router.register(r'friendrequests', views.FriendshipRequestViewSet, basename='friendrequests')
urlpatterns = router.urls

# urlpatterns = format_suffix_patterns(urlpatterns)
