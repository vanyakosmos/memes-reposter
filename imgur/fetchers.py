import requests

from core.fetcher import BaseFetcher
from settings import FETCH_LIMIT, IMGUR_CLIENT_ID


class GalleryFetcher(BaseFetcher):
    def fetch(self):
        section = 'hot'  # hot | top | user
        sort = 'viral'  # viral | top | time | rising (only available with user section)
        show_viral = 'true'
        show_mature = 'true'
        album_previews = 'false'

        url = f'https://api.imgur.com/3/gallery/{section}/{sort}'
        querystring = {"showViral": f"{show_viral}", "mature": f"{show_mature}", "album_previews": f"{album_previews}"}
        headers = {'authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        response = requests.request("GET", url, headers=headers, params=querystring)
        json = response.json()

        self.logger.debug(f'Fetched. Code: {response.status_code}')

        return json['data'][:FETCH_LIMIT]


class AlbumFetcher(BaseFetcher):
    def fetch(self, post_id):
        url = f'https://api.imgur.com/3/album/{post_id}/images'
        headers = {'authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        response = requests.request("GET", url, headers=headers)
        json = response.json()

        self.logger.debug(f'Fetched. Code: {response.status_code}')

        return json['data']
