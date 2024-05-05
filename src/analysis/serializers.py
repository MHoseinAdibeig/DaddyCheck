from rest_framework import serializers

from .models import Gadget, State, Analysis, Result, SampleDetail


class GadgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gadget
        fields = "__all__"


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"


class SampleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleDetail

        fields = "__all__"


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        exclude = (
            "user",
            "gadget",
            "ip",
        )


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        exclude = (
            "iteration",
            "selected_result",
            "filename_format",
        )
