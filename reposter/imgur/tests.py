import pytest
from django.test import override_settings

from core.models import Subscription
from core.publisher import publish_into_telegram
from telegram_app.models import Chat, Message
from .models import ImgurConfig, Post
from .tasks import fetch_and_publish, publish_imgur_posts


@pytest.mark.usefixtures('mock_bot')
@pytest.mark.django_db
class TestTasks:
    def test_fetch_and_publish_blank(self, mocker):
        mocker.patch.object(publish_imgur_posts, 'delay', publish_imgur_posts)
        ImgurConfig.objects.create(score_limit=0)
        with override_settings(IMGUR_FETCH_LIMIT=2):
            fetch_and_publish(blank=True)
        assert Post.objects.count() == 2

    def test_fetch_and_publish(self, mocker):
        mocker.patch.object(publish_into_telegram, 'delay', publish_into_telegram)
        mocker.patch.object(publish_imgur_posts, 'delay', publish_imgur_posts)
        mocker.patch.object(Chat, 'update_from_telegram')

        sub = Subscription.objects.create(name='pics')
        conf = ImgurConfig.objects.create(score_limit=0)
        sub.imgur_configs.add(conf)
        chat1 = Chat.objects.create(telegram_id='1111', username='username1', type='private')
        chat2 = Chat.objects.create(telegram_id='2222', username='username2', type='private')
        sub.telegram_chats.add(chat1, chat2)

        with override_settings(IMGUR_FETCH_LIMIT=2):
            fetch_and_publish(blank=False)
        assert Post.objects.count() == 2
        assert Message.objects.count() == 4
        assert Message.objects.filter(chat=chat1).count() == 2
        assert Message.objects.filter(chat=chat2).count() == 2
