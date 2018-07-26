from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.views import poster
from apps.reddit.serializers import PostSerializer
from . import tasks
from .models import Post


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_view(request):
    return poster(tasks.fetch_and_publish)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def blank_publish_view(request):
    """Save posts into db w/o publishing."""
    return poster(lambda: tasks.fetch_and_publish(force=True, blank=True))


class PendingPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(status=Post.STATUS_PENDING,
                                   subreddit__on_moderation=True)


class PostView(generics.UpdateAPIView):
    queryset = Post.objects.filter(status=Post.STATUS_PENDING,
                                   subreddit__on_moderation=True)

    def update(self, request: Request, *args, **kwargs):
        post = self.get_object()
        accepted = request.data.get('accepted', False)
        post.status = Post.STATUS_ACCEPTED if accepted else Post.STATUS_REJECTED
        post.save()
        return Response({
            'accepted': accepted,
        })
