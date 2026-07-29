from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password", "first_name", "last_name", "is_staff", "follows"]
        read_only_fields = ["is_staff"]

    def update(self, instance, validated_data):
        password = validated_data.get("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password", "first_name", "last_name", "is_staff"]
        read_only_fields = ["is_staff"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"}
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)