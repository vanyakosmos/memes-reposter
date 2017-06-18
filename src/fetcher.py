import requests

from autoposter import AbstractFetcher, Response

from settings import CLIENT_ID


class GalleryFetcher(AbstractFetcher):
    def fetch(self):
        section = 'hot'  # hot | top | user
        sort = 'viral'  # viral | top | time | rising (only available with user section)
        show_viral = 'true'
        show_mature = 'true'
        album_previews = 'false'

        url = f'https://api.imgur.com/3/gallery/{section}/{sort}'
        querystring = {"showViral": f"{show_viral}", "mature": f"{show_mature}", "album_previews": f"{album_previews}"}
        headers = {'authorization': f'Client-ID {CLIENT_ID}'}
        response = requests.request("GET", url, headers=headers, params=querystring)
        response_json = response.json()

        self.log_status(response.status_code)
        return Response(success=response_json['success'],
                        data=response_json.get('data', None))


class AlbumFetcher(AbstractFetcher):
    def __init__(self, post_id):
        super().__init__()
        self.post_id = post_id

    def fetch(self):
        url = f'https://api.imgur.com/3/album/{self.post_id}/images'
        headers = {'authorization': f'Client-ID {CLIENT_ID}'}
        response = requests.request("GET", url, headers=headers)
        response_json = response.json()

        self.log_status(response.status_code)
        return Response(success=response_json['success'],
                        data=response_json.get('data', None))


class SubredditFetcher(AbstractFetcher):
    def __init__(self, subreddit):
        super().__init__()
        self.subreddit = subreddit

    def fetch(self):
        sort = 'top'  # time | top
        window = 'day'  # day | week | month | year | all

        url = f"https://api.imgur.com/3/gallery/r/{self.subreddit}/{sort}/{window}"
        headers = {'authorization': f"Client-ID {CLIENT_ID}"}
        response = requests.request("GET", url, headers=headers)
        response_json = response.json()

        self.log_status(response.status_code)
        return Response(success=response_json['success'],
                        data=response_json.get('data', None))
