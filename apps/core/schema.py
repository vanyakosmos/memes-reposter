from functools import wraps

import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from graphql_jwt.exceptions import PermissionDenied


User = get_user_model()


def is_authenticated(info: ResolveInfo):
    user = info.context.user
    return user.is_authenticated


def is_staff(info: ResolveInfo):
    user = info.context.user
    return user.is_staff


def is_admin(info: ResolveInfo):
    user = info.context.user
    return user.is_superuser


def permissions(*ps):
    def wrapper(resolver):
        @wraps(resolver)
        def decorator(obj, info, *args, **kwargs):
            for permission in ps:
                if len(permission.__code__.co_varnames) > 1:
                    passed = permission(info, *args, **kwargs)
                else:
                    passed = permission(info)
                if not passed:
                    raise PermissionDenied()
                return resolver(obj, info, *args, **kwargs)

        return decorator

    return wrapper


class UserType(DjangoObjectType):
    class Meta:
        model = User


class CoreQuery(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(UserType)

    @permissions(is_staff)
    def resolve_me(self, info):
        return info.context.user

    @permissions(is_staff)
    def resolve_users(self, info):
        return User.objects.all()


class CoreMutations(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
