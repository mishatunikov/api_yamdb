from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import SignUpAPIView, TokenAccessObtainView
from .views import (CategoryViewSet, TitleViewSet, GenreViewSet)

router_v1 = SimpleRouter()

router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'categories', CategoryViewSet)

auth_endpoints = [
    path('signup/', SignUpAPIView.as_view()),
    path('token/', TokenAccessObtainView.as_view())
]


urlpatterns = [
    path('v1/auth/', include(auth_endpoints))
]
