from typing import NamedTuple, Optional, List


class Media(NamedTuple):
    url: str
    video: bool = False
    file_path: Optional[str] = None
    caption: Optional[str] = None


class Post(NamedTuple):
    id: str
    url: str
    comments: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    keywords: Optional[List[str]] = []
    medias: List[Media] = []


def restore_from_raw(raw_post: tuple):
    *raw_post, raw_medias = raw_post
    return Post(*raw_post, medias=[Media(*values) for values in raw_medias])
