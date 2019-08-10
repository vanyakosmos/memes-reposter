from typing import NamedTuple, Optional, List, Union


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
    medias: List[Media] = []
    keywords: Optional[List[str]] = []
