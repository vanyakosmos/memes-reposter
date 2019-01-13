from django.test import TestCase

from apps.core.models import Subscription
from apps.reddit.models import Post, Subreddit
from apps.tgapp.models import TelegramChannel
from apps.tgapp.publishers.reddit import check_post


class RedditPublisherTests(TestCase):
    def setUp(self):
        sub1 = Subscription.objects.create(type=Subscription.REDDIT, name='foo')
        sub2 = Subscription.objects.create(type=Subscription.REDDIT, name='bar')

        self.sr1 = Subreddit.objects.create(name='red1')
        self.sr2 = Subreddit.objects.create(name='red2')

        self.sr1.subscriptions.add(sub1)
        self.sr1.subscriptions.add(sub2)
        self.sr2.subscriptions.add(sub1)

        self.tg1 = TelegramChannel(username='tg1')
        self.tg1.save(update_meta=False)
        self.tg1.subscriptions.add(sub1)

        self.tg2 = TelegramChannel(username='tg2')
        self.tg2.save(update_meta=False)
        self.tg2.subscriptions.add(sub1)

        Post.objects.create(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='1',
            title='title 1',
            url='https://im.com/1.png',
            source_url='https://im.com/1.png',
            status=Post.STATUS_ACCEPTED,
            channel_uuid=self.tg1.uuid,
        )
        Post.objects.create(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='2',
            title='title 2',
            url='https://im.com/2.png',
            source_url='https://im.com/2.png',
            status=Post.STATUS_PENDING,
            channel_uuid=self.tg1.uuid,
        )

    def test_similar_post(self):
        # same reddit_id and url
        post = Post(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='1',
            title='title 1',
            url='https://im.com/1.png',
            source_url='https://im.com/1.png',
            channel_uuid=self.tg1.uuid,
        )
        self.assertFalse(check_post(post, self.tg1, False))

        # same url
        post = Post(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='2',
            title='title 2',
            url='https://im.com/1.png',
            source_url='https://im.com/1.png',
            channel_uuid=self.tg1.uuid,
        )
        self.assertFalse(check_post(post, self.tg1, False))

        # different post
        post = Post(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='3',
            title='title 3',
            url='https://im.com/3.png',
            source_url='https://im.com/3.png',
            channel_uuid=self.tg1.uuid,
        )
        self.assertTrue(check_post(post, self.tg1, False))

    def test_same_post_as_old_pending(self):
        # same reddit_id as old pending post
        post = Post(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='2',
            title='title 2',
            url='https://im.com/3.png',
            source_url='https://im.com/3.png',
            status=Post.STATUS_ACCEPTED,
            channel_uuid=self.tg1.uuid,
        )
        self.assertTrue(check_post(post, self.tg1, False))

    def test_new_not_ready_post(self):
        post = Post(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='3',
            title='title 3',
            url='https://im.com/3.png',
            source_url='https://im.com/3.png',
            status=Post.STATUS_PENDING,
            channel_uuid=self.tg1.uuid,
        )
        self.assertFalse(check_post(post, self.tg1, False))

    def test_idle(self):
        post = Post(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='3',
            title='title 3',
            url='https://im.com/3.png',
            source_url='https://im.com/3.png',
            status=Post.STATUS_ACCEPTED,
            channel_uuid=self.tg1.uuid,
        )
        self.assertFalse(check_post(post, self.tg1, True))

    def test_post_into_another_channel(self):
        post = Post(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='1',
            title='title 1',
            url='https://im.com/1.png',
            source_url='https://im.com/1.png',
            status=Post.STATUS_ACCEPTED,
            channel_uuid=self.tg2.uuid,
        )
        post.clone()
        self.assertTrue(check_post(post, self.tg2, False))

    def test_cloned_post(self):
        post = Post(
            subreddit=self.sr1,
            subreddit_name='red1',
            reddit_id='3',
            title='title 3',
            url='https://im.com/3.png',
            source_url='https://im.com/3.png',
            status=Post.STATUS_ACCEPTED,
            channel_uuid=self.tg1.uuid,
        )
        self.assertTrue(check_post(post, self.tg1, False))

        post = post.clone(exclude=['id'])
        post.channel_uuid = self.tg2.uuid
        self.assertTrue(check_post(post, self.tg2, False))

        post = post.clone(exclude=['id'])
        post.channel_uuid = self.tg1.uuid
        self.assertFalse(check_post(post, self.tg2, False))
