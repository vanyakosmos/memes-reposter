import graphene

from apps.core.schema import CoreQuery
from apps.reddit.schema import RedditQuery


class Query(RedditQuery, CoreQuery, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    pass


# noinspection PyTypeChecker
schema = graphene.Schema(query=Query)
