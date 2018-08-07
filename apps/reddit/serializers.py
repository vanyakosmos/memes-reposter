from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    media_type = serializers.SerializerMethodField()
    comments_url = serializers.SerializerMethodField()
    sub = serializers.SerializerMethodField()

    def get_media_type(self, post: Post):
        return post.media_type

    def get_comments_url(self, post: Post):
        return post.comments_full

    def get_sub(self, post: Post):
        return post.subreddit.name

    class Meta:
        model = Post
        fields = ('id', 'sub', 'title', 'media_link', 'media_type', 'status',
                  'created', 'reddit_id', 'media_type', 'comments_url')


class PostUpdateSerializer(serializers.Serializer):
    accepted = serializers.BooleanField(default=False)
    title = serializers.CharField(allow_null=True)
