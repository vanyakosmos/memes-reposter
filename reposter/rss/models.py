import feedparser
from django.core.exceptions import ValidationError
from django.db import models

from core.fields import URLField
from core.post import Post as NormalPost


class RssFeed(models.Model):
    link = models.URLField()
    title = models.CharField(max_length=300, blank=True, null=True)
    link_field = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        name = self.title or self.link
        return name

    def clean(self):
        feed = feedparser.parse(self.link)
        if feed['bozo'] != 0:
            raise ValidationError("Not valid rss link.")


class Post(models.Model):
    feed = models.ForeignKey(RssFeed, on_delete=models.CASCADE, related_name='posts')
    title = models.TextField()
    url = URLField()
    photo_url = URLField(null=True, blank=True)
    comments = URLField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def __repr__(self):
        fields = ['feed', 'title', 'url', 'photo_url']
        pairs = [f'{f}={repr(getattr(self, f))}' for f in fields]
        concat = ', '.join(pairs)
        return f'Post({concat})'

    class Meta:
        unique_together = ('feed', 'url')

    def normalize(self):
        return NormalPost(
            id=f"rss:{self.url}",
            title=self.title,
            url=self.url,
            photo_url=self.photo_url,
            video_url=None,
            text=None,
            comments=self.comments,
            file_path=None,
            tokens=self.title.split(),
        )
