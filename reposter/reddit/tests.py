import pytest

from reddit.filters import inner_unique_filter

from .models import Subreddit, Post


class TestSubredditModel:
    pass


@pytest.mark.django_db
class TestFilters:
    def test_inner_unique_filter(self):
        sub = Subreddit(name='sub')
        posts = [
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='a'),
        ]
        new_posts = inner_unique_filter(posts, sub)
        assert len(new_posts) == 1
        assert new_posts[0] == posts[0]

        posts = [
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='b'),
            Post(subreddit=sub, url='c'),
        ]
        new_posts = inner_unique_filter(posts, sub)
        assert len(new_posts) == 3

        posts = [
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='b', photo_url='a'),
            Post(subreddit=sub, url='c', video_url='b'),
        ]
        new_posts = inner_unique_filter(posts, sub)
        assert len(new_posts) == 1
        assert new_posts[0] == posts[0]
