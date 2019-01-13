import graphene
from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import ResolveInfo

from apps.core.permissions import is_staff, permissions
from . import tasks
from .models import Post, RedditConfig


class PostFilter(FilterSet):
    order_by = OrderingFilter(
        fields=(
            ('created', 'created'),
            ('status', 'status'),
            ('score', 'score'),
        ),
    )

    class Meta:
        model = Post
        fields = (
            'status',
            'type',
            'subreddit__on_moderation',
            'subreddit__subscriptions__name',
            'subreddit__subscriptions__type',
        )


class PostNode(DjangoObjectType):
    class Meta:
        model = Post
        interfaces = (relay.Node,)

    @classmethod
    @permissions(is_staff)
    def get_node(cls, info, id):
        return super().get_node(info, id)


class RedditQuery(graphene.ObjectType):
    reddit_enabled = graphene.Boolean()
    reddit_post = relay.Node.Field(PostNode)
    all_reddit_posts = DjangoFilterConnectionField(PostNode, filterset_class=PostFilter)

    @permissions(is_staff)
    def resolve_reddit_enabled(self, info: ResolveInfo):
        return RedditConfig.get_solo().enabled

    @permissions(is_staff)
    def resolve_all_reddit_posts(self, info: ResolveInfo, **kwargs):
        return Post.objects.all()


class PublishPosts(graphene.Mutation):
    skip = graphene.Boolean()

    class Arguments:
        idle = graphene.Boolean(default_value=False)

    @permissions(is_staff)
    def mutate(self, info: ResolveInfo, idle):
        skip = not idle and tasks.skip_publishing()
        tasks.publish_posts_task.delay(idle)
        return PublishPosts(skip=skip)


class PublishPost(relay.ClientIDMutation):
    accepted = graphene.Boolean()

    class Input:
        id = graphene.ID(required=True)
        title = graphene.Boolean()

    @classmethod
    def get_object(cls, **input):
        try:
            id = relay.Node.from_global_id(input['id'])[1]
            return Post.objects.get(pk=id)
        except Post.DoesNotExist:
            pass

    @permissions(is_staff)
    def mutate_and_get_payload(self, info: ResolveInfo, **input):
        post = PublishPost.get_object(request=info.context, **input)
        if not post:
            raise Exception("Post not found")

        if post.status == Post.STATUS_ACCEPTED:
            return PublishPost(accepted=False)
        title = input.get('title')
        post.status = Post.STATUS_ALMOST
        post.title = title or post.title
        post.save()
        tasks.publish_post_task.delay(post.id, title)
        return PublishPost(accepted=True)


class PostInput(graphene.InputObjectType):
    id = graphene.ID(required=True)


class RejectPosts(graphene.Mutation):
    count = graphene.Int()

    class Arguments:
        posts = graphene.List(graphene.NonNull(graphene.ID), required=True)

    @permissions(is_staff)
    def mutate(self, info: ResolveInfo, posts):
        post_ids = [
            relay.Node.from_global_id(p)[1]
            for p in posts
        ]
        posts = Post.objects.filter(pk__in=post_ids)
        rows = posts.update(status=Post.STATUS_REJECTED)
        return RejectPosts(count=rows)


class ToggleRedditState(graphene.Mutation):
    enabled = graphene.Boolean()

    class Arguments:
        pass

    @permissions(is_staff)
    def mutate(self, info: ResolveInfo, **input):
        config = RedditConfig.get_solo()
        config.enabled = not config.enabled
        config.save()
        return ToggleRedditState(enabled=config.enabled)


class RedditMutation(graphene.ObjectType):
    publish_reddit_posts = PublishPosts.Field()
    publish_reddit_post = PublishPost.Field()
    reject_reddit_posts = RejectPosts.Field()
    toggle_reddit_state = ToggleRedditState.Field()
