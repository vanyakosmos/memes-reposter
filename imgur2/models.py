from .fetchers import AlbumFetcher


class Post(object):
    def __init__(self, json, images_per_post=10, images_per_long_post=5):
        self.id = json.get('id')
        self.title = json.get('title', None) or ''
        self.desc = json.get('description', None) or ''
        self.score = int(json.get('score'))
        self.datetime = json.get('datetime')
        self.is_album = json.get('is_album')
        self.url = self.get_url(json)
        self.tags = [tag["name"] for tag in json['tags']]
        self.size = json.get('images_count', 1)
        self.is_long = self.size > images_per_post
        self.images = self.get_images(json, images_per_long_post)

    def get_images(self, json, images_per_long_post):
        album_fetcher = AlbumFetcher()
        if self.is_album:
            row_images = album_fetcher.fetch(self.id)
            if self.is_long:
                row_images = row_images[:images_per_long_post]
            return [Image(item) for item in row_images]
        else:
            return [Image(json)]

    def get_url(self, json):
        if self.is_album:
            return json.get('link')
        else:
            return 'https://imgur.com/' + self.id

    def __str__(self):
        return f'Post(id="{self.id}", is_long={self.is_long}, url="{self.url}")'

    def __repr__(self):
        return (f'Post(\n'
                f'   id="{self.id}", \n'
                f'   is_long={self.is_long}, \n'
                f'   title="{self.title}", \n'
                f'   url="{self.url}")')


class Image(object):
    def __init__(self, json):
        self.animated = json.get('animated')
        self.title = json.get('title') or ''
        self.desc = json.get('description') or ''
        self.size = json.get('size')
        self.width = json.get('width')
        self.height = json.get('height')
        if self.animated:
            self.url = json.get('mp4', None) or json.get('link')
        else:
            self.url = json.get('link')

    def __str__(self):
        return (f'Image(\n'
                f'   desc="{self.desc}", \n'
                f'   url="{self.url}")')

    def __repr__(self):
        return str(self)
