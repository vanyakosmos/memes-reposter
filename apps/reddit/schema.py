import graphene
from graphene_django import DjangoObjectType

from .models import Post


class PostObject(DjangoObjectType):
    class Meta:
        model = Post


class RedditQuery(graphene.ObjectType):
    post = PostObject(id=graphene.Int(required=True))
    posts = graphene.List(PostObject)

    def resolve_post(self, info, id):
        print(info)
        return Post.objects.get(id=id)

    def resolve_posts(self, info):
        print(info)
        return Post.objects.all()
