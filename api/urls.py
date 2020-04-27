from django.urls import include, path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
	
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('', include(router.urls)),
    path('auth/', include('djoser.urls.jwt')),

    path('user/', views.UserView.as_view()),

    path('profile/', views.ProfileView.as_view()),

    path('my-conferences/', views.MyConferenceListView.as_view()),
    path('my-conferences/<int:pk>/', views.MyConferenceDetailView.as_view()),

    path('other-conferences/', views.OtherConferenceListView.as_view()),

    path('venues/for/<int:conference_id>/', views.VenueListView.as_view()),
    path('venues/<int:pk>/', views.VenueDetailView.as_view()),

    path('agenda/for/<int:conference_id>/', views.AgendaListView.as_view()),
    path('agenda/<int:pk>/', views.AgendaDetailView.as_view()),

    path('connections/', views.ConnectionListView.as_view()),

    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

# urlpatterns = format_suffix_patterns(urlpatterns)