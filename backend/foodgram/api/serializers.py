from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if not request or request.user.is_anonymous:
            return False
        return self.obj.following.filter(user=request.user).exists()
