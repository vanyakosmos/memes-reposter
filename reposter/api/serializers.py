from rest_framework import serializers


class PublishRequest(serializers.Serializer):
    blank = serializers.BooleanField(
        default=False,
        help_text="If true then don't propagate posts to targets.",
    )


class CleanUpRequest(serializers.Serializer):
    days = serializers.IntegerField(
        default=None,
        allow_null=True,
        help_text="Posts older than N days will be deleted.",
    )
