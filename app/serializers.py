from django.contrib.auth.models import User

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["value", "text", "name", "username"]

    value = serializers.IntegerField(source="id", read_only=True)
    text = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField(method_name="get_text")

    def get_text(self, obj: User) -> str:
        return obj.get_full_name()
