import pytest

from core.models import Subscription
from core.publisher import publish_into_telegram
from rss.fetcher import fetch_posts
from rss.models import Post, RssFeed
from telegram_app.models import Chat, Message
from .tasks import publish_feed, fetch_and_publish


@pytest.mark.django_db
class TestFetcher:
    def test_fetch_posts(self):
        feed = RssFeed.objects.create(link='https://www.theverge.com/rss/index.xml')
        ps = fetch_posts(feed)
        assert ps


@pytest.mark.usefixtures('mock_bot')
@pytest.mark.django_db
class TestTasks:
    def setup_feed(self, mocker):
        mocker.patch.object(publish_feed, 'delay', publish_feed)
        mocker.patch.object(Chat, 'update_from_telegram')

        feed = RssFeed.objects.create(link='https://example.com/feed.xml')
        mocker.patch(
            'rss.fetcher.fetch_posts',
            return_value=[
                Post(feed=feed, url='https://example.com/1', title="example 1"),
                Post(feed=feed, url='https://example.com/2', title="example 1"),
            ],
        )
        self.chat1 = Chat.objects.create(telegram_id='1111', username='username1', type='private')
        self.chat2 = Chat.objects.create(telegram_id='2222', username='username2', type='private')
        sub = Subscription.objects.create(name='pics')
        sub.telegram_chats.add(self.chat1, self.chat2)
        sub.rss_feeds.add(feed)

    def test_fetch_and_publish_blank(self, mocker):
        self.setup_feed(mocker)
        fetch_and_publish(blank=True)
        assert Post.objects.count() == 2
        assert Message.objects.count() == 0

    def test_fetch_and_publish(self, mocker):
        mocker.patch.object(publish_into_telegram, 'delay', publish_into_telegram)
        self.setup_feed(mocker)
        fetch_and_publish(blank=False)
        assert Post.objects.count() == 2
        assert Message.objects.count() == 4
        assert Message.objects.filter(chat=self.chat1).count() == 2
        assert Message.objects.filter(chat=self.chat2).count() == 2
