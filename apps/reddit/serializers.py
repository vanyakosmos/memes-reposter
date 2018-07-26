from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    media_type = serializers.SerializerMethodField()

    def get_media_type(self, post: Post):
        return post.media_type

    class Meta:
        model = Post
        fields = ('id', 'subreddit', 'title', 'media_link', 'media_type', 'status',
                  'created', 'reddit_id', 'media_type')
