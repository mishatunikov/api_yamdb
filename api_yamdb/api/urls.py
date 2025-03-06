from django.urls import include, path

from api.views import SignUpAPIView, TokenAccessObtainView

auth_endpoints = [
    path('signup/', SignUpAPIView.as_view()),
    path('token/', TokenAccessObtainView.as_view())
]


urlpatterns = [
    path('v1/auth/', include(auth_endpoints))
]
