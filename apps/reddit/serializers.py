from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    media_type = serializers.SerializerMethodField()

    def get_media_type(self, post: Post):
        return post.meta.type

    class Meta:
        model = Post
        fields = ('subreddit', 'title', 'link', 'status',
                  'created', 'reddit_id', 'media_type')
