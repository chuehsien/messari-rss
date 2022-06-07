from utils import shorten_body, makeId, getTimestampFromRaw, getTitleFromRaw, getDescFromRaw, getLinkFromRaw
from pydantic import BaseModel
from typing import Union

class RSSArticle(BaseModel):

    # raw:None = None
    id: Union[str, None] = None
    feed_id: Union[str, None] = None
    timestamp: Union[int, None] = None
    title: Union[str, None] = None
    description: Union[str, None] = None
    link: Union[str, None] = None


    def __init__(self, id=None, feed_id=None, timestamp=None, title=None, description=None, link=None):
        super().__init__(id=id,feed_id=feed_id,timestamp=timestamp,title=title,description=description,link=link)
        self.fill_id()

    def fill_id(self):
        self.id = makeId(self.feed_id, self.title)

    # def parse_raw(self, raw):
    #     if (raw is not None):
    #         self.timestamp = getTimestampFromRaw(raw)
    #         self.title = getTitleFromRaw(raw)
    #         self.description = getDescFromRaw(raw)
    #         self.link = getLinkFromRaw(raw)

    def print_info(self):
        print(f"{self.title}\n{shorten_body(self.description)}\n{self.link}")
