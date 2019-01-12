import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


UserModel = get_user_model()


class User(DjangoObjectType):
    class Meta:
        model = UserModel


class CoreQuery(graphene.ObjectType):
    users = graphene.List(User)

    def resolve_users(self, info):
        return UserModel.objects.all()
