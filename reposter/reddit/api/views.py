from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from reddit import tasks
from reddit.models import Post
from .serializers import PostSerializer, PostUpdateRequest, RejectRequest, RejectResponse


class PostViewMixin:
    permission_classes = (IsAdminUser,)
    queryset = Post.objects.filter(status=Post.PENDING)


class PostsListView(PostViewMixin, generics.ListAPIView):
    serializer_class = PostSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ('subreddit_name',)
    ordering_fields = ('created', 'score')
    search_fields = ('title',)

    @swagger_auto_schema(operation_id="get pending posts list")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PostView(PostViewMixin, generics.GenericAPIView):
    serializer_class = PostUpdateRequest

    @swagger_auto_schema(
        operation_id="publish single post",
        responses={status.HTTP_201_CREATED: 'empty'},
    )
    def post(self, request: Request, *args, **kwargs):
        post = self.get_object()
        if post.status == Post.ACCEPTED:
            return Response(status=status.HTTP_201_CREATED)

        s: PostUpdateRequest = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        title = s.validated_data.get('title')
        post.status = Post.ALMOST
        if title:
            post.title = title
        post.save()
        tasks.publish_post_task.delay(post.id, bool(title))
        return Response(status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    operation_id="reject posts in bulk",
    method='post',
    request_body=RejectRequest,
    responses={status.HTTP_200_OK: RejectResponse},
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_view(request: Request):
    s = RejectRequest(data=request.data)
    s.is_valid(raise_exception=True)
    posts = Post.objects.filter(pk__in=s.validated_data['posts'])
    rows = posts.update(status=Post.REJECTED)
    res = RejectResponse(data={'rejected': rows})
    res.is_valid(raise_exception=True)
    return Response(res.validated_data)
