from typing import NamedTuple, Optional, List


class Post(NamedTuple):
    id: str
    title: Optional[str]
    url: Optional[str]
    photo_url: Optional[str]
    video_url: Optional[str]
    text: Optional[str]
    comments: Optional[str]  # url
    file_path: Optional[str]
    tokens: Optional[List[str]]
