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

    methods = ['send_message', 'send_video', 'send_photo']
    for method in methods:
        mocker.patch.object(Bot, method, send)


@pytest.fixture(scope='class')
def create_reddit_post(request: FixtureRequest):
    from reddit.models import Post

    def _factory(
        subreddit,
        id=None,
        subreddit_name=None,
        title=None,
        score=None,
        reddit_id=None,
        url=None,
        status=None,
        **kwargs
    ):
        return Post.objects.create(
            subreddit=subreddit,
            subreddit_name=subreddit_name or subreddit.name,
            title=title or id or 'title',
            score=score or 0,
            reddit_id=reddit_id or id or '1',
            url=url or id or 'https://example.com/foo.png',
            status=status or Post.ACCEPTED,
            **kwargs,
        )

    return append_to_cls(request, _factory, 'create_reddit_post')
