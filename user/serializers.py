from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "first_name", "last_name", "is_staff"]
        read_only_fields = ["is_staff"]