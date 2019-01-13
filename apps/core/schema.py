import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import ResolveInfo

from .models import SiteConfig, Subscription
from .permissions import is_staff, permissions


User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User


class SubscriptionNode(DjangoObjectType):
    class Meta:
        model = Subscription
        filter_fields = ('name', 'type')
        interfaces = (relay.Node,)


class CoreQuery(graphene.ObjectType):
    status = graphene.String()
    site_enabled = graphene.Boolean()
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    all_subscriptions = DjangoFilterConnectionField(SubscriptionNode)

    @permissions(is_staff)
    def resolve_status(self, info):
        """
        todo: system status report
        - objects number
        - redis open connections
        - last error messages
        """
        return ""

    @permissions(is_staff)
    def resolve_site_enabled(self, info):
        return SiteConfig.get_solo().enabled

    @permissions(is_staff)
    def resolve_me(self, info):
        return info.context.user

    @permissions(is_staff)
    def resolve_users(self, info):
        return User.objects.all()

    @permissions(is_staff)
    def resolve_all_subscriptions(self, info: ResolveInfo, **kwargs):
        return Subscription.objects.all().order_by('type', 'name')


class ToggleSiteState(graphene.Mutation):
    enabled = graphene.Boolean()

    class Arguments:
        pass

    @permissions(is_staff)
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
