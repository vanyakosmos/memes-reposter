import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from apps.core.permissions import is_staff, permissions
from .models import TelegramChannel


class TelegramChannelNode(DjangoObjectType):
    class Meta:
        model = TelegramChannel
        interfaces = (relay.Node,)

    @classmethod
    @permissions(is_staff)
    def get_node(cls, info, id):
        return super().get_node(info, id)


class TelegramQuery(graphene.ObjectType):
    telegram_channel = relay.Node.Field(TelegramChannelNode)
    all_telegram_channels = graphene.List(TelegramChannelNode)

    @permissions(is_staff)
    def resolve_all_telegram_channels(self, info: ResolveInfo, **kwargs):
        return TelegramChannel.objects.all()
