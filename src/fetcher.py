import requests

from autoposter import AbstractFetcher, Response

from settings import IMGUR_CLIENT_ID, REDDIT_NAME, FETCH_LIMIT


class GalleryFetcher(AbstractFetcher):
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
        response_json = response.json()

        self.log_status(response.status_code)
        return Response(success=response_json['success'],
                        data=response_json.get('data', None))


class AlbumFetcher(AbstractFetcher):
    def fetch(self, post_id):
        url = f'https://api.imgur.com/3/album/{post_id}/images'
        headers = {'authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        response = requests.request("GET", url, headers=headers)
        response_json = response.json()

        self.log_status(response.status_code)
        return Response(success=response_json['success'],
                        data=response_json.get('data', None))


class RedditFetcher(AbstractFetcher):
    def fetch(self, subreddit):
        url = f"https://reddit.com/r/{subreddit}/top/.json?limit={FETCH_LIMIT}"
        headers = {"User-Agent": f"ChangeMeClient/0.1 by {REDDIT_NAME}"}
        response = requests.request("GET", url, headers=headers)
        response_json = response.json()

        self.log_status(response.status_code)
        data = []
        if response.status_code == 200:
            data = response_json['data']['children']
        return Response(success=response.status_code == 200,
                        data=data)


if __name__ == '__main__':
    f = RedditFetcher()
    resp = f.fetch('funny')
    print(resp.data)
