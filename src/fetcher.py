import requests

from autoposter import AbstractFetcher, Response


class ImgurFetcher(AbstractFetcher):
    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id


class GalleryFetcher(ImgurFetcher):
    def fetch(self):
        section = 'hot'  # hot | top | user
        sort = 'viral'  # viral | top | time | rising (only available with user section)
        show_viral = 'true'
        show_mature = 'true'
        album_previews = 'false'

        url = f'https://api.imgur.com/3/gallery/{section}/{sort}'
        querystring = {"showViral": f"{show_viral}", "mature": f"{show_mature}", "album_previews": f"{album_previews}"}
        headers = {'authorization': f'Client-ID {self.client_id}'}
        response = requests.request("GET", url, headers=headers, params=querystring)
        response_json = response.json()

        self.log_status(response.status_code)
        return Response(success=response_json['success'],
                        data=response_json.get('data', None))


class AlbumFetcher(ImgurFetcher):
    def fetch(self, post_id):
        url = f'https://api.imgur.com/3/album/{post_id}/images'
        headers = {'authorization': f'Client-ID {self.client_id}'}
        response = requests.request("GET", url, headers=headers)
        response_json = response.json()

        self.log_status(response.status_code)
        return Response(success=response_json['success'],
                        data=response_json.get('data', None))


class SubredditFetcher(ImgurFetcher):
    def fetch(self):
        pass
