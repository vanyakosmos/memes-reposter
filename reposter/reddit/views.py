from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from . import tasks
from .models import Post
from .serializers import PostSerializer, PostUpdateSerializer, RejectSerializer


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_view(request):
    tasks.fetch_and_publish()
    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def blank_publish_view(request):
    """Save posts into db w/o publishing."""
    tasks.fetch_and_publish(blank=True)
    return Response({'status': 'ok'})


@api_view()
@permission_classes([IsAdminUser])
def index(request: Request):
    return render(request, 'reddit/index.html')


class PostViewMixin(generics.GenericAPIView):
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        qs = Post.objects.filter(status=Post.STATUS_PENDING)
        qs = qs.order_by('-created')
        return qs


class PendingPostListView(PostViewMixin, generics.ListAPIView):
    serializer_class = PostSerializer


class PostView(PostViewMixin, generics.UpdateAPIView):
    serializer_class = PostUpdateSerializer

    def update(self, request: Request, *args, **kwargs):
        s = self.get_serializer(data=request.data)  # type: PostUpdateSerializer
        s.is_valid(raise_exception=True)
        title = s.validated_data.get('title')

        post = self.get_object()
        if post.status == Post.STATUS_ACCEPTED:
            return Response({
                'accepted': True,
            })
        post.status = Post.STATUS_ALMOST
        post.title = title or post.title
        post.save()
        tasks.publish_post_task.delay(post.id, bool(title))
        return Response({
            'accepted': True,
        })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_view(request: Request):
    s = RejectSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    posts_ids = s.validated_data['posts']
    posts = Post.objects.filter(pk__in=s.validated_data['posts'])
    posts.update(status=Post.STATUS_REJECTED)
    return Response({
        'rejected': posts_ids,
    })
