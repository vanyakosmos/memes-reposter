from functools import wraps

import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphql import ResolveInfo
from graphql_jwt.exceptions import PermissionDenied

from apps.core.models import SiteConfig


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
    status = graphene.String()
    site_enabled = graphene.Boolean()
    me = graphene.Field(UserType)
    users = graphene.List(UserType)

    def resolve_status(self, info):
        """
        todo: system status report
        - objects number
        - redis open connections
        - last error messages
        """
        return ""

    def resolve_site_enabled(self, info):
        return SiteConfig.get_solo().enabled

    @permissions(is_staff)
    def resolve_me(self, info):
        return info.context.user

    @permissions(is_staff)
    def resolve_users(self, info):
        return User.objects.all()


class ToggleSiteState(graphene.Mutation):
    enabled = graphene.Boolean()

    class Arguments:
        pass

    def mutate(self, info: ResolveInfo, **input):
        config = SiteConfig.get_solo()
        config.enabled = not config.enabled
        config.save()
        return ToggleSiteState(enabled=config.enabled)


class CoreMutations(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    toggle_site_state = ToggleSiteState.Field()
