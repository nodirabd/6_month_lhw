from django.urls import path
from users.views import RegistrationAPIView, AuthorizationAPIView, ConfirmUserAPIView
from users.google_oauth import GoogleLoginAPIView
urlpatterns = [
    path('registration/', RegistrationAPIView.as_view()),
    path('authorization/', AuthorizationAPIView.as_view()),
    path('confirm/', ConfirmUserAPIView.as_view()),
    path('oauth/google/', GoogleLoginAPIView.as_view())
]