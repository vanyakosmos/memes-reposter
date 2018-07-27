from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    media_type = serializers.SerializerMethodField()
    comments_url = serializers.SerializerMethodField()

    def get_media_type(self, post: Post):
        return post.media_type

    def get_comments_url(self, post: Post):
        return post.comments_full

    class Meta:
        model = Post
        fields = ('id', 'subreddit', 'title', 'media_link', 'media_type', 'status',
                  'created', 'reddit_id', 'media_type', 'comments_url')


class PostUpdateSerializer(serializers.Serializer):
    accepted = serializers.BooleanField(default=False)
    title = serializers.CharField(allow_null=True)
