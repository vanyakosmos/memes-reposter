from typing import NamedTuple, Optional


class Post(NamedTuple):
    title: str
    url: Optional[str]
    photo_url: Optional[str]
    video_url: Optional[str]
    text: Optional[str]
    comments: Optional[str]  # url
    file_path: Optional[str]
