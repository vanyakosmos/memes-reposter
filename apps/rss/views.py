import re

from coreapi import Link
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect, render
from rest_framework import schemas
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.schemas.generators import LinkNode, distribute_links

from . import tasks
from .models import Channel


VERB_MAP = {
    'read': 'GET',
    'list': 'GET_LIST',
    'create': 'POST',
    'update': 'PUT',
    'partial_update': 'PATCH',
    'delete': 'DELETE',
}
API_TITLE = 'Sanegnize API'
URL_REGEX = re.compile(r'{\w+?}')


def traverse(request, node, root_key):
    res = {}
    if isinstance(node, Link):
        root_key = VERB_MAP.get(root_key, root_key)
        url = URL_REGEX.sub('1', node.url)
        return root_key, request.build_absolute_uri(url)
    elif isinstance(node, LinkNode):
        for key, n in node.items():
            key, r = traverse(request, n, key)
            res[key] = r
    return root_key, res


@api_view()
@permission_classes([IsAdminUser])
def root_view(request: Request):
    gen = schemas.SchemaGenerator()
    gen.get_schema()
    root = gen.get_links(request)
    distribute_links(root)
    key, res = traverse(request, root, root_key='api')
    return Response(res)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def refresh_view(request: Request):
    stats = tasks.refresh_channels_meta()

    next_url = request.query_params.get('next', None)
    if next_url:
        return redirect(next_url)
    return Response({
        'refreshed': stats,
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_view(request: Request):
    stats = tasks.fetch_and_publish()

    next_url = request.query_params.get('next', None)
    if next_url:
        return redirect(next_url)
    return Response({
        'published': stats,
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def delete_old_posts_view(request: Request):
    deleted = tasks.delete_old_posts_db()

    next_url = request.query_params.get('next', None)
    if next_url:
        return redirect(next_url)
    return Response({
        'deleted': deleted,
    })


def index_view(request: Request):
    channels = Channel.objects.filter(rssfeed__active=True).distinct()
    return render(request, 'rss/index.html', {
        'channels': channels,
        'DEBUG': settings.DEBUG,
    })


@api_view()
def channels_view(request: Request):
    channels = Channel.objects.filter(rssfeed__active=True)
    search = request.query_params.get('search', None)
    if search:
        channels = channels.filter(Q(title__icontains=search) |
                                   Q(username__icontains=search) |
                                   Q(rssfeed__title__icontains=search))
    channels = channels.distinct()
    return Response([
        {
            'username': c.username,
            'name': str(c),
            'tg_link': c.tg_link,
            'feeds': [
                {
                    'title': f.title,
                    'link': f.link,
                }
                for f in c.rssfeed_set.all()
            ]
        }
        for c in channels
    ])
