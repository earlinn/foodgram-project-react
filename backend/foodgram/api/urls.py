from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SelfUserView, SetPasswordRetypeView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('users/me/', SelfUserView.as_view()),
    path('users/set_password/', SetPasswordRetypeView.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
