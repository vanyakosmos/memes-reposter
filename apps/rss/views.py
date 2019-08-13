from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from . import tasks
from .fetcher import fetch_posts
from .models import Channel, Post, RssFeed
from .publisher import post_exists


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
    tasks.fetch_and_publish()
    next_url = request.query_params.get('next', None)
    if next_url:
        return redirect(next_url)
    return Response()


@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_blank_view(request: Request):
    stats = {}
    for feed in RssFeed.objects.filter(active=True):
        posts = fetch_posts(feed.link, feed.link_field)
        for post in posts:
            post.feed = feed
        posts = [
            p for p in posts
            if not post_exists(feed.channel, p)
        ]
        Post.objects.bulk_create(posts)
        key, length = str(feed), len(posts)
        stats[key] = length
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
