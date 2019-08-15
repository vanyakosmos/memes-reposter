import pytest
from django.test import override_settings

from core.publisher import publish_into_telegram
from reddit.tasks import fetch_and_publish, publish_sub

from . import filters
from .models import Subreddit, Post
from core.models import Subscription
from telegram_app.models import Chat, Message


@pytest.mark.usefixtures('create_reddit_post')
@pytest.mark.django_db
class TestModels:
    def test_get_posts(self):
        sub = Subreddit(name='pics')
        raw_posts = sub.get_posts(limit=2)
        posts = [Post.from_dict(p, sub) for p in raw_posts]
        assert len(raw_posts) == 2
        assert posts[0].subreddit_name == 'pics'

    def test_pending_subs_no_posts(self):
        subs = Post.objects.pending_subs()
        assert list(subs) == []

    def test_pending_subs_no_pending(self):
        sub1 = Subreddit.objects.create(name='sub1')
        self.create_reddit_post(subreddit=sub1)
        self.create_reddit_post(subreddit=sub1)
        subs = Post.objects.pending_subs()
        assert list(subs) == []

    def test_pending_subs(self):
        sub2 = Subreddit.objects.create(name='sub2')
        self.create_reddit_post(subreddit=sub2, status=Post.PENDING)
        self.create_reddit_post(subreddit=sub2, status=Post.PENDING)
        self.create_reddit_post(subreddit=sub2)
        sub3 = Subreddit.objects.create(name='sub3')
        self.create_reddit_post(subreddit=sub3, status=Post.PENDING)
        subs = Post.objects.pending_subs()
        assert list(subs) == ['sub2', 'sub3']


@pytest.mark.usefixtures('create_reddit_post')
@pytest.mark.django_db
class TestFilters:
    def test_score_filter(self):
        sub = Subreddit.objects.create(name='sub', score_limit=100, score_limit_repost=200)
        posts = [
            Post(subreddit=sub, url='a', score=50),
            Post(subreddit=sub, url='b', score=150),
            Post(subreddit=sub, url='c', score=250),
        ]
        ps = filters.score_filter(posts)
        assert len(ps) == 2
        assert ps[0].status == Post.PENDING
        assert ps[1].status == Post.ACCEPTED

        sub = Subreddit.objects.create(name='sub', score_limit=100, score_limit_repost=100)
        posts = [
            Post(subreddit=sub, url='a', score=50),
            Post(subreddit=sub, url='b', score=150),
            Post(subreddit=sub, url='c', score=250),
        ]
        ps = filters.score_filter(posts)
        assert len(ps) == 2
        assert ps[0].status == Post.ACCEPTED
        assert ps[1].status == Post.ACCEPTED

    def test_nsfw_filter(self):
        sub = Subreddit.objects.create(name='sub')
        posts = [
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='b', nsfw=True),
            Post(subreddit=sub, url='c'),
        ]
        ps = filters.nsfw_filter(posts)
        assert len(ps) == 2
        assert ps[0].url == 'a' and ps[1].url == 'c'

    def test_inner_unique_filter(self):
        sub = Subreddit.objects.create(name='sub')
        posts = [
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='a'),
        ]
        new_posts = filters.inner_unique_filter(posts)
        assert len(new_posts) == 1
        assert new_posts[0] == posts[0]

        posts = [
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='b'),
            Post(subreddit=sub, url='c'),
        ]
        new_posts = filters.inner_unique_filter(posts)
        assert len(new_posts) == 3

        posts = [
            Post(subreddit=sub, url='a'),
            Post(subreddit=sub, url='a', type=Post.PHOTO),
            Post(subreddit=sub, url='a', type=Post.VIDEO),
        ]
        new_posts = filters.inner_unique_filter(posts)
        assert len(new_posts) == 1
        assert new_posts[0] == posts[0]

    def test_unique_filter(self):
        sub = Subreddit.objects.create(name='sub')
        self.create_reddit_post(subreddit=sub, id='a', status=Post.ACCEPTED)
        p2 = self.create_reddit_post(subreddit=sub, id='b', status=Post.PENDING)
        self.create_reddit_post(subreddit=sub, id='c', status=Post.REJECTED)
        posts = [
            Post(subreddit=sub, reddit_id='a'),
            Post(subreddit=sub, reddit_id='b', status=Post.ACCEPTED),
            Post(subreddit=sub, reddit_id='c'),
            Post(subreddit=sub, reddit_id='d'),
        ]
        ps = filters.unique_filter(posts)
        assert len(ps) == 2
        assert ps[0] == p2
        assert ps[1] == posts[3]

    def test_keywords_filter(self):
        sub = Subreddit.objects.create(name='sub', forbidden_keywords=['a', 'b', 'c'])
        posts = [
            Post(subreddit=sub, title='foo bar'),
            Post(subreddit=sub, title='foo a'),
            Post(subreddit=sub, title='foo b c'),
        ]
        ps = filters.keywords_filter(posts)
        assert len(ps) == 1
        assert ps[0] == posts[0]

    def test_apply_filters(self):
        pass


@pytest.mark.usefixtures('mock_bot')
@pytest.mark.django_db
class TestTasks:
    def test_fetch_and_publish_blank(self, mocker):
        mocker.patch.object(publish_sub, 'delay', publish_sub)
        Subreddit.objects.create(name='pics')
        with override_settings(REDDIT_POSTS_LIMIT=2):
            fetch_and_publish(blank=True)
        assert Post.objects.count() == 2
        assert Post.objects.filter(status=Post.REJECTED).count() == 2

    def test_fetch_and_publish(self, mocker):
        mocker.patch.object(publish_into_telegram, 'delay', publish_into_telegram)
        mocker.patch.object(publish_sub, 'delay', publish_sub)
        mocker.patch.object(Chat, 'update_from_telegram')

        subr = Subreddit.objects.create(name='pics', score_limit=0, score_limit_repost=0)
        chat1 = Chat.objects.create(telegram_id='1111', username='username1', type='private')
        chat2 = Chat.objects.create(telegram_id='2222', username='username2', type='private')
        sub = Subscription.objects.create(name='pics')
        sub.telegram_chats.add(chat1, chat2)
        sub.subreddits.add(subr)

        with override_settings(REDDIT_POSTS_LIMIT=2):
            fetch_and_publish(blank=False)
        assert Post.objects.count() == 2
        assert Post.objects.filter(status=Post.ACCEPTED).count() == 2
        assert Message.objects.count() == 4
        assert Message.objects.filter(chat=chat1).count() == 2
        assert Message.objects.filter(chat=chat2).count() == 2
