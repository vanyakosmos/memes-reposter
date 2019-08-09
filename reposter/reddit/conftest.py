import pytest
from _pytest.fixtures import FixtureRequest

from .models import Post


def append_to_cls(request: FixtureRequest, func, name=None):
    name = name or func.__name__.strip('_')
    if request.cls:
        setattr(request.cls, name, staticmethod(func))
    return func


@pytest.fixture(scope='class')
def create_post(request: FixtureRequest):
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

    return append_to_cls(request, _factory, 'create_post')
