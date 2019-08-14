from uuid import uuid4

from django.contrib.auth.models import User
from time import time

import pytest
from _pytest.fixtures import FixtureRequest


def append_to_cls(request: FixtureRequest, func, name=None):
    name = name or func.__name__.strip('_')
    if request.cls:
        setattr(request.cls, name, staticmethod(func))
    return func


@pytest.fixture()
def mock_bot(mocker):
    from telegram import Bot, Message as TGMessage

    def send(*args, **kwargs):
        return TGMessage.de_json(
            {
                'message_id': '1111',
                'from': {
                    'id': '1111',
                    'first_name': 'user',
                    'is_bot': False,
                },
                'chat': {
                    'id': '1111',
                    'first_name': 'user',
                    'type': 'private',
                },
                'date': time(),
            },
            None,
        )

    methods = ['send_message', 'send_video', 'send_photo', 'send_media_group']
    for method in methods:
        mocker.patch.object(Bot, method, send)


@pytest.fixture(scope='class')
def create_subreddit(request: FixtureRequest):
    from reddit.models import Subreddit

    def _factory(name, **kwargs):
        return Subreddit.objects.create(name=name or str(uuid4()), **kwargs)

    return append_to_cls(request, _factory, 'create_subreddit')


@pytest.fixture(scope='class')
def create_reddit_post(request: FixtureRequest, create_subreddit):
    from reddit.models import Post

    def _factory(
        subreddit=None,
        id=None,
        subreddit_name=None,
        title=None,
        score=None,
        reddit_id=None,
        url=None,
        status=None,
        **kwargs
    ):
        subreddit = subreddit or create_subreddit(name=subreddit_name)
        return Post.objects.create(
            subreddit=subreddit,
            subreddit_name=subreddit_name or subreddit.name,
            title=title or id or 'title',
            score=score or 0,
            reddit_id=reddit_id or id or str(uuid4()),
            url=url or id or 'https://example.com/foo.png',
            status=status or Post.ACCEPTED,
            **kwargs,
        )

    return append_to_cls(request, _factory, 'create_reddit_post')


@pytest.fixture(scope='class')
def create_user(request: FixtureRequest):
    def _factory(super=False, username=None, email=None, password=None, **kwargs):
        create = User.objects.create_superuser if super else User.objects.create_user
        return create(
            username=username or str(uuid4()),
            email=email,
            password=password or 'pass',
            **kwargs,
        )

    return append_to_cls(request, _factory, 'create_user')


@pytest.fixture(autouse=True)
def attached_client(request: FixtureRequest, client):
    setattr(request.cls, 'client', client)
