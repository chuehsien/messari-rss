from utils import makeFeedId
from pydantic import BaseModel
from typing import Union

class RSSFeed(BaseModel):

    url: str
    id: Union[str, None] = None
    lastBuildTimestamp: Union[int, None] = None
    lastQueriedTimestamp: Union[int, None] = None
    lastResult: Union[str, None] = None # list of article ids
    pattern: Union[str, None] = None

    forceRefresh: bool = False

    def __init__(self, url=None, id=None, lastBuildTimestamp=None,lastQueriedTimestamp=None,lastResult=None,pattern=None,forceRefresh=False):
        super().__init__(url=url,
            id=id,
            lastBuildTimestamp=lastBuildTimestamp,
            lastQueriedTimestamp=lastQueriedTimestamp,
            lastResult=lastResult,
            pattern=pattern,
            forceRefresh=forceRefresh
        )
        if (self.id is None):
            self.id = makeFeedId(url,pattern)
        # self.print_info()

    # def print_info(self):
    #     print(f"RSS: {self.url} lastBuild: {self.lastBuildTimestamp} last Queried: {self.lastQueriedTimestamp}")
