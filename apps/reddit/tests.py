from pprint import pprint
from unittest import TestCase

from apps.reddit.fetcher import fetch


class FetcherTests(TestCase):
    def test_fetch(self, ):
        posts = fetch('gifs', limit=3)
        pprint(posts)
