from rest_framework import serializers

from reddit.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostUpdateRequest(serializers.Serializer):
    title = serializers.CharField(allow_null=True)


class RejectRequest(serializers.Serializer):
    posts = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="IDs of posts to reject.",
    )


class RejectResponse(serializers.Serializer):
    rejected = serializers.IntegerField(help_text="Number of rejected posts.")
