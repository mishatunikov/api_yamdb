from django.urls import include, path

from api.views import SignUpAPIView

auth_endpoints = [
    path('signup/', SignUpAPIView.as_view()),
]


urlpatterns = [
    path('v1/auth/', include(auth_endpoints))
]
