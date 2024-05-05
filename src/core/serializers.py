from rest_framework import serializers

from .models import Message, MessageLevel, Key


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class MessageLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLevel
        fields = "__all__"


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = "__all__"
