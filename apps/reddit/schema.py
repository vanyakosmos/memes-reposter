import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import ResolveInfo

from . import tasks
from .models import Post


class PostObject(DjangoObjectType):
    class Meta:
        model = Post
        filter_fields = (
            'status',
            'subreddit__on_moderation',
            'subreddit__subscriptions__name',
        )
        interfaces = (relay.Node,)


class RedditQuery(graphene.ObjectType):
    reddit_post = relay.Node.Field(PostObject)
    all_reddit_posts = DjangoFilterConnectionField(PostObject)


class PublishPosts(graphene.Mutation):
    skip = graphene.Boolean()

    class Arguments:
        idle = graphene.Boolean(default_value=False)

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

    def mutate(self, info: ResolveInfo, posts):
        post_ids = [
            relay.Node.from_global_id(p)[1]
            for p in posts
        ]
        posts = Post.objects.filter(pk__in=post_ids)
        rows = posts.update(status=Post.STATUS_REJECTED)
        return RejectPosts(count=rows)


class RedditMutation(graphene.ObjectType):
    publish_posts = PublishPosts.Field()
    publish_post = PublishPost.Field()
    reject_posts = RejectPosts.Field()
