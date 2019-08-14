import pytest
from django.urls import reverse

from reddit.models import Post


# noinspection PyUnresolvedReferences
class LoginMixin:
    def login(self):
        user = self.create_user(super=True)
        self.client.force_login(user)


@pytest.mark.usefixtures('create_user')
@pytest.mark.django_db
class TestPostsListView(LoginMixin):
    def test_auth(self):
        url = reverse('api:reddit:list')
        res = self.client.get(url)
        assert res.status_code == 401
        user = self.create_user()
        self.client.force_login(user)
        res = self.client.get(url)
        assert res.status_code == 403

    def test_get(self):
        self.login()
        url = reverse('api:reddit:list')
        res = self.client.get(url)
        assert res.json()['results'] == []


@pytest.mark.usefixtures('create_user', 'create_reddit_post')
@pytest.mark.django_db
class TestPostView(LoginMixin):
    def test_auth(self):
        url = reverse('api:reddit:update', args=(1,))
        res = self.client.post(url)
        assert res.status_code == 401
        user = self.create_user()
        self.client.force_login(user)
        res = self.client.post(url)
        assert res.status_code == 403

    def test_publish(self, mocker):
        mocker.patch('reddit.tasks.publish_post_task')
        self.login()
        p1 = self.create_reddit_post(status=Post.PENDING)
        url = reverse('api:reddit:update', args=(p1.id,))
        res = self.client.post(url)
        assert res.status_code == 201
        p1.refresh_from_db()
        assert p1.status == Post.ALMOST

    def test_publish_change_title(self, mocker):
        mocker.patch('reddit.tasks.publish_post_task')
        self.login()
        p1 = self.create_reddit_post(status=Post.PENDING)
        url = reverse('api:reddit:update', args=(p1.id,))
        res = self.client.post(url, data={'title': 'foo'})
        assert res.status_code == 201
        p1.refresh_from_db()
        assert p1.status == Post.ALMOST
        assert p1.title == 'foo'


@pytest.mark.usefixtures('create_user', 'create_reddit_post')
@pytest.mark.django_db
class TestRejectView(LoginMixin):
    def test_auth(self):
        url = reverse('api:reddit:reject')
        res = self.client.post(url)
        assert res.status_code == 401
        user = self.create_user()
        self.client.force_login(user)
        res = self.client.post(url)
        assert res.status_code == 403

    def test_reject(self):
        self.login()
        url = reverse('api:reddit:reject')
        p1 = self.create_reddit_post(status=Post.PENDING)
        p2 = self.create_reddit_post(status=Post.PENDING)
        p3 = self.create_reddit_post(status=Post.PENDING)
        res = self.client.post(url, data={'posts': [p1.id, p2.id]})
        assert res.status_code == 200
        assert res.json()['rejected'] == 2
        p1.refresh_from_db()
        assert p1.status == Post.REJECTED
        p2.refresh_from_db()
        assert p2.status == Post.REJECTED
        p3.refresh_from_db()
        assert p3.status == Post.PENDING


@pytest.mark.usefixtures('create_user', 'create_reddit_post')
@pytest.mark.django_db
class TestPendingSubredditsView(LoginMixin):
    def test_auth(self):
        url = reverse('api:reddit:pending_subs')
        res = self.client.get(url)
        assert res.status_code == 401
        user = self.create_user()
        self.client.force_login(user)
        res = self.client.get(url)
        assert res.status_code == 403

    def test_get(self):
        self.login()
        url = reverse('api:reddit:pending_subs')
        self.create_reddit_post(status=Post.PENDING)
        self.create_reddit_post(status=Post.PENDING)
        res = self.client.get(url)
        assert len(res.json()['subreddits']) == 2
