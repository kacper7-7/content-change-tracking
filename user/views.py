from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from user.serializers import UserSerializer, CreateUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = get_user_model().objects.prefetch_related("follows")
        if self.request.user and self.request.user.is_staff:
            return queryset
        return queryset.filter(pk=self.request.user.pk)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return UserSerializer
